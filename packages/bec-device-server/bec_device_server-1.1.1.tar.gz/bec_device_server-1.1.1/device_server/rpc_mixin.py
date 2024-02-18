import traceback
from contextlib import redirect_stdout
from io import StringIO
from typing import Any

import ophyd
from bec_lib import Alarms, MessageEndpoints, bec_logger, messages

from device_server.devices import is_serializable, rgetattr

logger = bec_logger.logger


class RPCMixin:
    """Mixin for handling RPC calls"""

    def run_rpc(self, instr: messages.DeviceInstructionMessage) -> None:
        """
        Run RPC call and send result to client. RPC calls also capture stdout and
        stderr and send it to the client.

        Args:
            instr: DeviceInstructionMessage

        """
        result = StringIO()
        with redirect_stdout(result):
            try:
                instr_params = instr.content.get("parameter")
                device = instr.content["device"]
                self._assert_device_is_enabled(instr)
                res = self._process_rpc_instruction(instr)
                # send result to client
                self._send_rpc_result_to_client(device, instr_params, res, result)
                logger.trace(res)
            except Exception as exc:  # pylint: disable=broad-except
                # send error to client
                self._send_rpc_exception(exc, instr)

    def _get_result_from_rpc(self, rpc_var: Any, instr_params: dict) -> Any:
        if callable(rpc_var):
            args = tuple(instr_params.get("args", ()))
            kwargs = instr_params.get("kwargs", {})
            if args and kwargs:
                res = rpc_var(*args, **kwargs)
            elif args:
                res = rpc_var(*args)
            elif kwargs:
                res = rpc_var(**kwargs)
            else:
                res = rpc_var()
        else:
            res = rpc_var
        if not is_serializable(res):
            if isinstance(res, ophyd.StatusBase):
                return res
            if isinstance(res, list) and instr_params.get("func") in ["stage", "unstage"]:
                # pylint: disable=protected-access
                return [obj._staged for obj in res]
            res = None
            self.connector.raise_alarm(
                severity=Alarms.WARNING,
                alarm_type="TypeError",
                source=instr_params,
                msg=f"Return value of rpc call {instr_params} is not serializable.",
                metadata={},
            )
        return res

    def _send_rpc_result_to_client(
        self, device: str, instr_params: dict, res: Any, result: StringIO
    ):
        self.producer.set(
            MessageEndpoints.device_rpc(instr_params.get("rpc_id")),
            messages.DeviceRPCMessage(
                device=device, return_val=res, out=result.getvalue(), success=True
            ),
            expire=1800,
        )

    def _rpc_read_and_return(self, instr: messages.DeviceInstructionMessage) -> Any:
        res = self._read_and_update_devices([instr.content["device"]], instr.metadata)
        if isinstance(res, list) and len(res) == 1:
            res = res[0]
        return res

    def _rpc_read_configuration_and_return(self, instr: messages.DeviceInstructionMessage) -> Any:
        res = self._read_config_and_update_devices([instr.content["device"]], instr.metadata)
        if isinstance(res, list) and len(res) == 1:
            res = res[0]
        return res

    def _process_rpc_instruction(self, instr: messages.DeviceInstructionMessage) -> Any:
        # handle ophyd read. This is a special case because we also want to update the
        # buffered value in redis
        instr_params = instr.content.get("parameter")
        device_root = instr.content["device"].split(".")[0]
        if instr_params.get("func") == "read" or instr_params.get("func").endswith(".read"):
            if instr_params.get("func") == "read":
                obj = self.device_manager.devices[device_root].obj
            else:
                obj = rgetattr(
                    self.device_manager.devices[device_root].obj,
                    instr_params.get("func").split(".read")[0],
                )
            if isinstance(obj, ophyd.Device):
                return self._rpc_read_and_return(instr)
            if isinstance(obj, ophyd.Signal):
                if obj.kind not in [ophyd.Kind.omitted, ophyd.Kind.config]:
                    return self._rpc_read_and_return(instr)
                if obj.kind == ophyd.Kind.config:
                    return self._rpc_read_configuration_and_return(instr)
                if obj.kind == ophyd.Kind.omitted:
                    return obj.read()
        if instr_params.get("func") == "read_configuration" or instr_params.get("func").endswith(
            ".read_configuration"
        ):
            return self._rpc_read_configuration_and_return(instr)
        if instr_params.get("kwargs", {}).get("_set_property"):
            sub_access = instr_params.get("func").split(".")
            property_name = sub_access[-1]
            if len(sub_access) > 1:
                sub_access = sub_access[0:-1]
            else:
                sub_access = []
            obj = self.device_manager.devices[device_root].obj
            if sub_access:
                obj = rgetattr(obj, ".".join(sub_access))
            setattr(obj, property_name, instr_params.get("args")[0])
            return None

        # handle other ophyd methods
        rpc_var = rgetattr(self.device_manager.devices[device_root].obj, instr_params.get("func"))
        res = self._get_result_from_rpc(rpc_var, instr_params)
        if instr_params.get("func") == "put" or instr_params.get("func").endswith(".put"):
            if instr_params.get("func") == "put":
                obj = self.device_manager.devices[device_root].obj
            else:
                obj = rgetattr(
                    self.device_manager.devices[device_root].obj,
                    instr_params.get("func").split(".put")[0],
                )
            if obj.kind == ophyd.Kind.config:
                return self._rpc_read_configuration_and_return(instr)
            if obj.kind in [ophyd.Kind.normal, ophyd.Kind.hinted]:
                return self._rpc_read_and_return(instr)
        if isinstance(res, ophyd.StatusBase):
            res.__dict__["instruction"] = instr
            res.add_callback(self._status_callback)
            res = {
                "type": "status",
                "RID": instr.metadata.get("RID"),
                "success": res.success,
                "timeout": res.timeout,
                "done": res.done,
                "settle_time": res.settle_time,
            }
        elif isinstance(res, tuple) and hasattr(res, "_asdict") and hasattr(res, "_fields"):
            # convert namedtuple to dict
            res = {
                "type": "namedtuple",
                "RID": instr.metadata.get("RID"),
                "fields": res._fields,
                "values": res._asdict(),
            }
        elif isinstance(res, list) and isinstance(res[0], ophyd.Staged):
            res = [str(stage) for stage in res]
        return res

    def _send_rpc_exception(self, exc: Exception, instr: messages.DeviceInstructionMessage):
        exc_formatted = {
            "error": exc.__class__.__name__,
            "msg": exc.args,
            "traceback": traceback.format_exc(),
        }
        logger.info(f"Received exception: {exc_formatted}, {exc}")
        instr_params = instr.content.get("parameter")
        self.producer.set(
            MessageEndpoints.device_rpc(instr_params.get("rpc_id")),
            messages.DeviceRPCMessage(
                device=instr.content["device"], return_val=None, out=exc_formatted, success=False
            ),
        )

from fourier_core.predefine import *
from fourier_grx.comm.json.fi_comm_protocol_json import CommProtocolJson


class CommProtocolJsonM4(CommProtocolJson):
    def __init__(self, dynalink_interface=None):
        if dynalink_interface is None:
            if hasattr(self, "dynalink_interface"):
                pass
            else:
                from fourier_grx.comm.fi_dynalink_manager_grx import HardwareManagerM4 as HardwareManager
                self.dynalink_interface = DynalinkManager()
        else:
            self.dynalink_interface = dynalink_interface

    # ---------------------------------- server ----------------------------------

    def _server(self, receive_json=None) -> dict:
        send_json = super()._server(receive_json)

        tool_result, send_json_m4 = self._server_m4(self.receive_json)
        if tool_result == FunctionResult.SUCCESS:
            send_json.update(send_json_m4)

        return send_json

    def _server_m4(self, receive_json=None) -> (FunctionResult, dict):
        send_json = {}

        if receive_json is None:
            return FunctionResult.FAIL, send_json

        m4_data = receive_json.get("m4", None)
        if m4_data is None:
            return FunctionResult.FAIL, send_json

        send_json["m4"] = {}

        # request
        m4_write_fields = self.dynalink_interface.dynalink_m4.write_fields

        for field in m4_write_fields:
            if m4_data.get(field) is not None:
                setattr(self.dynalink_interface.dynalink_m4, field, m4_data.get(field))
                if "flag_" in field:
                    setattr(self.dynalink_interface.dynalink_m4, f"flag_{field}_update", FlagState.SET)

        # response
        m4_read_fields = self.dynalink_interface.dynalink_m4.read_fields

        for field in m4_read_fields:
            if m4_data.get(field) is not None:
                send_json["m4"][field] = getattr(self.dynalink_interface.dynalink_m4, field)

        return FunctionResult.SUCCESS, send_json

    # ---------------------------------- server ----------------------------------

    # ---------------------------------- client ----------------------------------

    def _client(self, receive_json=None) -> dict:
        send_json = super()._client(receive_json)

        tool_result, send_json_m4 = self._client_m4(self.receive_json)
        if tool_result == FunctionResult.SUCCESS:
            send_json.update(send_json_m4)

        return send_json

    def _client_m4(self, receive_json=None) -> (FunctionResult, dict):
        send_json = {}

        if receive_json is None:
            return FunctionResult.FAIL, send_json

        m4_data = receive_json.get("m4", None)
        if m4_data is None:
            return FunctionResult.FAIL, send_json

        send_json["m4"] = {}

        # response
        m4_read_fields = self.dynalink_interface.dynalink_m4.read_fields

        for field in m4_read_fields:
            if m4_data.get(field) is not None:
                setattr(self.dynalink_interface.dynalink_m4, field, m4_data.get(field))

        return FunctionResult.SUCCESS, send_json

    # ---------------------------------- client ----------------------------------

import json

from fourier_core.logger import *
from fourier_core.predefine import *


class CommProtocolJson:
    RECEIVE_DATA_MAX_LENGTH = 1024

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)

            cls.parse_type: str = "server"

            cls.receive_data = None
            cls.send_data = None
            cls.receive_json = None
            cls.send_json = None

        return cls._instance

    def __init__(self, dynalink_interface=None):
        if dynalink_interface is None:
            if hasattr(self, "dynalink_interface"):
                pass
            else:
                from fourier_grx.comm.fi_dynalink_manager import DynalinkManager
                self.dynalink_interface = DynalinkManager()
        else:
            self.dynalink_interface = dynalink_interface

    def set_parse_type(self, parse_type: str):
        if parse_type not in ["server", "client"]:
            Logger().print_error("CommProtocolJson set_parse_type unknown parse_type!")
            return FunctionResult.FAIL

        self.parse_type = parse_type

    def receive(self, data):
        # save to receive data
        self.receive_data = data

        try:
            self.receive_json = json.loads(self.receive_data)
        except Exception:
            Logger().print_error("not a json frame!")
            return FunctionResult.FAIL

        # Logger().print_debug(f"CommProtocolJson receive_json: {self.receive_json}")

        # parse json data
        send_json = self._parse()

        # prepare send data
        self.send_json = send_json

        # Logger().print_debug(f"CommProtocolJson send_json: {self.send_json}")

        send_data = json.dumps(self.send_json)
        self.send(send_data)

        return FunctionResult.SUCCESS

    def send(self, data):
        self.send_data = data

        return FunctionResult.SUCCESS

    def _parse(self):
        if self.parse_type == "server":
            send_json = self._server()
        elif self.parse_type == "client":
            send_json = self._client()
        else:
            Logger().print_error("CommProtocolJson unknown parse_type!")
            return FunctionResult.FAIL

        return send_json

    # ---------------------------------- server ----------------------------------

    def _server(self, receive_json=None) -> dict:
        if receive_json is None:
            pass
        else:
            self.receive_json = receive_json

        send_json = {}

        tool_result, send_json_error = self._server_error(self.receive_json)
        if tool_result == FunctionResult.SUCCESS:
            send_json.update(send_json_error)

        tool_result, send_json_app = self._server_app(self.receive_json)
        if tool_result == FunctionResult.SUCCESS:
            send_json.update(send_json_app)

        tool_result, send_json_robot = self._server_robot(self.receive_json)
        if tool_result == FunctionResult.SUCCESS:
            send_json.update(send_json_robot)

        tool_result, send_json_task = self._server_task(self.receive_json)
        if tool_result == FunctionResult.SUCCESS:
            send_json.update(send_json_task)

        return send_json

    def _server_app(self, receive_json=None) -> (FunctionResult, dict):
        send_json = {}

        if receive_json is None:
            return FunctionResult.FAIL, send_json

        app_data = receive_json.get("core", None)
        if app_data is None:
            return FunctionResult.FAIL, send_json

        send_json["core"] = {}

        # response
        app_read_fields = self.dynalink_interface.dynalink_core.read_fields

        for field in app_read_fields:
            if app_data.get(field) is not None:
                send_json["core"][field] = getattr(self.dynalink_interface.dynalink_core, field)

        return FunctionResult.SUCCESS, send_json

    def _server_error(self, receive_json=None) -> (FunctionResult, dict):
        send_json = {}

        if receive_json is None:
            return FunctionResult.FAIL, send_json

        error_data = receive_json.get("error")
        if error_data is None:
            return FunctionResult.FAIL, send_json

        send_json["error"] = {}

        # response
        error_read_fields = self.dynalink_interface.dynalink_error.read_fields

        for field in error_read_fields:
            if error_data.get(field) is not None:
                send_json["error"][field] = getattr(self.dynalink_interface.dynalink_error, field)

        return FunctionResult.SUCCESS, send_json

    def _server_robot(self, receive_json=None) -> (FunctionResult, dict):
        send_json = {}

        if receive_json is None:
            return FunctionResult.FAIL, send_json

        robot_data = receive_json.get("robot")
        if robot_data is None:
            return FunctionResult.FAIL, send_json

        send_json["robot"] = {}

        # response
        robot_read_fields = self.dynalink_interface.dynalink_robot.read_fields

        for field in robot_read_fields:
            if robot_data.get(field) is not None:
                send_json["robot"][field] = getattr(self.dynalink_interface.dynalink_robot, field)

        return FunctionResult.SUCCESS, send_json

    def _server_task(self, receive_json=None) -> (FunctionResult, dict):
        send_json = {}

        if receive_json is None:
            return FunctionResult.FAIL, send_json

        task_data = receive_json.get("task")
        if task_data is None:
            return FunctionResult.FAIL, send_json

        send_json["task"] = {}

        # request
        task_write_fields = self.dynalink_interface.dynalink_task.write_fields

        for field in task_write_fields:
            if task_data.get(field) is not None:
                setattr(self.dynalink_interface.dynalink_task, field, task_data.get(field))
                if "flag_" in field:
                    setattr(self.dynalink_interface.dynalink_task, f"flag_{field}_update", FlagState.SET)

        # response
        task_read_fields = self.dynalink_interface.dynalink_task.read_fields

        for field in task_read_fields:
            if task_data.get(field) is not None:
                send_json["task"][field] = getattr(self.dynalink_interface.dynalink_task, field)

        return FunctionResult.SUCCESS, send_json

    # ---------------------------------- server ----------------------------------

    # ---------------------------------- client ----------------------------------

    def _client(self, receive_json=None) -> dict:
        if receive_json is None:
            pass
        else:
            self.receive_json = receive_json

        send_json = {}

        tool_result, send_json_app = self._client_app(self.receive_json)
        if tool_result == FunctionResult.SUCCESS:
            send_json.update(send_json_app)

        tool_result, send_json_robot = self._client_robot(self.receive_json)
        if tool_result == FunctionResult.SUCCESS:
            send_json.update(send_json_robot)

        tool_result, send_json_task = self._client_task(self.receive_json)
        if tool_result == FunctionResult.SUCCESS:
            send_json.update(send_json_task)

        return send_json

    def _client_app(self, receive_json=None) -> (FunctionResult, dict):
        send_json = {}

        if receive_json is None:
            return FunctionResult.FAIL, send_json

        app_data = receive_json.get("core", None)
        if app_data is None:
            return FunctionResult.FAIL, send_json

        send_json["core"] = {}

        # response
        app_read_fields = self.dynalink_interface.dynalink_core.read_fields

        for field in app_read_fields:
            if app_data.get(field) is not None:
                setattr(self.dynalink_interface.dynalink_core, field, app_data.get(field))

        return FunctionResult.SUCCESS, send_json

    def _client_robot(self, receive_json=None) -> (FunctionResult, dict):
        send_json = {}

        if receive_json is None:
            return FunctionResult.FAIL, send_json

        robot_data = receive_json.get("robot", None)
        if robot_data is None:
            return FunctionResult.FAIL, send_json

        send_json["robot"] = {}

        # response
        robot_read_fields = self.dynalink_interface.dynalink_robot.read_fields

        for field in robot_read_fields:
            if robot_data.get(field) is not None:
                setattr(self.dynalink_interface.dynalink_robot, field, robot_data.get(field))

        return FunctionResult.SUCCESS, send_json

    def _client_task(self, receive_json=None) -> (FunctionResult, dict):
        send_json = {}

        if receive_json is None:
            return FunctionResult.FAIL, send_json

        task_data = receive_json.get("task", None)
        if task_data is None:
            return FunctionResult.FAIL, send_json

        send_json["task"] = {}

        # response
        task_read_fields = self.dynalink_interface.dynalink_task.read_fields

        for field in task_read_fields:
            if task_data.get(field) is not None:
                setattr(self.dynalink_interface.dynalink_task, field, task_data.get(field))
                if "flag_" in field:
                    setattr(self.dynalink_interface.dynalink_task, f"flag_{field}_update", FlagState.SET)

        return FunctionResult.SUCCESS, send_json

    # ---------------------------------- client ----------------------------------

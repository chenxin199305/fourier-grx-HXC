from typing import Dict


class FSMData(Dict):
    """
    任务数据类数据结构：
    {
        task_A : {command: {}, state: {}},
        task_B : {command: {}, state: {}},
        ...
    }
    """

    def __init__(self):
        super().__init__()
        
        self.data = {}

    def __str__(self):
        return str(self.data)

    def set_command(self, task_name, command: dict):
        if task_name not in self:
            self[task_name] = {"command": {}, "state": {}}

        self[task_name]["command"] = command

    def set_state(self, task_name, state: dict):
        if task_name not in self:
            self[task_name] = {"command": {}, "state": {}}

        self[task_name]["state"] = state

    def update_command(self, task_name, command: dict):
        if task_name not in self:
            self[task_name] = {"command": {}, "state": {}}

        self[task_name]["command"].update(command)

    def update_state(self, task_name, state: dict):
        if task_name not in self:
            self[task_name] = {"command": {}, "state": {}}

        self[task_name]["state"].update(state)

    def get_command(self, task_name=None) -> dict:
        if task_name:
            if task_name not in self:
                return {}
            return self[task_name]["command"]

        return {name: self[name]["command"] for name in self.keys()}

    def get_state(self, task_name=None) -> dict:
        if task_name:
            if task_name not in self:
                return {}
            return self[task_name]["state"]

        return {name: self[name]["state"] for name in self.keys()}

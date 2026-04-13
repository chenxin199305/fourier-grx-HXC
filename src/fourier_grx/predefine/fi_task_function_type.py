from enum import IntEnum


class TaskFunctionType(IntEnum):
    # for real robot
    META = 1
    COMPONENT = 2
    STANDALONE = 3
    ZENOH = 4

    # for simulation
    SIM_WEBOTS = 11
    SIM_MUJOCO = 12

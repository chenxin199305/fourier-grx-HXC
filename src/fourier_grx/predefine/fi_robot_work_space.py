from enum import IntEnum


class RobotWorkSpace(IntEnum):
    NONE = 0
    TASK_SPACE = 1  # TASK_SPACE means the calculation happens in task space, but still controls the joint movement
    URDF_SPACE = 2  # URDF_SPACE means the calculation happens in urdf space, but still controls the joint movement
    JOINT_SPACE = 3  # JOINT_SPACE means control the joint movement
    ACTUATOR_SPACE = 4  # ACTUATOR_SPACE means controls the actuator directly

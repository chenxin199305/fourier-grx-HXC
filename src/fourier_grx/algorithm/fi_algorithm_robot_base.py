from dataclasses import dataclass


@dataclass
class AlgorithmRobotBaseControlModel:
    stage = 0


@dataclass
class AlgorithmRobotBaseJointEffortControlModel(AlgorithmRobotBaseControlModel):
    target_joint_effort = []
    output_joint_control_mode = []
    output_joint_effort = []


class AlgorithmRobotBaseJointVelocityControlModel(AlgorithmRobotBaseControlModel):
    target_joint_velocity = []
    target_joint_acceleration = []
    output_joint_control_mode = []
    output_joint_velocity = []
    output_joint_acceleration = []


class AlgorithmRobotBaseJointPositionControlModel(AlgorithmRobotBaseControlModel):
    target_joint_position = []
    target_joint_velocity = []
    target_joint_acceleration = []
    output_joint_control_mode = []
    output_joint_position = []
    output_joint_velocity = []
    output_joint_acceleration = []


class AlgorithmRobotBaseJointMixControlModel(AlgorithmRobotBaseControlModel):
    target_joint_position = []
    target_joint_velocity = []
    target_joint_acceleration = []
    output_joint_control_mode = []
    output_joint_position = []
    output_joint_velocity = []
    output_joint_acceleration = []


class AlgorithmRobotBaseEndEffectorEffortControlModel(AlgorithmRobotBaseControlModel):
    target_end_effector_effort = []
    output_end_effector_control_mode = []
    output_joint_control_mode = []
    output_joint_position = []
    output_joint_velocity = []
    output_joint_acceleration = []
    output_joint_effort = []


class AlgorithmRobotBaseEndEffectorVelocityControlModel(AlgorithmRobotBaseControlModel):
    target_end_effector_velocity = []
    target_end_effector_acceleration = []
    output_joint_control_mode = []
    output_joint_position = []
    output_joint_velocity = []
    output_joint_acceleration = []
    output_joint_effort = []


class AlgorithmRobotBaseEndEffectorPositionControlModel(AlgorithmRobotBaseControlModel):
    target_end_effector_position = []
    target_end_effector_velocity = []
    target_end_effector_acceleration = []
    output_joint_control_mode = []
    output_joint_position = []
    output_joint_velocity = []
    output_joint_acceleration = []
    output_joint_effort = []


class AlgorithmRobotBaseEndEffectorMixControlModel(AlgorithmRobotBaseControlModel):
    target_end_effector_position = []
    target_end_effector_velocity = []
    target_end_effector_acceleration = []
    output_joint_control_mode = []
    output_joint_position = []
    output_joint_velocity = []
    output_joint_acceleration = []
    output_joint_effort = []


class AlgorithmRobotBaseFindHomeControlModel(AlgorithmRobotBaseControlModel):
    output_joint_control_mode = []
    output_joint_position = []
    output_joint_velocity = []
    output_joint_acceleration = []
    output_joint_effort = []


class AlgorithmRobotBaseSetHomeControlModel(AlgorithmRobotBaseControlModel):
    output_joint_control_mode = []
    output_joint_position = []
    output_joint_velocity = []
    output_joint_acceleration = []
    output_joint_effort = []


class AlgorithmRobotBaseClearAlarmControlModel(AlgorithmRobotBaseControlModel):
    output_joint_control_mode = []
    output_joint_position = []
    output_joint_velocity = []
    output_joint_acceleration = []
    output_joint_effort = []


class AlgorithmRobotBaseClearFaultControlModel(AlgorithmRobotBaseControlModel):
    output_joint_control_mode = []
    output_joint_position = []
    output_joint_velocity = []
    output_joint_acceleration = []
    output_joint_effort = []


class AlgorithmRobotBaseSetConfigControlModel(AlgorithmRobotBaseControlModel):
    output_joint_control_mode = []


class AlgorithmRobotBaseServoZeroControlModel(AlgorithmRobotBaseControlModel):
    pass


class AlgorithmRobotBaseServoOnControlModel(AlgorithmRobotBaseControlModel):
    output_joint_control_mode = []
    output_joint_position = []
    output_joint_velocity = []
    output_joint_acceleration = []
    output_joint_effort = []


class AlgorithmRobotBaseServoOffControlModel(AlgorithmRobotBaseControlModel):
    output_joint_control_mode = []
    output_joint_position = []
    output_joint_velocity = []
    output_joint_acceleration = []
    output_joint_effort = []


class AlgorithmRobotBaseServoRebootControlModel(AlgorithmRobotBaseControlModel):
    pass


class AlgorithmRobotBasePauseMotionControlModel(AlgorithmRobotBaseControlModel):
    target_joint_acceleration = []
    output_joint_control_mode = []
    output_joint_position = []
    output_joint_velocity = []
    output_joint_acceleration = []
    output_joint_effort = []


class AlgorithmRobotBaseSensorCalibrationControlModel(AlgorithmRobotBaseControlModel):
    pass


class AlgorithmRobotBaseSensorSoftwareVersionControlModel(AlgorithmRobotBaseControlModel):
    pass

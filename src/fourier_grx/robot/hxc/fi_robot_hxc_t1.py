from fourier_core.predefine import *

from fourier_grx.predefine import *
from fourier_grx.task.hxc import *
from fourier_grx.task.fi_task_registry import TaskRegistry

from fourier_grx.robot.hxc.fi_robot_hxc_param import *
from fourier_grx.robot.hxc.fi_robot_hxc import RobotHXC
from fourier_grx.robot.fi_robot_registry import RobotRegistry


@RobotRegistry.register(
    name=RobotName.HXCT1,
    backend=RobotBackend.Real,
)
class RobotHXCT1(RobotHXC):
    def __init__(self):
        super().__init__()

        # task
        RobotHXCT1._init_task(self)

    # =====================================================================================================

    def _load_param(self) -> FunctionResult:
        self.robot_param = RobotHXCT1Param()

        return FunctionResult.SUCCESS

    def _init_robot(self) -> FunctionResult:
        self.robot_name = RobotName.HXCT1

        return FunctionResult.SUCCESS

    def _init_task(self) -> FunctionResult:
        for task_cls in TaskRegistry.get_tasks(RobotName.HXCT1):
            self._register_task(task_cls)

        return FunctionResult.SUCCESS

    # =====================================================================================================

    @staticmethod
    def base_imu_transform(
            sensor_imu_group_measured_quat,
            sensor_imu_group_measured_euler_angle,
            sensor_imu_group_measured_angular_velocity,
            sensor_imu_group_measured_linear_acceleration,
    ):
        # imu
        # base link imu is the first imu,
        # change the value to match the upside down installation direction
        out_sensor_imu_group_measured_quat = numpy.array(
            [
                -sensor_imu_group_measured_quat[3],
                -sensor_imu_group_measured_quat[2],
                sensor_imu_group_measured_quat[0],
                -sensor_imu_group_measured_quat[1],
            ]
        )

        out_sensor_imu_group_measured_euler_angle = numpy.array(
            [
                numpy.pi - sensor_imu_group_measured_euler_angle[0]
                if sensor_imu_group_measured_euler_angle[0] > 0
                else -numpy.pi - sensor_imu_group_measured_euler_angle[0],
                sensor_imu_group_measured_euler_angle[1],
                sensor_imu_group_measured_euler_angle[2],
            ]
        )  # unit : rad

        out_sensor_imu_group_measured_angular_velocity = numpy.array(
            [
                -sensor_imu_group_measured_angular_velocity[1],
                -sensor_imu_group_measured_angular_velocity[0],
                -sensor_imu_group_measured_angular_velocity[2],
            ]
        )  # unit : rad/s

        out_sensor_imu_group_measured_linear_acceleration = (
                numpy.array(
                    [
                        -sensor_imu_group_measured_linear_acceleration[1],
                        -sensor_imu_group_measured_linear_acceleration[0],
                        -sensor_imu_group_measured_linear_acceleration[2],
                    ]
                )
                * -9.81
        )  # unit : m/s^2

        return (
            out_sensor_imu_group_measured_quat,
            out_sensor_imu_group_measured_euler_angle,
            out_sensor_imu_group_measured_angular_velocity,
            out_sensor_imu_group_measured_linear_acceleration,
        )

    def control_loop_update_state(self) -> FunctionResult:
        """
        Changes:
        1. update imu data
        2. update base state
        3. update leg joint position, velocity, acceleration, torque
        4. update state estimator
        """

        RobotHXC.control_loop_update_state(self)

        # imu
        # base link imu is the first imu, change the value to match the upside down installation direction
        (
            self.sensor_imu_group_measured_quat[0:4],
            self.sensor_imu_group_measured_euler_angle[0:3],
            self.sensor_imu_group_measured_angular_velocity[0:3],
            self.sensor_imu_group_measured_linear_acceleration[0:3]
        ) = self.base_imu_transform(self.sensor_imu_group_measured_quat,
                                    self.sensor_imu_group_measured_euler_angle,
                                    self.sensor_imu_group_measured_angular_velocity,
                                    self.sensor_imu_group_measured_linear_acceleration)

        return FunctionResult.SUCCESS

    # =====================================================================================================

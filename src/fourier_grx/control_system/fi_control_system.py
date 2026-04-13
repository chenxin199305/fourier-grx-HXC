import os
import sys
import time

from fourier_core.logger import *
from fourier_core.predefine import *
from fourier_core.hardware import *

from fourier_grx.predefine import *
from fourier_grx.robot import RobotFactory
from fourier_grx.task import TaskMenuRobotBase, TaskMenuRobotReal
from fourier_grx.control_system.fi_control_system_developer_mode import developer_mode_init


class ControlSystem:
    time_of_robot_control_loop_input_and_calculate_target_s = 0

    def __new__(cls):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)

        return cls._instance

    def __init__(self):
        pass

    @classmethod
    def _reset(cls):
        """Reset singleton instance. For testing purposes only."""
        if hasattr(cls, '_instance'):
            del cls._instance

    # ---------------------------------------------------------------------------

    @property
    def robot_interface(self):
        return RobotFactory()

    def check_robot_interface(self) -> FunctionResult:
        if self.robot_interface is None:
            Logger().print_error("ControlSystem: The robot model has not been initialized!!!")
            return FunctionResult.FAIL

        return FunctionResult.SUCCESS

    def check_input_control_frequency(
            self,
            input_control_frequency: float
    ) -> (FunctionResult, float):

        if input_control_frequency <= 0.0:
            Logger().print_error("ControlSystem: control_frequency should be greater than 0, "
                                 "the value has been set to 50")
            control_frequency = 50.0

            return FunctionResult.FAIL, control_frequency

        if input_control_frequency > 500.0:
            Logger().print_warning("ControlSystem: control_frequency should be less than 500, "
                                   "the value has been clipped to 500")
            control_frequency = 500.0

            return FunctionResult.FAIL, control_frequency

        control_frequency = input_control_frequency

        return FunctionResult.SUCCESS, control_frequency

    # =====================================================================================================

    def sdk_mode(self, control_frequency: float = 400.0) -> FunctionResult:
        """
        SDK mode for robot control system.

        :param control_frequency: Control frequency for the robot. Default is 400 Hz.
        :return: FunctionResult indicating success or failure.
        """
        if self.check_robot_interface() == FunctionResult.SUCCESS:
            pass
        else:
            return FunctionResult.FAIL

        # change deploy mode to SDK_MODE
        self.robot_interface.deploy_mode = DeployMode.SDK_MODE

        # check input control frequency validity
        check_result, control_frequency = self.check_input_control_frequency(control_frequency)
        if check_result == FunctionResult.FAIL:
            return FunctionResult.FAIL

        # init, comm, prepare robot...
        self.robot_control_loop_init(control_period=1 / control_frequency)
        self.robot_control_loop_before()

        # developer mode init
        self.robot_control_set_task_command(TaskMenuRobotReal.TASK_SERVO_OFF)

        return FunctionResult.SUCCESS

    def developer_mode(self, servo_on: bool = False, control_frequency: float = 400.0) -> FunctionResult:
        """
        Developer mode for robot control system.

        :param servo_on: Whether to turn on the servo motors.
        :param control_frequency: Control frequency for the robot. Default is 400 Hz.
        :return: FunctionResult indicating success or failure.
        """

        if self.check_robot_interface() == FunctionResult.SUCCESS:
            pass
        else:
            return FunctionResult.FAIL

        # change deploy mode to DEVELOPER_MODE
        self.robot_interface.deploy_mode = DeployMode.DEVELOPER_MODE

        # check input control frequency validity
        check_result, control_frequency = self.check_input_control_frequency(control_frequency)
        if check_result == FunctionResult.FAIL:
            return FunctionResult.FAIL

        # init, comm, prepare robot...
        self.robot_control_loop_init(control_period=1 / control_frequency)
        self.robot_control_loop_before()

        # dev mode init
        if servo_on is False:
            developer_mode_init(servo_on=FlagState.CLEAR)
        else:
            developer_mode_init(servo_on=FlagState.SET)

        # sleep some time to allow data updated
        time.sleep(2)

        return FunctionResult.SUCCESS

    def play_mode(self, control_period: float | None = None) -> FunctionResult:
        """
        Play mode for robot control system.

        :param control_period: Control period for the robot. If None, uses default control period.
        :return: FunctionResult indicating success or failure.
        """
        if self.check_robot_interface() == FunctionResult.SUCCESS:
            pass
        else:
            return FunctionResult.FAIL

        # init, comm, prepare robot...
        self.robot_control_loop_init(control_period=control_period)
        self.robot_control_loop_before()

        # will enter self.robot_interface.ready_state()'s state

        return FunctionResult.SUCCESS

    def debug_mode(self, control_period: float | None = None) -> FunctionResult:
        """
        Debug mode for robot control system.

        :param control_period: Control period for the robot. If None, uses default control period.
        :return: FunctionResult indicating success or failure.
        """
        if self.check_robot_interface() == FunctionResult.SUCCESS:
            pass
        else:
            return FunctionResult.FAIL

        # init, comm, prepare robot...
        self.robot_control_loop_init(control_period=control_period)
        self.robot_control_loop_before()

        # change task command to TaskMenuRobotBase.TASK_IDLE
        self.robot_interface.set_task_command(task_command=TaskMenuRobotBase.TASK_IDLE)

        return FunctionResult.SUCCESS

    # =====================================================================================================

    def robot_control_loop_init(self, control_period: float | None = None) -> FunctionResult:
        """
        Robot control loop, init stage
        """
        if self.check_robot_interface() == FunctionResult.SUCCESS:
            pass
        else:
            return FunctionResult.FAIL

        # print robot info
        self.robot_interface.log_robot_info()

        # print tasks info
        self.robot_interface.log_task_info()

        # update robot control period
        if control_period is None:
            pass
        else:
            self.robot_interface.control_loop_intf_set_control_period(control_period)

        # set steps
        self.robot_interface.control_loop_intf_set_steps()

        return FunctionResult.SUCCESS

    def robot_control_loop_before(self) -> FunctionResult:
        """
        Robot control loop, before stage
        """
        if self.check_robot_interface() == FunctionResult.SUCCESS:
            pass
        else:
            return FunctionResult.FAIL

        # hardware initialize (for common component)
        self.robot_interface.control_loop_intf_init()

        return FunctionResult.SUCCESS

    def robot_control_loop_run(self) -> FunctionResult:
        """
        Robot control loop, run stage
        """
        self.robot_interface.control_loop_intf_update_state()
        self.robot_interface.control_loop_intf_algorithm()
        self.robot_interface.control_loop_intf_output_control()
        self.robot_interface.control_loop_intf_developer_related()

        return FunctionResult.SUCCESS

    def robot_control_loop_algorithm(self) -> FunctionResult:
        """
        Robot control loop, algorithm stage
        """
        self.robot_interface.control_loop_intf_algorithm()

        return FunctionResult.SUCCESS

    def robot_control_loop_communication(self) -> FunctionResult:
        """
        Robot control loop, communication stage
        """
        self.robot_interface.communication_loop_intf_run()

        return FunctionResult.SUCCESS

    # =====================================================================================================
    # 接口层函数 (Python 开发)

    def robot_control_set_task_command(self, task_command: int) -> FunctionResult:
        """
        Set task command to robot interface.

        :param task_command: task command
        :return: FunctionResult
        """
        self.robot_interface.set_task_command(task_command=task_command)

        return FunctionResult.SUCCESS

    def robot_control_set_task_component(self, component_command: int) -> FunctionResult:
        """
        Set task component to robot interface.

        :param component_command: component command
        :return: FunctionResult
        """
        self.robot_interface.set_component_command(component_command=component_command)

        return FunctionResult.SUCCESS

    def robot_control_loop_get_state(self) -> dict:
        """
        Get robot state from control loop interface.

        :return: state_dict
        """
        state_dict = self.robot_interface.control_loop_intf_get_state()

        return state_dict

    def robot_control_loop_set_control(self, control_dict: dict) -> FunctionResult:
        """
        Set control command to control loop interface.

        :param control_dict: control command dictionary
        :return: FunctionResult
        """
        self.robot_interface.control_loop_intf_set_control(control_dict)

        return FunctionResult.SUCCESS

    # ---------------------------------------------------------------------------

    def get_info(self) -> dict:
        info_dict = {
            "fourier_core_version": self.robot_interface.fourier_core_version,
            "fourier_grx_version": self.robot_interface.fourier_grx_version,
        }

        return info_dict

    # ---------------------------------------------------------------------------

    def reboot_system(self) -> None:
        """
        Restarts the current program.

        Note: this function does not return.
        Any cleanup action (like saving data) must be done before calling this function.
        """
        print("ready to restart program......")
        python = sys.executable
        os.execl(python, python, *sys.argv)

    def shutdown(self) -> None:
        """
        Shutting down the robot control system.
        """
        print("ready to shutdown program......")
        os.system("shutdown -h now")  # Linux

    # =====================================================================================================

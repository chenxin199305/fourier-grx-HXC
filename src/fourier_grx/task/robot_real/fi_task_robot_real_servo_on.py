from fourier_core.predefine import *

from fourier_grx.predefine import *
from fourier_grx.fsm import *
from fourier_grx.task import *

from fourier_grx.algorithm.robot_real.fi_algorithm_robot_real_servo_on import (
    AlgorithmRobotRealServoOnControlModel,
)
from fourier_grx.task.robot_real.fi_task_robot_real_base import (
    TaskRobotRealBase,
)
from fourier_grx.task.fi_task_registry import TaskRegistry


@TaskRegistry.register(
    RobotName.Base,
)
class TaskRobotRealServoOn(TaskRobotRealBase):
    def register(
            self,
            fsm_manager: FSMManager,
    ) -> FunctionResult:
        """
        Bind the task_manager to the self.fsm_manager,
        create the task_model and return the FunctionResult.SUCCESS.
        """

        self.fsm_manager = fsm_manager
        self.task_model = AlgorithmRobotRealServoOnControlModel()
        self.task_key = TaskMenuRobotReal.TASK_SERVO_ON

        return FunctionResult.SUCCESS

    # =====================================================================================================

    def _function_meta(self, **kwargs) -> FunctionResult:
        """
        Return the meta information of the task.
        """

        # import
        from fourier_grx.robot.robot_real import RobotReal

        # model
        robot: RobotReal = self.fsm_manager

        # --------------------------------------------------

        if self.task_model.stage == AlgorithmStage.STAGE_INIT:
            # output
            robot.work_space = RobotWorkSpace.ACTUATOR_SPACE
            for actuator in robot.actuators:
                actuator.set_target_control_mode(ActuatorControlMode.SERVO_ON)
                actuator.set_target_position(0)
                actuator.set_target_velocity(0)
                actuator.set_target_effort(0)
                actuator.set_target_current(0)

            # update stage
            self.task_model.stage = AlgorithmStage.STAGE_START

        elif self.task_model.stage == AlgorithmStage.STAGE_START:
            # output
            robot.work_space = RobotWorkSpace.ACTUATOR_SPACE
            for actuator in robot.actuators:
                actuator.set_target_control_mode(ActuatorControlMode.NONE)
                actuator.set_target_position(0)
                actuator.set_target_velocity(0)
                actuator.set_target_effort(0)
                actuator.set_target_current(0)

            # update stage
            self.task_model.stage = AlgorithmStage.STAGE_RUN

        elif self.task_model.stage == AlgorithmStage.STAGE_RUN:
            # output
            robot.work_space = RobotWorkSpace.ACTUATOR_SPACE
            for actuator in robot.actuators:
                actuator.set_target_control_mode(ActuatorControlMode.NONE)

            # update stage
            self.task_model.stage = AlgorithmStage.STAGE_FINISH

        elif self.task_model.stage == AlgorithmStage.STAGE_FINISH:
            # update stage
            self.task_model.stage = AlgorithmStage.STAGE_SWITCH

        elif self.task_model.stage == AlgorithmStage.STAGE_SWITCH:
            # switch to idle task
            robot.set_task_command(task_command=TaskMenuRobotBase.TASK_IDLE)

        else:
            self.task_model.stage = AlgorithmStage.STAGE_INIT

        # --------------------------------------------------

        return FunctionResult.SUCCESS

    def function_component(self, **kwargs) -> FunctionResult:
        self._function_meta(**kwargs)

        return FunctionResult.SUCCESS

    def function_standalone(self, **kwargs) -> FunctionResult:
        self._function_meta(**kwargs)

        return FunctionResult.SUCCESS

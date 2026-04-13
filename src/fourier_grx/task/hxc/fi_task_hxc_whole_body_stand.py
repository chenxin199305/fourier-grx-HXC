import numpy

from fourier_core.logger import *
from fourier_core.predefine import *

from fourier_grx.predefine import *
from fourier_grx.fsm import *
from fourier_grx.task import *

from fourier_grx.robot.hxc.fi_robot_hxc_param import RobotHXCParam
from fourier_grx.algorithm.hxc import (
    AlgorithmHXCWholeBodyStandControlModel,
)
from fourier_grx.task.hxc.fi_task_hxc_base import (
    TaskHXCBase,
)
from fourier_grx.task.fi_task_registry import TaskRegistry


@TaskRegistry.register(
    RobotName.HXCT1,
)
class TaskHXCWholeBodyStand(TaskHXCBase):
    def register(
            self,
            fsm_manager: FSMManager,
    ) -> FunctionResult:
        """
        Stand control for all 16 joints.

        Data flow (every 20 ms):
          Sensor (16 joint positions)
            → stand algorithm  (AlgorithmHXCWholeBodyStandControlModel)
            → PD position targets for 12 leg joints
            + VELOCITY = 0 for 4 wheel joints
        """
        super().register(fsm_manager=fsm_manager)

        self.task_model = AlgorithmHXCWholeBodyStandControlModel(dt=self.fsm_manager.control_period)
        self.task_key   = TaskMenuHXC.TASK_WHOLE_BODY_STAND_CONTROL

        return FunctionResult.SUCCESS

    # =====================================================================================================

    def _function_meta(self, **kwargs) -> FunctionResult:

        # ---- 1. Read sensor data ------------------------------------------------
        joint_pos_full = self.robot_joint_position      # (16,) rad

        # ---- 2. Map to the 16-joint algorithm space ----------------------------
        n = self.task_model.number_of_joint             # 16

        joint_pos_algo = numpy.zeros(n)
        for i in range(n):
            idx               = self.task_model.index_of_joints_real_robot[i]
            joint_pos_algo[i] = joint_pos_full[idx]

        # ---- 3. Run stand algorithm → position targets for all 16 joints -------
        _, _, joint_target_position = self.task_model.run(
            joint_measured_position=joint_pos_algo,
        )

        # ---- 4. Set output buffers: PD for leg joints, VELOCITY for wheel joints
        wheel_indices = set(RobotHXCParam.indexes_of_wheel_body_joints.tolist())
        joint_target_control_mode = [
            JointControlMode.VELOCITY if i in wheel_indices else JointControlMode.PD
            for i in range(n)
        ]

        self.work_space                = RobotWorkSpace.JOINT_SPACE
        self.joint_target_control_mode = joint_target_control_mode
        self.joint_target_kp           = self.task_model.pd_control_kp_real_robot.copy()
        self.joint_target_kd           = self.task_model.pd_control_kd_real_robot.copy()
        self.joint_target_position     = joint_target_position  # unit: rad
        self.joint_target_velocity     = numpy.zeros(n)         # wheel target: 0 rad/s

        return FunctionResult.SUCCESS

    # =====================================================================================================

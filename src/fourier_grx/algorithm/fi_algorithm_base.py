from fourier_core.logger import *

from fourier_grx.predefine import *


class AlgorithmBaseControlModel:
    def __init__(self):
        """
        基础算法模型类
        """

        self.stage = AlgorithmStage.STAGE_INIT
        self.interruptable = True

    def reset(self, **kwargs) -> None:
        pass

    def run(self, **kwargs) -> None:
        pass

    def set_stage(self, stage: AlgorithmStage, **kwargs) -> None:
        """
        设置算法阶段
        """

        if self.interruptable:
            # 如果模型允许中断，则可以直接设置到任意阶段。
            self.stage = stage
        else:
            if (
                    # 如果模型不允许中断，
                    # 但是要设置的阶段是初始阶段
                    # 表明是从其他任务切换到当前任务的，
                    # 所以要允许切换到初始阶段。
                    stage == AlgorithmStage.STAGE_INIT
            ):
                self.stage = stage
            elif (
                    # 如果模型不允许中断，
                    # 但是当前模型的阶段是初始阶段或其他已完成任务的阶段，
                    # 则可以切换到指定阶段。
                    self.stage == AlgorithmStage.STAGE_INIT or
                    self.stage == AlgorithmStage.STAGE_START or
                    self.stage == AlgorithmStage.STAGE_ERROR or
                    self.stage == AlgorithmStage.STAGE_SUCCESS or
                    self.stage == AlgorithmStage.STAGE_FINISH or
                    self.stage == AlgorithmStage.STAGE_SWITCH
            ):
                self.stage = stage
            else:
                Logger().print_info(
                    f"{self.__class__.__name__} set_stage: "
                    f"Cannot change stage from {self.stage} to {stage}, "
                    f"model's interruptable is False."
                )

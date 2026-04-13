from threading import Thread

from fourier_core.predefine import *

from fourier_grx.robot import RobotFactory
from fourier_grx.task import TaskMenuRobotReal


def other_mode_init(mode_name) -> int:
    # TODO: right now 400Hz is stable, need to change to use value in config.yaml later
    RobotFactory().control_period = 1 / 400  # unit : s

    # change task command to TaskMenuRobotReal.TASK_SERVO_ON
    RobotFactory().set_task_command(task_command=TaskMenuRobotReal.TASK_SERVO_ON)

    # create thread
    thread_handle = Thread(
        target=thread_other_mode_handle,
        args=(mode_name,),
        daemon=True,
    )
    thread_handle.start()

    return FunctionResult.SUCCESS


def thread_other_mode_handle(args):
    print("======================================================================================")
    mode_name = args[0]

    loop_period_in_s = RobotFactory().control_period
    print("thread_", mode_name, "_mode_control_loop period: ", loop_period_in_s, "s")

    print("not support other_mode!!!")

from threading import Thread
from ischedule import run_loop, schedule

from fourier_core.predefine import *

from fourier_grx.robot import RobotFactory
from fourier_grx.task import TaskMenuRobotReal


def developer_mode_init(servo_on=FlagState.CLEAR) -> FunctionResult:
    # change task command to TaskMenuRobotReal.TASK_SERVO_ON or TaskMenuRobotReal.TASK_SERVO_OFF
    if servo_on == FlagState.SET:
        RobotFactory().set_task_command(task_command=TaskMenuRobotReal.TASK_SERVO_ON)
    else:
        RobotFactory().set_task_command(task_command=TaskMenuRobotReal.TASK_SERVO_OFF)

    # --------------------------------------------------
    # create peripheral thread
    from fourier_grx.thread import thread_init, thread_deinit

    thread_init()
    # --------------------------------------------------

    # create developer thread
    thread_handle = Thread(
        target=thread_developer_mode_handle,
        daemon=True,
    )
    thread_handle.start()

    return FunctionResult.SUCCESS


def developer_mode_deinit() -> FunctionResult:
    # --------------------------------------------------
    # disable peripheral thread
    from fourier_grx.thread import thread_init, thread_deinit

    thread_deinit()
    # --------------------------------------------------

    return FunctionResult.SUCCESS


def thread_developer_mode_handle():
    print("======================================================================================")

    loop_period_in_s = RobotFactory().control_period
    print("thread_developer_mode_control_loop period: ", loop_period_in_s, "s")

    schedule(schedule_developer_mode_handle, interval=loop_period_in_s)
    print("thread_developer_mode_control_loop enter loop")

    run_loop()


def schedule_developer_mode_handle():
    # update state
    RobotFactory().control_loop_intf_update_state()

    # algorithm (user customized...)
    # time cost : 0.02ms
    RobotFactory().control_loop_intf_algorithm()

    # output control
    RobotFactory().control_loop_intf_output_control()

    # developer related
    RobotFactory().control_loop_intf_developer_related()

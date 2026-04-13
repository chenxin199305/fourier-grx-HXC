from fourier_core.predefine import *


def process_set_priority() -> FunctionResult:
    """
    设置进程优先级
    """

    """
    Jason 2024-12-29:
    Psutil 进程优先级设置要求 root 权限
    出于安全考虑，暂时不开启
    """
    # process = psutil.Process()
    # Logger().print_debug(f"Before Setting: \n"
    #                      f"Process ID: {process.pid} \n"
    #                      f"Process Name: {process.name()} \n"
    #                      f"Process Nice: {process.nice()} \n"
    #                      f"Process I/O Priority: {process.ionice()} \n"
    #                      f"Process CPU Affinity: {process.cpu_affinity()}")
    #
    # """
    # 设置进程优先级:
    # 0 ~ 20: 优先级逐渐降低，由用户态设置
    # -20 ~ -1: 优先级逐渐升高，由内核态设置，需要 root 权限
    # """
    # process.nice(0)
    #
    # """
    # 设置进程 I/O 优先级:
    # IOPRIO_CLASS_NONE = 0  # 无
    # IOPRIO_CLASS_RT = 1  # 实时
    # IOPRIO_CLASS_BE = 2  # 最佳效率
    # IOPRIO_CLASS_IDLE = 3  # 空闲
    # """
    # process.ionice(psutil.IOPRIO_CLASS_NONE, 0)
    #
    # """
    # 设置 cpu 亲和性:
    # """
    # process.cpu_affinity([0, 1, 2, 3])
    #
    # Logger().print_debug(f"After Setting: \n"
    #                      f"Process ID: {process.pid} \n"
    #                      f"Process Name: {process.name()} \n"
    #                      f"Process Nice: {process.nice()} \n"
    #                      f"Process I/O Priority: {process.ionice()} \n"
    #                      f"Process CPU Affinity: {process.cpu_affinity()}")

    return FunctionResult.SUCCESS


def process_init() -> FunctionResult:
    """
    初始化通信进程

    Jason 2024-11-12:
    通信子进程的初始化必须要在主进程其他线程之前，因为不然的话，
    在子进程中，可能对应的子线程也会被复制一份，从而造成有多个线程同时运行的情况！！！
    """
    from fourier_grx.process.sync.fi_process_sync_interface import sync_init
    from fourier_grx.process.dds.fi_process_dds_interface import dds_init
    from fourier_grx.process.record.fi_process_record_interface import record_init
    from fourier_grx.process.rerun.fi_process_rerun_interface import rerun_init
    from fourier_grx.process.streamlit.fi_process_streamlit_interface import streamlit_init
    from fourier_grx.process.teleoperation.fi_process_teleoperation_interface import teleoperation_init

    sync_init()
    dds_init()
    record_init()
    rerun_init()
    streamlit_init()
    teleoperation_init()

    return FunctionResult.SUCCESS


def process_deinit() -> FunctionResult:
    """
    释放通信进程
    """
    from fourier_grx.process.sync.fi_process_sync_interface import sync_deinit
    from fourier_grx.process.dds.fi_process_dds_interface import dds_deinit
    from fourier_grx.process.record.fi_process_record_interface import record_deinit
    from fourier_grx.process.rerun.fi_process_rerun_interface import rerun_deinit
    from fourier_grx.process.streamlit.fi_process_streamlit_interface import streamlit_deinit
    from fourier_grx.process.teleoperation.fi_process_teleoperation_interface import teleoperation_deinit

    sync_deinit()
    dds_deinit()
    record_deinit()
    rerun_deinit()
    streamlit_deinit()
    teleoperation_deinit()

    return FunctionResult.SUCCESS

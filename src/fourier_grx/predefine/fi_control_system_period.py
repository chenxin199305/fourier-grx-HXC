class ControlSystemPeriod:
    # Default periods for various control system tasks
    DEFAULT_CTRL_PERIOD = 0.02  # 20ms, 50Hz
    DEFAULT_TASK_PERIOD = 0.02  # 20ms, 50Hz

    # Default periods for other tasks
    DEFAULT_COMM_PERIOD = 1.0  # 1s, 1Hz
    DEFAULT_SYNC_PERIOD = 1.0  # 1s, 1Hz
    DEFAULT_RERUN_PERIOD = 1.0  # 1s, 1Hz
    DEFAULT_STREAMLIT_PERIOD = 1.0  # 1s, 1Hz
    DEFAULT_RECORD_PERIOD = 1.0  # 1s, 1Hz
    DEFAULT_DDS_PERIOD = 1.0  # 1s, 1Hz

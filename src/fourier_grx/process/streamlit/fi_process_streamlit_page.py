"""
Fourier-GRx Streamlit Page

This file is used to create a Streamlit page for the Fourier-GRx robot.
Run this file to start the Streamlit server by:
- `streamlit run src/fourier_grx/process/streamlit/fi_process_streamlit_page.py`
"""

import streamlit as st
from streamlit import selectbox

from fourier_grx.task.menu import (
    TaskMenuRobotBase,
    TaskMenuRobotReal,
    TaskMenuHXC,
)


# --------------------------------------------------
# Global variables
@st.cache_resource
def get_fourier_grx_sync_client():
    # 初始化 SyncClient 进行数据同步
    from fourier_grx.process.sync.fi_sync_client import SyncClient

    return SyncClient()


@st.cache_resource
def get_fourier_grx_dynalink_manager():
    # 初始化 DynalinkManager 用于通信
    from fourier_grx.comm import DynalinkManager

    return DynalinkManager()


# --------------------------------------------------


# Create a label
st.write("**Fourier-GRx Control Panel**")

# --------------------------------------------------
# callback functions
if "axis_left_value_x" not in st.session_state:
    st.session_state.axis_left_value_x = 0

if "axis_left_value_y" not in st.session_state:
    st.session_state.axis_left_value_y = 0

if "axis_right_value_x" not in st.session_state:
    st.session_state.axis_right_value_x = 0

if "axis_right_value_y" not in st.session_state:
    st.session_state.axis_right_value_y = 0

if "selectbox_option" not in st.session_state:
    st.session_state.selectbox_option = TaskMenuRobotReal.TASK_SERVO_OFF.name


def callback_button_left_on_click():
    print("Left button clicked.")

    st.session_state.axis_left_value_x -= 0.25
    if st.session_state.axis_left_value_x < -1.0:
        st.session_state.axis_left_value_x = -1.0

    dynalink_manager = get_fourier_grx_dynalink_manager()
    dynalink_manager.dynalink_grx.virtual_joystick_axis_left = [
        st.session_state.axis_left_value_x,
        0.0,
    ]

    sync_client = get_fourier_grx_sync_client()
    sync_client.publish(
        key="grx",
        value={
            "virtual_joystick_axis_left": dynalink_manager.dynalink_grx.virtual_joystick_axis_left,
        }
    )


def callback_button_forward_on_click():
    print("Forward button clicked.")

    st.session_state.axis_left_value_y += 0.25
    if st.session_state.axis_left_value_y > 1.0:
        st.session_state.axis_left_value_y = 1.0

    dynalink_manager = get_fourier_grx_dynalink_manager()
    dynalink_manager.dynalink_grx.virtual_joystick_axis_left = [
        0.0,
        st.session_state.axis_left_value_y,
    ]

    sync_client = get_fourier_grx_sync_client()
    sync_client.publish(
        key="grx",
        value={
            "virtual_joystick_axis_left": dynalink_manager.dynalink_grx.virtual_joystick_axis_left,
        }
    )


def callback_button_backward_on_click():
    print("Backward button clicked.")

    st.session_state.axis_left_value_y -= 0.25
    if st.session_state.axis_left_value_y < -1.0:
        st.session_state.axis_left_value_y = -1.0

    dynalink_manager = get_fourier_grx_dynalink_manager()
    dynalink_manager.dynalink_grx.virtual_joystick_axis_left = [
        0.0,
        st.session_state.axis_left_value_y,
    ]

    sync_client = get_fourier_grx_sync_client()
    sync_client.publish(
        key="grx",
        value={
            "virtual_joystick_axis_left": dynalink_manager.dynalink_grx.virtual_joystick_axis_left,
        }
    )


def callback_button_right_on_click():
    print("Right button clicked.")

    st.session_state.axis_left_value_x += 0.25
    if st.session_state.axis_left_value_x > 1.0:
        st.session_state.axis_left_value_x = 1.0

    dynalink_manager = get_fourier_grx_dynalink_manager()
    dynalink_manager.dynalink_grx.virtual_joystick_axis_left = [
        st.session_state.axis_left_value_x,
        0.0,
    ]

    sync_client = get_fourier_grx_sync_client()
    sync_client.publish(
        key="grx",
        value={
            "virtual_joystick_axis_left": dynalink_manager.dynalink_grx.virtual_joystick_axis_left,
        }
    )


def callback_button_turn_left_on_click():
    print("Turn Left button clicked.")

    st.session_state.axis_right_value_x -= 0.25
    if st.session_state.axis_right_value_x < -1.0:
        st.session_state.axis_right_value_x = -1.0

    dynalink_manager = get_fourier_grx_dynalink_manager()
    dynalink_manager.dynalink_grx.virtual_joystick_axis_right = [
        st.session_state.axis_right_value_x,
        0.0,
    ]

    sync_client = get_fourier_grx_sync_client()
    sync_client.publish(
        key="grx",
        value={
            "virtual_joystick_axis_right": dynalink_manager.dynalink_grx.virtual_joystick_axis_right,
        }
    )


def callback_button_turn_right_on_click():
    print("Turn Right button clicked.")

    st.session_state.axis_right_value_x += 0.25
    if st.session_state.axis_right_value_x > 1.0:
        st.session_state.axis_right_value_x = 1.0

    dynalink_manager = get_fourier_grx_dynalink_manager()
    dynalink_manager.dynalink_grx.virtual_joystick_axis_right = [
        st.session_state.axis_right_value_x,
        0.0,
    ]

    sync_client = get_fourier_grx_sync_client()
    sync_client.publish(
        key="grx",
        value={
            "virtual_joystick_axis_right": dynalink_manager.dynalink_grx.virtual_joystick_axis_right,
        }
    )


def callback_selectbox_on_change():
    print("Selectbox changed.")


def callback_button_run_command_on_click():
    print("Run Command button clicked.")

    selectbox_option = st.session_state.selectbox_option
    robot_task_command = None

    print("selectbox_option:", selectbox_option)

    for task in TaskMenuRobotBase:
        if task.name == selectbox_option:
            robot_task_command = task.value
            break

    for task in TaskMenuHXC:
        if task.name == selectbox_option:
            robot_task_command = task.value
            break

    if robot_task_command is None:
        print("Error: robot_task_command is None. No tasks match with the selectbox_option.")
        return

    dynalink_manager = get_fourier_grx_dynalink_manager()
    dynalink_manager.dynalink_task.robot_task_command = robot_task_command
    dynalink_manager.dynalink_task.flag_task_command_update = True

    sync_client = get_fourier_grx_sync_client()
    sync_client.publish(
        key="task",
        value={
            "robot_task_command": dynalink_manager.dynalink_task.robot_task_command,
            "flag_task_command_update": dynalink_manager.dynalink_task.flag_task_command_update,
        }
    )


def callback_button_emergent_stop_on_click():
    print("Emergent Stop button clicked.")

    dynalink_manager = get_fourier_grx_dynalink_manager()
    dynalink_manager.dynalink_task.robot_task_command = TaskMenuRobotReal.TASK_SERVO_OFF.value
    dynalink_manager.dynalink_task.flag_task_command_update = True

    sync_client = get_fourier_grx_sync_client()
    sync_client.publish(
        key="task",
        value={
            "robot_task_command": dynalink_manager.dynalink_task.robot_task_command,
            "flag_task_command_update": dynalink_manager.dynalink_task.flag_task_command_update,
        }
    )


# --------------------------------------------------


# Add a separate line
st.markdown("---")

# Create a label
st.write("**Joystick Control:**")

joystick_value_column1, \
    joystick_value_column2, \
    joystick_value_column3, \
    joystick_value_column4 \
    = st.columns([1, 1, 1, 1])

with joystick_value_column1:
    st.write(f"joystick_left_x: {st.session_state.axis_left_value_x}")

with joystick_value_column2:
    st.write(f"joystick_left_y: {st.session_state.axis_left_value_y}")

with joystick_value_column3:
    st.write(f"joystick_right_x: {st.session_state.axis_right_value_x}")

with joystick_value_column4:
    st.write(f"joystick_right_y: {st.session_state.axis_right_value_y}")

# Create columns for joystick layout
joystick_column1, \
    joystick_column2, \
    joystick_column3, \
    joystick_column4, \
    joystick_column5 \
    = st.columns([1, 1, 1, 1, 1])

with joystick_column1:
    st.write(" ")
    st.write(" ")
    st.button(label="**Left**", on_click=callback_button_left_on_click)

with joystick_column2:
    st.button(label="**Forward**", on_click=callback_button_forward_on_click)
    st.write(" ")
    st.button(label="**Backward**", on_click=callback_button_backward_on_click)

with joystick_column3:
    st.write(" ")
    st.write(" ")
    st.button(label="**Right**", on_click=callback_button_right_on_click)

with joystick_column4:
    st.write(" ")
    st.write(" ")
    st.button(label="**Turn Left**", on_click=callback_button_turn_left_on_click)

with joystick_column5:
    st.write(" ")
    st.write(" ")
    st.button(label="**Turn Right**", on_click=callback_button_turn_right_on_click)

# Create a label
st.write("**Commands:**")

st.write(f"current state: {get_fourier_grx_dynalink_manager().dynalink_task.robot_task_state}")

# Create columns for selector layout
selector_column_1, \
    selector_column2, \
    selector_column3 \
    = st.columns([2, 1, 1])

with selector_column_1:
    st.session_state.selectbox_option = st.selectbox(
        label="Which command would you like to run?",
        options=[
            TaskMenuRobotReal.TASK_SERVO_OFF.name,
            TaskMenuHXC.TASK_WHOLE_BODY_STAND_CONTROL.name,
            TaskMenuHXC.TASK_WHOLE_BODY_STEER_DRIVE.name,
            TaskMenuHXC.TASK_LEG_BODY_RL_WALK_AIRTIME.name,
            TaskMenuHXC.TASK_LEG_BODY_RL_WALK_CPG.name,
            TaskMenuHXC.TASK_WHOLE_BODY_RL_WALK_CPG.name,
        ],
        on_change=callback_selectbox_on_change,
    )

with selector_column2:
    # add space line
    st.write(" ")
    st.write(" ")
    st.button(label="**Run Command**", on_click=callback_button_run_command_on_click)

with selector_column3:
    # add space line
    st.write(" ")
    st.write(" ")
    st.button(label="**Emergent Stop**", on_click=callback_button_emergent_stop_on_click)

# Add a separate line
st.markdown("---")

st.write("This software is designed to control the Fourier-GRx robot.")
st.write("More information about the Fourier-GRx robot can contact the developer.")

from fourier_core.predefine import *
from fourier_core.config.fi_config import gl_config

from fourier_grx.predefine import *
from fourier_grx.control_system.fi_control_system import (
    ControlSystem,
)
from fourier_grx.sdk.user.task_command import (
    GRXTaskCommand as TaskCommand,
)
from fourier_grx.peripheral import (
    peripheral_joystick as joystick,
    peripheral_keyboard as keyboard,
)

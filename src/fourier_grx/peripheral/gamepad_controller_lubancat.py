import os
import time
import threading
import traceback
import json

from dataclasses import dataclass
from inputs import InputEvent, get_gamepad, devices, UnpluggedError

from fourier_core.logger import *


def remap(value, old_min, old_max, new_min, new_max):
    return (value - old_min) * (new_max - new_min) / (old_max - old_min) + new_min


@dataclass
class Stick:
    x: float = 0
    y: float = 0
    value_range = (0, 255)  # (-32768, 32767)

    def update_x(self, value):
        # map (0, 255) to (-1, 1)
        lower, upper = self.value_range
        if value < lower or value > upper:
            self.value_range = (-32768, 32767)
        self.x = remap(value, lower, upper, -1, 1)
        self.x = round(self.x, 3)  # keep 3 decimation

    def update_y(self, value):
        lower, upper = self.value_range
        if value < lower or value > upper:
            self.value_range = (-32768, 32767)
        self.y = remap(value, lower, upper, -1, 1)
        self.y = round(self.y, 3)  # keep 3 decimation

    def reset(self):
        self.x = 0
        self.y = 0


class Button:
    def __init__(self):
        self.pressed = False

    def is_pressed(self):
        print(f"IS_PRESSED {self.pressed}")
        return self.pressed

    def update(self, value):
        if value == 1:
            self.pressed = True
        elif value == 0:
            self.pressed = False
        else:
            raise ValueError("Button value must be 0 or 1")
        # print(f"UPDATE {self.pressed} {value}")

    def reset(self):
        self.pressed = False


@dataclass(slots=True)
class Trigger:
    value: float = 0.0

    def update(self, value):
        self.value = value

    def reset(self):
        self.value = 0

    def as_button(self, threshold=200):
        return self.value > 200


class GamePadControllerLubancat(threading.Thread):
    def __init__(self):
        super().__init__()
        self.daemon = True
        self.running = True
        self._lock = threading.Lock()
        self._shutdown_flag = threading.Event()

        self.sticks = {
            f"{name}": Stick()
            for name in [
                "left", "right",
            ]
        }

        self.buttons = {
            f"{name}": Button()
            for name in [
                "south", "north", "east", "west",
                "logo", "mode",
                "select", "start",
                "l1", "l2", "r1", "r2",
                "axis_left", "axis_right",
            ]
        }

        self.pad_buttons = {
            f"{name}": Button()
            for name in [
                "left", "right",
                "top", "bottom",
            ]
        }

        self.triggers = {
            f"{name}": Trigger(0)
            for name in [
                "lz", "rz",
            ]
        }

    def stop(self):
        with self._lock:
            """
            Jason 2024-12-27:
            这里的 self.running 用于控制线程的退出，而这里能够保证线程的退出的前提是：
            在 run() 方法中的 events = get_key() 没有阻塞，否则线程无法退出。
            """
            self.running = False

            # reset all states
            self.reset_state()

        self._shutdown_flag.set()

    def run(self):
        while self.running:
            events = None

            try:
                """
                Jason 2025-02-08:
                这里发现一个 bug：
                - 由于是基于事件触发方式，所以在没有事件触发的情况下，该方法不会被调用执行。
                - 但是，实际的手柄还在给对应的 IO 设备发送数据，数据会缓存在对应的接口文件中，当我们 read() 对应的文件时，可能读取到大量的缓存数据。
                - 这样，在一段时间不操作手柄的情况下，再次操作手柄时，会读取到大量的缓存数据，导致程序卡顿。
                """
                events = get_gamepad()

            except UnpluggedError as e:
                # Situations:
                # - gamepad is unplugged: if the gamepad is unplugged when starting the gamepad controller
                Logger().print_warning(f"Gamepad UnpluggedError: {e}")

                self.stop()

            except PermissionError:
                # Situations:
                # - authorization error: if the user does not have permission to access the gamepad device
                if len(devices.gamepads) > 0:
                    device_path = devices.gamepads[0].get_char_device_path()
                else:
                    # print error
                    Logger().print_warning(f"No gamepad device found")
                    device_path = None

                if device_path:
                    Logger().print_info(f"Permission authorization to gamepad device: {device_path}")
                    os.system(f"sudo chmod 666 {device_path}")
                else:
                    pass

            except OSError as e:
                # Situations:
                # - no gamepad found: if no gamepad is connected to device,
                #   happens when the gamepad is disconnected during the gamepad controller is running
                Logger().print_warning(f"Gamepad OSError: {e}")

                self.stop()

            except Exception as e:
                Logger().print_error(e)

                self.stop()

            if events:
                for event in events:
                    match event:
                        case InputEvent(ev_type="Absolute", code="ABS_X", state=state):
                            self.sticks["left"].update_x(state)
                        case InputEvent(ev_type="Absolute", code="ABS_Y", state=state):
                            self.sticks["left"].update_y(state)
                        case InputEvent(ev_type="Absolute", code="ABS_Z", state=state):
                            self.sticks["right"].update_x(state)
                        case InputEvent(ev_type="Absolute", code="ABS_RZ", state=state):
                            self.sticks["right"].update_y(state)

                        case InputEvent(ev_type="Key", code="BTN_SOUTH", state=state):
                            self.buttons["south"].update(state)
                        case InputEvent(ev_type="Key", code="BTN_NORTH", state=state):
                            self.buttons["north"].update(state)
                        case InputEvent(ev_type="Key", code="BTN_EAST", state=state):
                            self.buttons["east"].update(state)
                        case InputEvent(ev_type="Key", code="BTN_TL", state=state):
                            self.buttons["west"].update(state)
                        case InputEvent(ev_type="Key", code="BTN_MODE", state=state):
                            self.buttons["logo"].update(state)
                            self.buttons["mode"].update(state)
                        case InputEvent(ev_type="Key", code="BTN_TL2", state=state):
                            self.buttons["select"].update(state)
                        case InputEvent(ev_type="Key", code="BTN_TR2", state=state):
                            self.buttons["start"].update(state)
                        case InputEvent(ev_type="Key", code="BTN_MODE", state=state):
                            self.buttons["mode"].update(state)
                            self.buttons["logo"].update(state)

                        # l1
                        case InputEvent(ev_type="Key", code="BTN_WEST", state=state):
                            self.buttons["l1"].update(state)
                        # r1
                        case InputEvent(ev_type="Key", code="BTN_Z", state=state):
                            self.buttons["r1"].update(state)
                        # l2
                        case InputEvent(ev_type="Key", code="BTN_TL", state=state):
                            self.buttons["l2"].update(state)
                        # r2
                        case InputEvent(ev_type="Key", code="BTN_TR", state=state):
                            self.buttons["r2"].update(state)

                        # button_axis_left
                        case InputEvent(ev_type="Key", code="BTN_SELECT", state=state):
                            self.buttons["axis_left"].update(state)
                        # button_axis_right
                        case InputEvent(ev_type="Key", code="BTN_START", state=state):
                            self.buttons["axis_right"].update(state)

                        # hat
                        case InputEvent(ev_type="Absolute", code="ABS_HAT0X", state=state):  # -1 is left, 1 is right
                            if state == 0:
                                self.pad_buttons["left"].update(0)
                                self.pad_buttons["right"].update(0)
                            elif state == -1:
                                self.pad_buttons["left"].update(1)
                                self.pad_buttons["right"].update(0)
                            elif state == 1:
                                self.pad_buttons["left"].update(0)
                                self.pad_buttons["right"].update(1)

                        case InputEvent(ev_type="Absolute", code="ABS_HAT0Y", state=state):  # -1 is up, 1 is down
                            if state == 0:
                                self.pad_buttons["top"].update(0)
                                self.pad_buttons["bottom"].update(0)
                            elif state == -1:
                                self.pad_buttons["top"].update(1)
                                self.pad_buttons["bottom"].update(0)
                            elif state == 1:
                                self.pad_buttons["top"].update(0)
                                self.pad_buttons["bottom"].update(1)

                        case InputEvent(ev_type="Absolute", code="ABS_RX", state=state):
                            self.triggers["lz"].update(state)
                        case InputEvent(ev_type="Absolute", code="ABS_RY", state=state):
                            self.triggers["rz"].update(state)

            if self._shutdown_flag.is_set():
                Logger().print_warning("Gamepad controller is shutting down!")
                break

            """
            Jason 2025-02-08:
            - 等待一段时间，不需要太频繁的检查，把 CPU 让给其他线程
            - 每一次的 event 检测通常占用时间为 10^-6s，所以这里设置为 0.001s 即可
            """
            time.sleep(0.001)

    def read(self):
        with self._lock:
            result = {}
            result.update({f"{name}_stick_x": stick.x for name, stick in self.sticks.items()})
            result.update({f"{name}_stick_y": stick.y for name, stick in self.sticks.items()})
            result.update({f"button_{name}": button.pressed for name, button in self.buttons.items()})
            result.update({f"pad_button_{name}": button.pressed for name, button in self.pad_buttons.items()})
            result.update({f"trigger_{name}": trigger.value for name, trigger in self.triggers.items()})
            return result

    def reset_state(self):
        for stick in self.sticks.values():
            stick.reset()

        for button in self.buttons.values():
            button.reset()

        for button in self.pad_buttons.values():
            button.reset()

        for trigger in self.triggers.values():
            trigger.reset()


def main():
    gamepad_controller = GamePadControllerLubancat()
    gamepad_controller.start()

    try:
        while True:
            res = gamepad_controller.read()

            if res:
                print(json.dumps(res, indent=4))

            time.sleep(0.01)

    except KeyboardInterrupt:
        gamepad_controller.stop()


if __name__ == "__main__":
    main()

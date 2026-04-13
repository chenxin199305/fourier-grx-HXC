import os
import time
import threading
import traceback

from inputs import InputEvent, get_key, devices, UnpluggedError

from fourier_core.logger import *


class Key:
    def __init__(self):
        self.state = 0

    def update(self, value):
        self.state = value

    def reset(self):
        self.state = 0

    def is_pressed(self):
        return self.state == 1 or self.state == 2


class KeyboardController(threading.Thread):
    def __init__(self):
        super().__init__()
        self.daemon = True
        self.running = True
        self._lock = threading.Lock()
        self._shutdown_flag = threading.Event()

        self.keys = {
            f"KEY_{name}": Key()
            for name in [
                "UP", "DOWN", "LEFT", "RIGHT",
                "ENTER", "ESC", "SPACE",
                "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8",
                "W", "A", "S", "D", "Q", "E",
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

            # reset all keys state
            self.reset_state()

        self._shutdown_flag.set()

    def run(self):
        while self.running:
            events = None

            try:
                events = get_key()

            except UnpluggedError:
                # Situations:
                # - keyboard is unplugged: if the keyboard is unplugged when starting the keyboard controller
                Logger().print_warning(f"Keyboard is unplugged")

                self.stop()

            except PermissionError:
                # Situations:
                # - authorization error: if the user does not have permission to access the keyboard device
                if len(devices.keyboards) > 0:
                    device_path = devices.keyboards[0].get_char_device_path()
                else:
                    # print error
                    Logger().print_warning("No keyboard device found")
                    device_path = None

                if device_path:
                    Logger().print_info(f"Permission authorization to keyboard device: {device_path}")
                    os.system(f"sudo chmod 666 {device_path}")
                else:
                    pass

            except OSError:
                # Situations:
                # - no keyboard found: if no keyboard is connected to device,
                #   happens when the keyboard is disconnected during the keyboard controller is running
                Logger().print_warning(f"No keyboard device found")

                self.stop()

            except Exception as e:
                Logger().print_error(e)

                self.stop()

            if events:
                for event in events:
                    match event:
                        case InputEvent(ev_type="Key", code="KEY_UP", state=state):
                            self.keys["KEY_UP"].update(state)
                        case InputEvent(ev_type="Key", code="KEY_DOWN", state=state):
                            self.keys["KEY_DOWN"].update(state)
                        case InputEvent(ev_type="Key", code="KEY_LEFT", state=state):
                            self.keys["KEY_LEFT"].update(state)
                        case InputEvent(ev_type="Key", code="KEY_RIGHT", state=state):
                            self.keys["KEY_RIGHT"].update(state)
                        case InputEvent(ev_type="Key", code="KEY_ENTER", state=state):
                            self.keys["KEY_ENTER"].update(state)
                        case InputEvent(ev_type="Key", code="KEY_ESC", state=state):
                            self.keys["KEY_ESC"].update(state)
                        case InputEvent(ev_type="Key", code="KEY_SPACE", state=state):
                            self.keys["KEY_SPACE"].update(state)

                        case InputEvent(ev_type="Key", code="KEY_F1", state=state):
                            self.keys["KEY_F1"].update(state)
                        case InputEvent(ev_type="Key", code="KEY_F2", state=state):
                            self.keys["KEY_F2"].update(state)
                        case InputEvent(ev_type="Key", code="KEY_F3", state=state):
                            self.keys["KEY_F3"].update(state)
                        case InputEvent(ev_type="Key", code="KEY_F4", state=state):
                            self.keys["KEY_F4"].update(state)
                        case InputEvent(ev_type="Key", code="KEY_F5", state=state):
                            self.keys["KEY_F5"].update(state)
                        case InputEvent(ev_type="Key", code="KEY_F6", state=state):
                            self.keys["KEY_F6"].update(state)
                        case InputEvent(ev_type="Key", code="KEY_F7", state=state):
                            self.keys["KEY_F7"].update(state)
                        case InputEvent(ev_type="Key", code="KEY_F8", state=state):
                            self.keys["KEY_F8"].update(state)

                        case InputEvent(ev_type="Key", code="KEY_W", state=state):
                            self.keys["KEY_W"].update(state)
                        case InputEvent(ev_type="Key", code="KEY_A", state=state):
                            self.keys["KEY_A"].update(state)
                        case InputEvent(ev_type="Key", code="KEY_S", state=state):
                            self.keys["KEY_S"].update(state)
                        case InputEvent(ev_type="Key", code="KEY_D", state=state):
                            self.keys["KEY_D"].update(state)
                        case InputEvent(ev_type="Key", code="KEY_Q", state=state):
                            self.keys["KEY_Q"].update(state)
                        case InputEvent(ev_type="Key", code="KEY_E", state=state):
                            self.keys["KEY_E"].update(state)

            if self._shutdown_flag.is_set():
                Logger().print_warning("Keyboard controller is shutting down!")
                break

            # thread sleep for 0.01 second, not need to check too frequently
            time.sleep(0.01)

    def read(self):
        with self._lock:
            result = {}
            result.update({key: key_obj.is_pressed() for key, key_obj in self.keys.items()})
            return result

    def reset_state(self):
        for key in self.keys.values():
            key.reset()


def main():
    """
    Example of using the KeyboardController class.
    1. PermissionError: [Errno 13] Permission denied: '/dev/input/event4'
    2. sudo chmod 666 /dev/input/event4
    """
    keyboard_controller = KeyboardController()
    keyboard_controller.start()
    try:

        while True:
            key = keyboard_controller.read()
            print(key)
            time.sleep(0.01)

    except KeyboardInterrupt:
        keyboard_controller.stop()


if __name__ == "__main__":
    main()

import numpy


def scale_norm_to_range(norm: float, value_range) -> float:
    low = abs(value_range[0].numpy())
    high = abs(value_range[1].numpy())
    return norm * (high if norm >= 0 else low)


def clip_to_range(value: float, value_range) -> float:
    return numpy.clip(
        value,
        value_range[0].numpy(),
        value_range[1].numpy()
    )


class TaskCommonTool:
    @staticmethod
    def read_peripheral_to_x_vel_commands(
            task_model,
    ) -> numpy.array:
        """
        读取外设输入数据，主要是手柄、键盘等输入设备的状态。
        根据输入设备的状态，计算出对应的机器人基座速度命令。

        :param task_model: 任务模型，包含了机器人状态和输入设备的相关信息。
        :return: 返回一个包含基座速度命令的 numpy 数组，格式为 [v_x, v_y, v_yaw]，
        """

        # --------------------------------------------------

        # FIXME 2024-08-07: have bugs when remove this line!!!
        commands = numpy.array([0.0])

        required_attrs = (
            'command_linear_velocity_x_range',
        )
        if not all(hasattr(task_model, a) for a in required_attrs):
            return commands

        x_range = task_model.command_linear_velocity_x_range[0]

        # --------------------------------------------------

        from fourier_grx.peripheral import peripheral_joystick

        if peripheral_joystick is not None:
            joystick = peripheral_joystick

            norm = numpy.array([
                -joystick.axis_left()[1],  # x
            ])

            commands[0] = scale_norm_to_range(norm[0], x_range)

        # --------------------------------------------------

        from fourier_grx.peripheral import peripheral_keyboard

        if peripheral_keyboard is not None:
            keyboard = peripheral_keyboard

            lin_step = 0.25

            if keyboard.key_w.get() and not keyboard.key_s.get():
                commands[0] += lin_step
            if keyboard.key_s.get() and not keyboard.key_w.get():
                commands[0] -= lin_step

        # --------------------------------------------------

        from fourier_grx.peripheral import peripheral_virtual_joystick

        if peripheral_virtual_joystick is not None:
            joystick = peripheral_virtual_joystick

            norm = numpy.array([
                -joystick.axis_left()[1],  # x
            ])

            commands[0] = scale_norm_to_range(norm[0], x_range)

        # --------------------------------------------------

        from fourier_grx.peripheral import peripheral_virtual_keyboard

        if peripheral_virtual_keyboard is not None:
            keyboard = peripheral_virtual_keyboard

            lin_step = 0.25

            if keyboard.key_w.get() and not keyboard.key_s.get():
                commands[0] += lin_step
            if keyboard.key_s.get() and not keyboard.key_w.get():
                commands[0] -= lin_step

        # --------------------------------------------------

        from fourier_grx.peripheral import peripheral_virtual_panel

        if peripheral_virtual_panel is not None:
            commands[0] = peripheral_virtual_panel.command_param_1()

        # --------------------------------------------------

        commands[0] = clip_to_range(commands[0], x_range)

        # --------------------------------------------------

        return commands

    @staticmethod
    def read_peripheral_to_xyyaw_vel_commands(
            task_model,
    ) -> numpy.array:
        """
        读取外设输入数据，主要是手柄、键盘等输入设备的状态。
        根据输入设备的状态，计算出对应的机器人基座速度命令。

        :param task_model: 任务模型，包含了机器人状态和输入设备的相关信息。
        :return: 返回一个包含基座速度命令的 numpy 数组，格式为 [v_x, v_y, v_yaw]，
        """

        # --------------------------------------------------

        # FIXME 2024-08-07: have bugs when remove this line!!!
        commands = numpy.zeros(3, dtype=float)

        required_attrs = (
            'command_linear_velocity_x_range',
            'command_linear_velocity_y_range',
            'command_angular_velocity_yaw_range',
        )
        if not all(hasattr(task_model, a) for a in required_attrs):
            return commands

        x_range = task_model.command_linear_velocity_x_range[0]
        y_range = task_model.command_linear_velocity_y_range[0]
        yaw_range = task_model.command_angular_velocity_yaw_range[0]

        # --------------------------------------------------

        from fourier_grx.peripheral import peripheral_joystick

        if peripheral_joystick is not None:
            joystick = peripheral_joystick

            norm = numpy.array([
                -joystick.axis_left()[1],  # x
                -joystick.axis_left()[0],  # y
                -joystick.axis_right()[0],  # yaw
            ])

            commands[0] = scale_norm_to_range(norm[0], x_range)
            commands[1] = scale_norm_to_range(norm[1], y_range)
            commands[2] = scale_norm_to_range(norm[2], yaw_range)

        # --------------------------------------------------

        from fourier_grx.peripheral import peripheral_keyboard

        if peripheral_keyboard is not None:
            keyboard = peripheral_keyboard

            lin_step = 0.25
            ang_step = 0.25

            if keyboard.key_w.get() and not keyboard.key_s.get():
                commands[0] += lin_step
            if keyboard.key_s.get() and not keyboard.key_w.get():
                commands[0] -= lin_step

            if keyboard.key_a.get() and not keyboard.key_d.get():
                commands[1] += lin_step
            if keyboard.key_d.get() and not keyboard.key_a.get():
                commands[1] -= lin_step

            if keyboard.key_q.get() and not keyboard.key_e.get():
                commands[2] += ang_step
            if keyboard.key_e.get() and not keyboard.key_q.get():
                commands[2] -= ang_step

        # --------------------------------------------------

        from fourier_grx.peripheral import peripheral_virtual_joystick

        if peripheral_virtual_joystick is not None:
            joystick = peripheral_virtual_joystick

            norm = numpy.array([
                -joystick.axis_left()[1],  # x
                -joystick.axis_left()[0],  # y
                -joystick.axis_right()[0],  # yaw
            ])

            commands[0] = scale_norm_to_range(norm[0], x_range)
            commands[1] = scale_norm_to_range(norm[1], y_range)
            commands[2] = scale_norm_to_range(norm[2], yaw_range)

        # --------------------------------------------------

        from fourier_grx.peripheral import peripheral_virtual_keyboard

        if peripheral_virtual_keyboard is not None:
            keyboard = peripheral_virtual_keyboard

            lin_step = 0.25
            ang_step = 0.25

            if keyboard.key_w.get() and not keyboard.key_s.get():
                commands[0] += lin_step
            if keyboard.key_s.get() and not keyboard.key_w.get():
                commands[0] -= lin_step

            if keyboard.key_a.get() and not keyboard.key_d.get():
                commands[1] += lin_step
            if keyboard.key_d.get() and not keyboard.key_a.get():
                commands[1] -= lin_step

            if keyboard.key_q.get() and not keyboard.key_e.get():
                commands[2] += ang_step
            if keyboard.key_e.get() and not keyboard.key_q.get():
                commands[2] -= ang_step

        # --------------------------------------------------

        from fourier_grx.peripheral import peripheral_virtual_panel

        if peripheral_virtual_panel is not None:
            commands[0] = peripheral_virtual_panel.command_param_1()
            commands[1] = peripheral_virtual_panel.command_param_2()
            commands[2] = peripheral_virtual_panel.command_param_3()

        # --------------------------------------------------

        commands[0] = clip_to_range(commands[0], x_range)
        commands[1] = clip_to_range(commands[1], y_range)
        commands[2] = clip_to_range(commands[2], yaw_range)

        # --------------------------------------------------

        return commands

    @staticmethod
    def read_peripheral_to_yaw_commands(
            task_model,
            yaw_commands: float = 0.0,
    ) -> numpy.array:
        """
        读取外设输入数据，主要是手柄、键盘等输入设备的状态。
        根据输入设备的状态，计算出对应的机器人航向角命令。

        :param task_model: 任务模型，包含了机器人状态和输入设备的相关信息。
        :return: 返回一个包含航向角命令的 numpy 数组，格式为 [yaw]，
        """

        commands = yaw_commands

        # --------------------------------------------------

        from fourier_grx.peripheral import peripheral_joystick

        if peripheral_joystick is not None:
            commands_current = peripheral_joystick.hat_left_right.get()
            commands_last = peripheral_joystick.hat_left_right.get_last()

            if commands_current == 1 and commands_last == 0:
                commands -= 0.2
            elif commands_current == -1 and commands_last == 0:
                commands += 0.2
            else:
                pass

        # --------------------------------------------------

        return commands

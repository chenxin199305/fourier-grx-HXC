from fourier_grx.peripheral.value_with_history import ValueWithHistory


class PeripheralVirtualTeleoperation:
    """
    Virtual teleoperation peripheral.

    This class is a singleton class that represents the virtual teleoperation peripheral.
    """

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)

            cls._instance._create_components()

        return cls._instance

    def __str__(self):
        return f"PeripheralVirtualTeleoperation: \n" \
               f"left_handle_pose={self.left_handle_pose}, \n" \
               f"right_handle_pose={self.right_handle_pose}, \n" \
               f"button_left={self.button_left}, \n" \
               f"button_right={self.button_right}"

    def _create_components(self):
        
        self.left_handle_pose = ValueWithHistory((0.185, 0.17565, -0.20999999999999996, 1.0, 0.0, 0.0, 0.0)) # x y z qw qx qy qz
        self.right_handle_pose = ValueWithHistory((0.185, -0.17565, -0.20999999999999996, 1.0, 0.0, 0.0, 0.0)) # x y z qw qx qy qz
        self.head_pose = ValueWithHistory((0.0, 0.0, 0.0))  # roll, pitch, yaw

        self.button_left = ValueWithHistory(0)
        self.button_right = ValueWithHistory(0)


    def update(
            self,
            left_handle_pose: list | None = None,
            right_handle_pose: list | None = None,
            head_pose: list | None = None,
            button_left: int | None = None,
            button_right: int | None = None,
    ):
        """
        Update the joystick status to the peripheral.
        """
        if left_handle_pose is not None:
            self.left_handle_pose.update(left_handle_pose)

        if right_handle_pose is not None:
            self.right_handle_pose.update(right_handle_pose)

        if button_left is not None:
            self.button_left.update(button_left)

        if button_right is not None:
            self.button_right.update(button_right)

        if head_pose is not None:
            self.head_pose.update(head_pose)
from typing import List

from fourier_grx.peripheral.value_with_history import ValueWithHistory


class PeripheralVirtualUser:
    """
    Virtual user peripheral.

    This class is a singleton class that represents the virtual user peripheral.
    """

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)

            cls._instance._create_components()

        return cls._instance

    def __str__(self):
        return (
            f"##################################################\n"
            f"PeripheralVirtualUser: \n"
            f"upper_leg_length_left={self.upper_leg_length_left}, \n"
            f"upper_leg_length_right={self.upper_leg_length_right}, \n"
            f"lower_leg_length_left={self.lower_leg_length_left}, \n"
            f"lower_leg_length_right={self.lower_leg_length_right}, \n"
            f"upper_arm_length_left={self.upper_arm_length_left}, \n"
            f"upper_arm_length_right={self.upper_arm_length_right}, \n"
            f"lower_arm_length_left={self.lower_arm_length_left}, \n"
            f"lower_arm_length_right={self.lower_arm_length_right}, \n"
            f"knee_restriction_left={self.knee_restriction_left}, \n"
            f"knee_restriction_right={self.knee_restriction_right} \n"
            f"##################################################"
        )

    def _create_components(self):
        self.upper_leg_length_left = ValueWithHistory(0.5)
        self.upper_leg_length_right = ValueWithHistory(0.5)
        self.lower_leg_length_left = ValueWithHistory(0.5)
        self.lower_leg_length_right = ValueWithHistory(0.5)
        self.upper_arm_length_left = ValueWithHistory(0.5)
        self.upper_arm_length_right = ValueWithHistory(0.5)
        self.lower_arm_length_left = ValueWithHistory(0.5)
        self.lower_arm_length_right = ValueWithHistory(0.5)

        # 针对康复患者的膝关节限制参数
        self.knee_restriction_left = ValueWithHistory(0.0)
        self.knee_restriction_right = ValueWithHistory(0.0)

    def update(
            self,
            upper_leg_length_left: float = None,
            upper_leg_length_right: float = None,
            lower_leg_length_left: float = None,
            lower_leg_length_right: float = None,
            upper_arm_length_left: float = None,
            upper_arm_length_right: float = None,
            lower_arm_length_left: float = None,
            lower_arm_length_right: float = None,
            knee_restriction_left: float = None,
            knee_restriction_right: float = None,
            **kwargs
    ):
        """
        Update the virtual user peripheral with new values.

        :param upper_leg_length_left: New value for the left upper leg length.
        :param upper_leg_length_right: New value for the right upper leg length.
        :param lower_leg_length_left: New value for the left lower leg length.
        :param lower_leg_length_right: New value for the right lower leg length.
        :param upper_arm_length_left: New value for the left upper arm length.
        :param upper_arm_length_right: New value for the right upper arm length.
        :param lower_arm_length_left: New value for the left lower arm length.
        :param lower_arm_length_right: New value for the right lower arm length.
        :param knee_restriction_left: New value for the left knee restriction.
        :param knee_restriction_right: New value for the right knee restriction.
        """
        if upper_leg_length_left is not None:
            self.upper_leg_length_left.update(upper_leg_length_left)
        if upper_leg_length_right is not None:
            self.upper_leg_length_right.update(upper_leg_length_right)
        if lower_leg_length_left is not None:
            self.lower_leg_length_left.update(lower_leg_length_left)
        if lower_leg_length_right is not None:
            self.lower_leg_length_right.update(lower_leg_length_right)
        if upper_arm_length_left is not None:
            self.upper_arm_length_left.update(upper_arm_length_left)
        if upper_arm_length_right is not None:
            self.upper_arm_length_right.update(upper_arm_length_right)
        if lower_arm_length_left is not None:
            self.lower_arm_length_left.update(lower_arm_length_left)
        if lower_arm_length_right is not None:
            self.lower_arm_length_right.update(lower_arm_length_right)

        if knee_restriction_left is not None:
            self.knee_restriction_left.update(knee_restriction_left)
        if knee_restriction_right is not None:
            self.knee_restriction_right.update(knee_restriction_right)

    def leg_length_left(self) -> float:
        """
        Get the left leg length.
        """
        return self.upper_leg_length_left() + self.lower_leg_length_left()

    def leg_length_right(self) -> float:
        """
        Get the right leg length.
        """
        return self.upper_leg_length_right() + self.lower_leg_length_right()

    def arm_length_left(self) -> float:
        """
        Get the left arm length.
        """
        return self.upper_arm_length_left() + self.lower_arm_length_left()

    def arm_length_right(self) -> float:
        """
        Get the right arm length.
        """
        return self.upper_arm_length_right() + self.lower_arm_length_right()

    def average_upper_leg_length(self) -> float:
        """
        Get the average upper leg length.
        """
        return (self.upper_leg_length_left() + self.upper_leg_length_right()) / 2.0

    def average_lower_leg_length(self) -> float:
        """
        Get the average lower leg length.
        """
        return (self.lower_leg_length_left() + self.lower_leg_length_right()) / 2.0

    def average_upper_arm_length(self) -> float:
        """
        Get the average upper arm length.
        """
        return (self.upper_arm_length_left() + self.upper_arm_length_right()) / 2.0

    def average_lower_arm_length(self) -> float:
        """
        Get the average lower arm length.
        """
        return (self.lower_arm_length_left() + self.lower_arm_length_right()) / 2.0

from fourier_core.config.fi_config import gl_config

from fourier_grx.robot.fi_robot_registry import RobotRegistry


class RobotFactory:
    """
    Robot Factory: to create robot instance from configuration.

    Jason 2026-02-01:
    在软件工程里，一个“工厂”指的是：
    - 一个不表达业务状态、
    - 只负责构造并返回其他对象的组件。
    """
    _robot = None

    def __new__(cls):
        if cls._robot is None:
            robot_cfg = gl_config.parameters["robot"]
            cls._robot = RobotRegistry.create(
                name=robot_cfg["name"],
                backend=robot_cfg.get("backend"),
            )
        return cls._robot

    @classmethod
    def _reset(cls):
        """Reset singleton instance. For testing purposes only."""
        cls._robot = None

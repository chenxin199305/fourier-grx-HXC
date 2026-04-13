class RobotRegistry:
    _registry = {}

    @classmethod
    def register(cls, name, backend=None):
        """
        Decorator to register a robot class with specific attributes.

        Usage:
        @RobotRegistry.register('robot_name', backend='back')
        class MyRobot:
            ...
        """

        def decorator(robot_cls):
            key = (name, backend)
            cls._registry[key] = robot_cls
            return robot_cls

        return decorator

    @classmethod
    def create(cls, name, backend=None):
        key = (name, backend)
        if key not in cls._registry:
            raise ValueError(f"Robot not registered: {key}")
        return cls._registry[key]()

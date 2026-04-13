class TaskRegistry:
    _tasks = {}

    @classmethod
    def register(cls, *robot_types):
        """
        Decorator to register a task class for specific robot types.

        Usage:
        @TaskRegistry.register('robot_type_1', 'robot_type_2')
        class MyTask:
            ...
        """

        def decorator(task_cls):
            for robot_type in robot_types:
                registered = cls._tasks.setdefault(robot_type, [])
                if task_cls not in registered:
                    registered.append(task_cls)
            return task_cls

        return decorator

    @classmethod
    def get_tasks(cls, robot_type):
        return cls._tasks.get(robot_type, [])

# Auto-discover and import all robot_real task modules to trigger @TaskRegistry.register()
# decorators, and re-export their public symbols for explicit imports elsewhere.
# Do NOT manually list imports here — add new task files to this directory instead.
import importlib
import pkgutil

for _importer, _module_name, _is_pkg in pkgutil.iter_modules(__path__):
    if not _module_name.endswith("_base"):
        _mod = importlib.import_module(f"{__name__}.{_module_name}")
        _full_module_name = f"{__name__}.{_module_name}"
        for _name, _obj in vars(_mod).items():
            if not _name.startswith("_") and getattr(_obj, "__module__", None) == _full_module_name:
                globals()[_name] = _obj

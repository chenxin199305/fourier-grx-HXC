# Auto-discover and import all robot_base task modules to trigger @TaskRegistry.register() decorators.
# Do NOT manually list imports here — add new task files to this directory instead.
import importlib
import pkgutil

for _importer, _module_name, _is_pkg in pkgutil.iter_modules(__path__):
    if not _module_name.endswith("_base"):
        importlib.import_module(f"{__name__}.{_module_name}")

# Auto-discover all algorithm modules and re-export their public symbols.
# Do NOT manually list imports here — add new algorithm files to this directory instead.
import importlib
import pkgutil

for _importer, _module_name, _is_pkg in pkgutil.iter_modules(__path__):
    if not _is_pkg:
        _mod = importlib.import_module(f"{__name__}.{_module_name}")
        _full_module_name = f"{__name__}.{_module_name}"
        for _name, _obj in vars(_mod).items():
            if not _name.startswith("_") and getattr(_obj, "__module__", None) == _full_module_name:
                globals()[_name] = _obj

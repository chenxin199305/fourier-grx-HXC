"""
Config validation for fourier-grx.

Call validate_config() early in main() after gl_config is loaded to ensure
required fields are present and have correct types. Fails fast with a clear
error message instead of silently using defaults at unexpected points later.
"""

from fourier_core.config.fi_config import gl_config
from fourier_core.logger import Logger


class ConfigValidationError(RuntimeError):
    """Raised when the loaded config is missing required fields or has invalid values."""
    pass


def _require(params: dict, *keys: str, label: str = "") -> None:
    """Assert a chain of nested keys exists and is not None."""
    node = params
    path = []
    for key in keys:
        path.append(key)
        if not isinstance(node, dict) or key not in node or node[key] is None:
            full_path = ".".join(path)
            prefix = f"[{label}] " if label else ""
            raise ConfigValidationError(
                f"{prefix}Config missing required field: '{full_path}'. "
                f"Please check your config YAML file."
            )
        node = node[key]
    return node


def _warn_if_missing(params: dict, *keys: str, default, label: str = "") -> None:
    """Log a warning when an optional field is absent, showing the default that will be used."""
    node = params
    for key in keys:
        if not isinstance(node, dict) or key not in node:
            full_path = ".".join(keys)
            Logger().print_warning(
                f"Config field '{full_path}' not found, using default: {default!r}"
            )
            return
        node = node[key]


def validate_config() -> None:
    """
    Validate gl_config parameters at startup.

    Raises ConfigValidationError if required fields are missing or invalid.
    Should be called once in main() immediately after gl_config is available.
    """
    params = gl_config.parameters

    if not params:
        raise ConfigValidationError(
            "Config is empty. Please provide a valid config YAML file."
        )

    # --- Required fields ---
    _require(params, "robot", label="robot")
    _require(params, "robot", "name", label="robot")

    robot_name = params["robot"]["name"]
    if not isinstance(robot_name, str) or not robot_name.strip():
        raise ConfigValidationError(
            f"Config field 'robot.name' must be a non-empty string, got: {robot_name!r}"
        )

    # --- control_period validation ---
    control_period = params.get("robot", {}).get("control_period", None)
    if control_period is not None:
        try:
            control_period = float(control_period)
        except (TypeError, ValueError):
            raise ConfigValidationError(
                f"Config field 'robot.control_period' must be a number, got: {control_period!r}"
            )
        if control_period <= 0:
            raise ConfigValidationError(
                f"Config field 'robot.control_period' must be > 0, got: {control_period}"
            )

    # --- Optional field warnings ---
    _warn_if_missing(params, "robot", "backend", default="Real", label="robot")
    _warn_if_missing(params, "mode", default="release")

    Logger().print_debug(
        f"Config validation passed. "
        f"robot.name={robot_name!r}, "
        f"robot.control_period={control_period}"
    )

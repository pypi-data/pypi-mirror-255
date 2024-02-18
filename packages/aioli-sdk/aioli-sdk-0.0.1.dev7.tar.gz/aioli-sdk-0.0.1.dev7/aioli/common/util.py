import functools
import os
import pathlib
import platform
import random
import warnings
from typing import Any, Callable, Optional, TypeVar, Union, cast

T = TypeVar("T")


def sizeof_fmt(val: Union[int, float]) -> str:
    val = float(val)
    for unit in ("", "K", "M", "G", "T", "P", "E", "Z"):
        if abs(val) < 1024.0:
            return "%3.1f%sB" % (val, unit)
        val /= 1024.0
    return "%.1f%sB" % (val, "Y")


def get_default_controller_address() -> str:
    return os.environ.get(
        "AIOLI_CONTROLLER", os.environ.get("AIOLI_CONTROLLER_ADDR", "localhost:8080")
    )


def get_aioli_username_from_env() -> Optional[str]:
    return os.environ.get("AIOLI_USER")


def get_aioli_user_token_from_env() -> Optional[str]:
    return os.environ.get("AIOLI_USER_TOKEN")


def get_aioli_password_from_env() -> Optional[str]:
    return os.environ.get("AIOLI_PASS")


def debug_mode() -> bool:
    return os.getenv("AIOLI_DEBUG", "").lower() in ("true", "1", "yes")


def preserve_random_state(fn: Callable) -> Callable:
    """A decorator to run a function with a fork of the random state."""

    @functools.wraps(fn)
    def wrapped(*arg: Any, **kwarg: Any) -> Any:
        state = random.getstate()
        try:
            return fn(*arg, **kwarg)
        finally:
            random.setstate(state)

    return wrapped


def get_config_path() -> pathlib.Path:
    if os.environ.get("AIOLI_DEBUG_CONFIG_PATH"):
        return pathlib.Path(os.environ["AIOLI_DEBUG_CONFIG_PATH"])

    system = platform.system()
    if "Linux" in system and "XDG_CONFIG_HOME" in os.environ:
        config_path = pathlib.Path(os.environ["XDG_CONFIG_HOME"])
    elif "Darwin" in system:
        config_path = pathlib.Path.home().joinpath("Library").joinpath("Application Support")
    elif "Windows" in system and "LOCALAPPDATA" in os.environ:
        config_path = pathlib.Path(os.environ["LOCALAPPDATA"])
    else:
        config_path = pathlib.Path.home().joinpath(".config")

    return config_path.joinpath("aioli")


U = TypeVar("U", bound=Callable[..., Any])


def deprecated(message: Optional[str] = None) -> Callable[[U], U]:
    def decorator(func: U) -> U:
        @functools.wraps(func)
        def wrapper_deprecated(*args: Any, **kwargs: Any) -> Any:
            warning_message = (
                f"{func.__name__} is deprecated and will be removed in a future version."
            )
            if message:
                warning_message += f" {message}."
            warnings.warn(warning_message, category=DeprecationWarning, stacklevel=2)
            return func(*args, **kwargs)

        return cast(U, wrapper_deprecated)

    return decorator


def prepend_protocol(host: str) -> str:
    # If neither http nor https is specified, supply the default of http.
    if not (host.startswith("http://") or host.startswith("https://")):
        host = f"http://{host}"
    return host

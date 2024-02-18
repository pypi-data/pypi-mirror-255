import os
from pathlib import Path


def env_get_str(key: str, def_value: str = None) -> str:
    """
    Retrieve and return the string value defined for *key* in the current operating environment.

    :param key: The key the value is associated with
    :param def_value: The default value to return, if the key has not been defined
    :return: The str value associated with the key
    """
    result: str
    try:
        result = os.environ[key]
    except (KeyError, TypeError):
        result = def_value

    return result


def env_get_bool(key: str, def_value: bool = None) -> bool:
    """
    Retrieve and return the boolean value defined for *key* in the current operating environment.

    :param key: The key the value is associated with
    :param def_value: The default value to return, if the key has not been defined
    :return: The bool value associated with the key
    """
    result: bool
    try:
        result = bool(os.environ[key])
    except (KeyError, TypeError):
        result = def_value

    return result


def env_get_int(key: str, def_value: int = None) -> int:
    """
    Retrieve and return the int value defined for *key* in the current operating environment.

    :param key: The key the value is associated with
    :param def_value: The default value to return, if the key has not been defined
    :return: The int value associated with the key
    """
    result: int
    try:
        result = int(os.environ[key])
    except (KeyError, TypeError):
        result = def_value

    return result


def env_get_float(key: str, def_value: float = None) -> float:
    """
    Retrieve and return the float value defined for *key* in the current operating environment.

    :param key: The key the value is associated with
    :param def_value: The default value to return, if the key has not been defined
    :return: The float value associated with the key
    """
    result: float
    try:
        result = int(os.environ[key])
    except (KeyError, TypeError):
        result = def_value

    return result


def env_get_path(key: str, def_value: Path = None) -> Path:
    """
    Retrieve and return the path value defined for *key* in the current operating environment.

    :param key: The key the value is associated with
    :param def_value: The default value to return, if the key has not been defined
    :return: The path value associated with the key
    """
    result: Path
    try:
        result = Path(os.environ[key])
    except (KeyError, TypeError):
        result = def_value

    return result


# the prefix to the names of the environment variables
APP_PREFIX = env_get_str("PYPOMES_APP_PREFIX", "PYPOMES")

import base64
from collections.abc import Iterable


def json_normalize_dict(source: dict) -> None:
    """
    Turn the values in *source* into values that can be serialized to JSON, thus avoiding *TypeError*.

    Possible transformations:
        - *bytes* e *bytearray* are changed to *str* in *Base64* format
        - *Iterable* is changed into a *list*
        - all other types are left unchanged
    HAZARD: depending on the type of object contained in *source*, the final result may not be serializable.

    :param source: the dict to be made serializable
    """
    for key, value in source.items():
        if isinstance(value, dict):
            json_normalize_dict(value)
        elif isinstance(value, bytes | bytearray):
            source[key] = base64.b64encode(value).decode()
        elif isinstance(value, Iterable) and not isinstance(value, str):
            source[key] = json_normalize_iterable(value)


def json_normalize_iterable(source: Iterable) -> list[any]:
    """
    Return in a *list* the values in *source* that can be serialized to JSON, thus avoiding *TypeError*.

    Possible operations:
        - *bytes* e *bytearray* are changed to *str* in *Base64* format
        - *Iterable* is changed into a *list*
        - all other types are left unchanged
    HAZARD: depending on the type of object contained in *source*, the final result may not be serializable.

    :param source: the dict to be made serializable
    :return: list with serialized values
    """
    result: list[any] = []
    for value in source:
        if isinstance(value, dict):
            json_normalize_dict(value)
            result.append(value)
        elif isinstance(value, bytes | bytearray):
            result.append(base64.b64encode(value).decode())
        elif isinstance(value, Iterable) and not isinstance(value, str):
            result.append(json_normalize_iterable(value))
        else:
            result.append(value)

    return result

from flask import Request
from pathlib import Path
from tempfile import gettempdir
from typing import Final
from werkzeug.datastructures import FileStorage
from .env_pomes import APP_PREFIX, env_get_path

TEMP_DIR: Final[Path] = env_get_path(f"{APP_PREFIX}_TEMP_DIR", Path(gettempdir()))


def file_from_request(request: Request, file_name: str = None, file_seq: int = 0) -> bytes:
    """
    Retrieve and return the contents of the file returned in the response to a request.

    The file may be referred to by its name (*file_name*), or if no name is specified,
    by its sequence number (*file_seq*).

    :param request: the request
    :param file_name: optional name for the file
    :param file_seq:  sequence number for the file, defaults to the first file
    :return: the contents retrieved from the file
    """
    # inicialize the return variable
    result: bytes | None = None

    count: int = len(request.files)
    # has a file been found ?
    if count > 0:
        # yes, retrieve it
        file: FileStorage | None = None
        if isinstance(file_name, str):
            file = request.files.get(file_name)
        elif isinstance(file_seq, int) and file_seq >= 0:
            file_in: str = list(request.files)[file_seq]
            file = request.files[file_in]

        if file:
            result: bytes = file.stream.read()

    return result

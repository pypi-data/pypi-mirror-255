import json
import logging
from datetime import datetime
from dateutil import parser
from flask import Request, Response, send_file
from io import BytesIO
from pathlib import Path
from typing import Final, Literal, TextIO
from .datetime_pomes import DATETIME_FORMAT_INV
from .env_pomes import APP_PREFIX, env_get_str, env_get_path
from .file_pomes import TEMP_DIR


def __get_logging_level(level: Literal["debug", "info", "warning", "error", "critical"]) -> int:
    """
    Translate the log severity string *level* into the logging's internal severity value.

    :param level: the string log severity
    :return: the internal logging severity value
    """
    result: int | None
    match level:
        case "debug":
            result = logging.DEBUG          # 10
        case "info":
            result = logging.INFO           # 20
        case "warning":
            result = logging.WARN           # 30
        case "error":
            result = logging.ERROR          # 40
        case "critical":
            result = logging.CRITICAL       # 50
        case _:
            result = logging.NOTSET         # 0

    return result


LOGGING_ID: Final[str] = env_get_str(f"{APP_PREFIX}_LOGGING_ID", f"{APP_PREFIX}")
LOGGING_FORMAT: Final[str] = env_get_str(f"{APP_PREFIX}_LOGGING_FORMAT",
                                         "{asctime} {levelname:1.1} {thread:5d} "
                                         "{module:20.20} {funcName:20.20} {lineno:3d} {message}")
LOGGING_STYLE: Final[str] = env_get_str(f"{APP_PREFIX}_LOGGING_STYLE", "{")

LOGGING_FILE_PATH: Final[Path] = env_get_path(f"{APP_PREFIX}_LOGGING_FILE_PATH",
                                              TEMP_DIR / f"{APP_PREFIX}.log")
LOGGING_FILE_MODE: Final[str] = env_get_str(f"{APP_PREFIX}_LOGGING_FILE_MODE", "a")

# define and configure the logger
PYPOMES_LOGGER: Final[logging.Logger] = logging.getLogger(LOGGING_ID)

# define the logging severity level
# noinspection PyTypeChecker
LOGGING_LEVEL: Final[int] = __get_logging_level(env_get_str(f"{APP_PREFIX}_LOGGING_LEVEL"))

# configure the logger
# noinspection PyTypeChecker
logging.basicConfig(filename=LOGGING_FILE_PATH,
                    filemode=LOGGING_FILE_MODE,
                    format=LOGGING_FORMAT,
                    datefmt=DATETIME_FORMAT_INV,
                    style=LOGGING_STYLE,
                    level=LOGGING_LEVEL)
for _handler in logging.root.handlers:
    _handler.addFilter(logging.Filter(LOGGING_ID))


def logging_request_entries(request: Request, as_attachment: bool = False) -> Response:
    """
    Retrieve from the log file, and return, the entries matching the criteria specified.

    These criteria are specified in the query string of the HTTP request, according to the pattern
    *path=<log-path>&level=<log-level>&from=YYYYMMDDhhmmss&to=YYYYMMDDhhmmss>*

    All criteria are optional:
        - path: the path of the log file
        - level: the logging level of the entries
        - from: the start timestamp
        - to: the finish timestamp

    :param request: the HTTP request
    :param as_attachment: indicate to browser that it should offer to save the file, or just display it
    :return: file containing the log entries requested on success, or incidental errors on fail
    """
    # declare the return variable
    result: Response

    # initialize the error messages list
    errors: list[str] = []

    # obtain the logging level
    log_level: str = request.args.get("level")

    # obtain the initial and final timestamps
    log_from: str = request.args.get("from")
    log_to: str = request.args.get("to")

    # obtain the path for the log file
    log_path: str = request.args.get("path") or LOGGING_FILE_PATH

    # retrieve the log entries
    # noinspection PyTypeChecker
    log_entries: BytesIO = logging_get_entries(errors, log_level, log_from, log_to, log_path)

    # any error ?
    if len(errors) == 0:
        # no, return the log entries requested as an attached file
        base: str = "entries" if not log_from or not log_to else \
            (
                f"{''.join(ch for ch in log_from if ch.isdigit())}"
                f"{'_'.join(ch for ch in log_to if ch.isdigit())}"
            )
        log_file = f"log_{base}.log"
        log_entries.seek(0)
        result = send_file(path_or_file=log_entries,
                           mimetype="text/plain",
                           as_attachment=as_attachment,
                           download_name=log_file)
    else:
        # yes, report the failure
        result = Response(json.dumps({"errors": errors}), status=401,  mimetype="text/plain")

    return result


def logging_get_entries(errors: list[str],
                        log_level:  Literal["debug", "info", "warning", "error", "critical"] = None,
                        log_from: str = None, log_to: str = None,
                        log_path: Path | str = LOGGING_FILE_PATH) -> BytesIO:
    """
    Extract and return all entries in the logging file *file_path*.

    It is expected for this logging file to be compliant with *PYPOMES_LOGGER*'s default format.
    The extraction meets the criteria specified by *log_level*, and by the inclusive interval *[log_from, log_to]*.

    :param errors: incidental error messages
    :param log_level: the logging level (defaults to all levels)
    :param log_from: the initial timestamp (defaults to unspecified)
    :param log_to: the finaL timestamp (defaults to unspecified)
    :param log_path: the path of the log file
    :return: the logging entries meeting the specified criteria
    """
    # inicializa variável de retorno
    result: BytesIO | None = None

    # obtain the logging level
    # noinspection PyTypeChecker
    logging_level: int = __get_logging_level(log_level)

    # obtain the initial timestamp
    from_stamp: datetime | None = None
    if log_from:
        from_stamp = parser.parse(log_from)
        if not from_stamp:
            errors.append(f"Value '{from_stamp}' of 'log_from' attribute invalid")

    # obtain the final timestamp
    to_stamp: datetime | None = None
    if log_to:
        to_stamp = parser.parse(log_to)
        if not to_stamp or \
           (from_stamp and from_stamp > to_stamp):
            errors.append(f"Value '{to_stamp}' of 'log_to' attribute invalid")

    file_path: Path = Path(log_path)
    # does the log file exist ?
    if not Path.exists(file_path):
        # no, report the error
        errors.append(f"File '{file_path}' not found")

    # any error ?
    if len(errors) == 0:
        # no, proceed
        result = BytesIO()
        with Path.open(file_path) as f:
            line: str = f.readline()
            while line:
                items: list[str] = line.split(maxsplit=3)
                # noinspection PyTypeChecker
                msg_level: int = __get_logging_level(items[2])
                if msg_level >= logging_level:
                    timestamp: datetime = parser.parse(f"{items[0]} {items[1]}")
                    if (not from_stamp or timestamp >= from_stamp) and \
                       (not to_stamp or timestamp <= to_stamp):
                        result.write(line.encode())
                line = f.readline()

    return result


def logging_log_msgs(msgs: list[str], output_dev: TextIO = None,
                     log_level: Literal["debug", "info", "warning", "error", "critical"] = "error",
                     logger: logging.Logger = PYPOMES_LOGGER) -> None:
    """
    Write all messages in *msgs* to *logger*'s logging file, and to *output_dev*.

    The output device is tipically *sys.stdout* or *sys.stderr*.

    :param msgs: the messages list
    :param output_dev: output device where the message is to be printed (None for no device printing)
    :param log_level: the logging level, defaults to 'error' (None for no logging)
    :param logger: the logger to use
    """
    # define the log writer
    log_writer: callable = None
    match log_level:
        case "debug":
            log_writer = logger.debug
        case "info":
            log_writer = logger.info
        case "warning":
            log_writer = logger.warning
        case "error":
            log_writer = logger.error
        case "critical":
            log_writer = logger.critical

    # traverse the messages list
    for msg in msgs:
        # has the log writer been defined ?
        if log_writer:
            # yes, log the message
            log_writer(msg)

        # has the output device been defined ?
        if output_dev:
            # yes, write the message to it
            output_dev.write(msg)

            # is the output device 'stderr' ou 'stdout' ?
            if output_dev.name.startswith("<std"):
                # yes, skip to the next line
                output_dev.write("\n")

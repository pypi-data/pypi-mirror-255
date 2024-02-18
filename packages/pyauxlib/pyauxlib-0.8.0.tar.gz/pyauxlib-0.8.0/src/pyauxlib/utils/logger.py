"""Logging functions."""
import logging
import logging.handlers
from datetime import datetime, timezone
from pathlib import Path

from pyauxlib.io.filesfolders import create_folder


def _set_level(level: int | str | None, default_level: int | str = "INFO") -> int:
    """Return a correct logging level value.

    This function takes a logging level as input, which can be either an integer, a string, or None.
    If the level is a string, it should be one of the following:
        ['CRITICAL', 'FATAL', 'ERROR', 'WARN', 'WARNING', 'INFO', 'DEBUG', 'NOTSET'].
    Note that lower case letters can also be used.

    If the level is None , the function will return the default_level.

    Parameters
    ----------
    level : int | str | None
        level of the logger, by "INFO"
        Any of the levels of logging can be passed as a string:
        ['CRITICAL', 'FATAL', 'ERROR', 'WARN', 'WARNING', 'INFO', 'DEBUG', 'NOTSET']
        Note that lower case letters can also be used
    default_level : int | str, optional
        default level in case that `level` is incorrect, by default "INFO"

    Returns
    -------
    int
        The numeric value of the logging level.

    Raises
    ------
    TypeError
        If `level` is not None, a string, or an integer.
    ValueError
        If `level` is a string but not a valid logging level.
    """
    if level is not None and not isinstance(level, (str | int)):
        raise TypeError

    if level is None:
        return _set_level(default_level)
    if isinstance(level, str):
        level_upper = level.upper()
        if level_upper not in logging._nameToLevel:  # noqa: SLF001
            error_msg = f"Invalid logging level: {level}"
            raise ValueError(error_msg)
        return int(logging.getLevelName(level.upper()))

    return level


def init_logger(  # noqa: PLR0913
    name: str,
    level: int | str = "INFO",
    level_console: int | str | None = None,
    level_file: int | str | None = None,
    output_folder: Path | None = None,
    file_size: int = 0,
    propagate: bool = False,
    output_console: bool = True,
    output_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
) -> logging.Logger:
    """Initialize the logger.

    Parameters
    ----------
    name : str
        name of the logger
    level : int | str, optional
        level of the logger, by default "INFO"
        Any of the levers of logging can be passed as a string:
        ['CRITICAL', 'FATAL', 'ERROR', 'WARN', 'WARNING', 'INFO', 'DEBUG', 'NOTSET']
        Note that lower case letters can also be used
    level_console : int | str | None, optional
        level of the console logger, by default None
    level_file : int | str | None, optional
        level of the file logger, by default None
    output_folder : Path, optional
        folder to output the log, by default None
    file_size : int, optional
        maximum size of the output file in bytes, by default 0 (=unlimited size)
    propagate : bool, optional
        the log messages are passed or not to the parent logger, by default False
    output_console : bool, optional
        output the log to the console, by default True
    output_format : str, optional
        format of the output

    Returns
    -------
    logging.Logger
        logger
    """
    # FIXME Need some way to handle if the passed level string is not correct
    level = _set_level(level)

    level_console = _set_level(level_console, default_level=level)
    level_file = _set_level(level_file, default_level=level)

    level = min([level, level_console, level_file])

    formatter = logging.Formatter(output_format)

    handler_list: list[logging.Handler] = []
    if output_folder is not None:
        # Timestamp for the log file name
        create_folder(output_folder, includes_file=False)
        timestamp = datetime.now(tz=timezone.utc).astimezone().strftime("%Y%m%d_%H%M%S")
        output_file_with_timestamp = output_folder / f"{timestamp}.log"

        file_handler = logging.handlers.RotatingFileHandler(
            filename=output_file_with_timestamp, maxBytes=file_size, backupCount=5
        )
        file_handler.setLevel(level_file)
        file_handler.setFormatter(formatter)
        handler_list.append(file_handler)

    if output_console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level_console)
        console_handler.setFormatter(formatter)
        handler_list.append(console_handler)

    logger = logging.getLogger(name)

    # ??? Do I need to set the basicConfig for the root logger?
    # Check if the parent is the root logger
    """# if logger.parent == logging.getLogger():
    #     logging.basicConfig(
    #         level=level,
    #         # format=output_format,
    #         handlers=handler_list,
    #     )

    # logger = logging.getLogger(name)"""

    logger.setLevel(level=level)
    logger.propagate = propagate
    for handler in handler_list:
        logger.addHandler(handler)
    return logger

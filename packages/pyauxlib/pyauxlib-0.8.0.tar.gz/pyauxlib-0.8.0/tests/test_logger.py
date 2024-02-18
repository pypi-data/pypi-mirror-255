"""Test for the logger."""
import logging
import shutil
from collections.abc import Generator
from pathlib import Path
from typing import Any

import pytest
from pyauxlib.utils.logger import init_logger

LOGS_PATH = Path("test_logs")


def test_init_logger() -> None:
    """Test the logger."""
    # Test without output file
    logger = init_logger("test_logger", "DEBUG")
    assert logger.name == "test_logger"
    assert logger.level == logging.DEBUG
    assert any(isinstance(handler, logging.StreamHandler) for handler in logger.handlers)
    assert not any(isinstance(handler, logging.FileHandler) for handler in logger.handlers)

    # Test with output file
    logger = init_logger("test_logger_file", "DEBUG", output_folder=LOGS_PATH)
    assert logger.name == "test_logger_file"
    assert logger.level == logging.DEBUG
    assert any(isinstance(handler, logging.StreamHandler) for handler in logger.handlers)
    assert any(isinstance(handler, logging.FileHandler) for handler in logger.handlers)

    # Close the handlers in order to later remove the log folder
    for handler in logger.handlers:
        handler.close()
        logger.removeHandler(handler)


def test_init_logger_file_output() -> None:
    """Test the logger file output."""
    logger = init_logger(
        "test_logger_file_output", "DEBUG", level_file="INFO", output_folder=LOGS_PATH
    )
    test_message = "This is a test message"
    logger.info(test_message)
    test_message_not_shown = "This won't be in the file"
    logger.debug(test_message_not_shown)

    # Close the handlers in order to later read the log file
    filenames = []
    for handler in logger.handlers:
        if isinstance(handler, logging.FileHandler):
            filenames.append(handler.baseFilename)
        handler.close()
        logger.removeHandler(handler)

    # Check if the message is in the log file
    for filename in filenames:
        with Path.open(Path(filename), "r") as f:
            log_content = f.read()
        assert test_message in log_content
        assert test_message_not_shown not in log_content


def test_init_logger_console_output(capfd: Any) -> None:
    """Test the logger console output."""
    logger = init_logger("test_logger_console_output", "DEBUG", level_console="INFO")
    test_message = "This is a test message"
    logger.info(test_message)
    test_message_not_shown = "This won't be in the in the output"
    logger.debug(test_message_not_shown)

    # Capture the stdout and stderr output
    captured = capfd.readouterr()
    assert test_message in captured.err
    assert test_message_not_shown not in captured.err


@pytest.fixture(autouse=True)
def _cleanup() -> Generator[None, None, None]:
    """Run after each test and clean up the folder of logs."""
    yield

    # Delete log folder for tests
    shutil.rmtree(LOGS_PATH, ignore_errors=True)

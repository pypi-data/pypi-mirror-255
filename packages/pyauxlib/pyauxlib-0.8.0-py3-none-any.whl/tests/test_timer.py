"""Tests for `pyauxlib.utils.timer`."""
import io
import logging
import time

import pytest
from pyauxlib.decorators import timer
from pyauxlib.utils.timer import Timer


def _check_attributes(timer: Timer, attributes: list[str], error_message: str) -> None:
    """Check that each attr in a list raises an AttributeError with a given error message.

    Parameters
    ----------
    timer : Timer
        The Timer instance to check.
    attributes : list of str
        The names of the attributes to check.
    error_message : str
        The error message that should be raised when an attribute is accessed.

    Raises
    ------
    AssertionError
        If an attribute does not raise an AttributeError with the given error message when accessed.
    """
    for attribute in attributes:
        with pytest.raises(AttributeError, match=error_message):
            _ = getattr(timer, attribute)


def test_timer_getattr() -> None:
    """Test the attributes of Timer related with start, stop and elapsed times."""
    timer = Timer()
    attributes = ["start_time", "stop_time", "elapsed_time"]

    # Test that attributes are not set before start() is called
    _check_attributes(timer, attributes, "is not set. Please start the timer first.")

    # Test that stop_time and elapsed_time are not set even after start() is called
    timer.start()
    _check_attributes(
        timer, ["stop_time", "elapsed_time"], "is not set. Please stop the timer first."
    )

    # Test that all attributes are set after stop() is called
    timer.stop()
    for attribute in attributes:
        assert hasattr(timer, attribute), f"{attribute} is not set after stop() is called"

    # Test that all attributes are removed after reset() is called
    timer.reset()
    _check_attributes(timer, attributes, "is not set. Please start the timer first.")


def test_timer() -> None:
    """Test the manual usage of the Timer."""
    # Test initialization
    logger = logging.getLogger(__name__)
    timer = Timer(logger=logger)
    assert timer.filename is None
    assert timer.time_func == time.time
    assert isinstance(timer.logger, logging.Logger)
    assert timer.where_output is not None
    assert timer.running is False

    # Test start and stop
    timer.start()
    assert timer.running is True
    assert hasattr(timer, "start_time")  # type: ignore[unreachable]
    time.sleep(1)  # wait for 1 second to ensure the elapsed time is non-zero
    elapsed_time = timer.stop()
    assert timer.running is False
    assert hasattr(timer, "stop_time")
    assert elapsed_time > 0

    # Test reset
    timer.reset()
    assert not hasattr(timer, "start_time")
    assert not hasattr(timer, "stop_time")


def test_timer_context_manager() -> None:
    """Test the context manager usage."""
    with Timer() as t:
        time.sleep(1)  # wait for 1 second to ensure the elapsed time is non-zero
        t.add_timestamp("#1")
    assert hasattr(t, "stop_time")


def test_timer_as_decorator() -> None:
    """Test the usage of Timer as a decorator."""
    # Decorator usage
    timer_instance = Timer()

    @timer_instance
    def some_function() -> None:
        time.sleep(1)  # wait for 1 second to ensure the elapsed time is non-zero

    some_function()
    assert hasattr(timer_instance, "stop_time")


def test_timer_decorator(caplog: pytest.LogCaptureFixture) -> None:
    """Test the timer decorator usage."""
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    @timer(logger=logger)
    def some_function() -> None:
        time.sleep(1)  # wait for 1 second to ensure the elapsed time is non-zero

    with caplog.at_level(logging.INFO):
        some_function()

    assert "Elapsed time:" in caplog.text


def test_timer_logging() -> None:
    """Test the logging of elapsed time in Timer."""
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    stream_handler = logging.StreamHandler(stream=io.StringIO())
    logger.addHandler(stream_handler)

    timer_instance = Timer(logger=logger)
    timer_instance.start()
    time.sleep(1)  # wait for 1 second to ensure the elapsed time is non-zero
    timer_instance.stop()

    log_output = stream_handler.stream.getvalue()

    assert "Elapsed time:" in log_output

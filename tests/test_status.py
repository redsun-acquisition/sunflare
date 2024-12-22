import pytest

from sunflare.engine.status import Status
from sunflare.engine._exceptions import StatusTimeoutError, InvalidState, WaitTimeoutError
from time import sleep

def test_status() -> None:

    def callback(_: Status) -> None:
        # Simulate a task
        sleep(0.5)

    status = Status()

    assert status.timeout is None
    assert status.settle_time == 0.0
    assert status.done is False

    status.add_callback(callback)

    assert len(status.callbacks) == 1

    status.set_finished()

    while not status.done:
        ...

    assert status.done is True # type: ignore
    assert status.success is True

def test_status_wrong_external_exception() -> None:
    status = Status()
    status.set_exception(Exception("Test exception"))

    with pytest.raises(InvalidState):
        # finishing twice raises invalid state
        status.set_exception(Exception("Can't call set exception twice"))

def test_status_false_exception() -> None:
    status = Status()
    with pytest.raises(Exception):
        status.set_exception("This is not an exception") # type: ignore
    assert status.done is False
    assert status.success is False

def test_status_timeout() -> None:

    status = Status(timeout=0.1)

    # cause a timeout
    sleep(0.5)
    assert isinstance(status.exception(), StatusTimeoutError)

    status = Status(timeout=0.3)

    # what happens if we set StatusTimeoutError as the exception?
    with pytest.raises(ValueError):
        status.set_exception(StatusTimeoutError) # type: ignore

def test_status_set_exception_after_timeout() -> None:
    status = Status(timeout=0.1)
    sleep(0.5)
    status.set_exception(Exception("Test exception"))
    assert isinstance(status.exception(), StatusTimeoutError)

def test_status_callback_after_finished() -> None:

    def post_callback(status: Status) -> None:
        assert status.done is True

    status = Status()
    status.set_finished()

    while not status.done:
        ...

    status.add_callback(post_callback)
    assert status.done is True
    assert status.success is True

def test_status_wait_timeout() -> None:
    status = Status()

    with pytest.raises(WaitTimeoutError):
        status.wait(timeout=0.1)

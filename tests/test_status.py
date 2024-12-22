from sunflare.engine.status import Status
from time import sleep

def test_status():

    def callback(s: Status):
        # Simulate a task
        sleep(0.5)

    status = Status()

    assert status.timeout is None
    assert status.settle_time == 0.0
    assert status.done is False

    status.add_callback(callback)
    status.set_finished()

    while not status.done:
        ...

    assert status.done is True
    assert status.success is True

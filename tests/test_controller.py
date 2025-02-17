import time
from pathlib import Path
from typing import cast

import zmq

from mocks import MockController, MockControllerInfo

from sunflare.model import ModelProtocol
from sunflare.config import ControllerInfo, RedSunSessionInfo
from sunflare.virtual import VirtualBus
from sunflare.controller import SyncPublisher, SyncSubscriber, SyncPubSub


def test_controller(config_path: Path, bus: VirtualBus) -> None:
    config_file = config_path / "controller_instance.yaml"

    config = RedSunSessionInfo.load_yaml(str(config_file))
    config_ctrl: dict[str, ControllerInfo] = {
        name: MockControllerInfo(**input)
        for name, input in config["controllers"].items()
    }

    assert len(config_ctrl) == 1

    for _, ctrl in config_ctrl.items():
        controller = MockController(cast(MockControllerInfo, ctrl), bus)
        assert controller.info == ctrl
        assert len(controller.plans) == 2
        assert controller.info.plugin_name == "N/A"
        assert controller.info.repository == "N/A"

def test_sync(bus: VirtualBus) -> None:

    class TestPublisher(SyncPublisher):
        def __init__(self, info: ControllerInfo, models: dict[str, ModelProtocol], virtual_bus: VirtualBus) -> None:
            super().__init__(virtual_bus)
            self.info = info
            self.models = models
            self.virtual_bus = virtual_bus

        def registration_phase(self):
            ...

        def connection_phase(self):
            ...


    class TestSubscriber(SyncSubscriber):
        def __init__(self, info: ControllerInfo, models: dict[str, ModelProtocol], virtual_bus: VirtualBus) -> None:
            super().__init__(virtual_bus, "test")
            self.info = info
            self.virtual_bus = virtual_bus
            self.msg_queue: list[tuple[str, ...]] = []

        def consume(self, content: list[bytes]) -> None:
            self.msg_queue.append(tuple(c.decode() for c in content))

        def registration_phase(self):
            ...

        def connection_phase(self):
            ...


    pub_info = ControllerInfo()
    sub_info = ControllerInfo()
    pub = TestPublisher(pub_info, {}, bus)
    sub = TestSubscriber(sub_info, {}, bus)

    # wait for the startup
    time.sleep(0.1)

    assert pub.pub_socket is not None, "Publisher socket not initialized"
    assert pub.pub_socket.getsockopt(zmq.TYPE) == zmq.PUB, "Publisher socket not of type PUB"

    assert sub.sub_socket is not None, "Subscriber socket not initialized"
    assert sub.sub_socket.getsockopt(zmq.TYPE) == zmq.SUB, "Subscriber socket not of type SUB"
    assert sub.sub_thread.is_alive(), "Consumer thread not started"

    pub.pub_socket.send_multipart([b"test", b"message"])
    pub.pub_socket.send_multipart([b"other-topic", b"message"])

    bus.shutdown()

    # wait for cleanup
    time.sleep(0.1)

    assert not sub.sub_thread.is_alive(), "Subscriber thread not terminated"
    assert len(sub.msg_queue) == 1, "Subscriber received more than one message or no message"
    assert sub.msg_queue == [("test", "message")], "Subscriber did not receive message"

def test_sync_single_class(bus: VirtualBus) -> None:
    class TestController(SyncPubSub):
        def __init__(self, info: ControllerInfo, models: dict[str, ModelProtocol], virtual_bus: VirtualBus) -> None:
            super().__init__(virtual_bus, "test")
            self.info = info
            self.models = models
            self.virtual_bus = virtual_bus
            self.msg_queue: list[tuple[str, ...]] = []

        def consume(self, content: list[bytes]) -> None:
            self.msg_queue.append(tuple(c.decode() for c in content))
            

    pub_sub_info = ControllerInfo()
    pub_sub = TestController(pub_sub_info, {}, bus)

    # wait for the startup
    time.sleep(0.1)

    assert pub_sub.pub_socket is not None, "Publisher socket not initialized"
    assert pub_sub.pub_socket.getsockopt(zmq.TYPE) == zmq.PUB, "Publisher socket not of type PUB"
    assert pub_sub.sub_socket is not None, "Subscriber socket not initialized"
    assert pub_sub.sub_socket.getsockopt(zmq.TYPE) == zmq.SUB, "Subscriber socket not of type SUB"
    assert pub_sub.sub_thread.is_alive(), "Consumer thread not started"

    pub_sub.pub_socket.send_multipart([b"test", b"message"])
    pub_sub.pub_socket.send_multipart([b"other-topic", b"message"])

    bus.shutdown()

    # wait for cleanup
    time.sleep(0.1)

    assert not pub_sub.sub_thread.is_alive(), "Subscriber thread not terminated"
    assert len(pub_sub.msg_queue) == 1, "Subscriber received more than one message or no message"
    assert pub_sub.msg_queue == [("test", "message")], "Subscriber did not receive message"

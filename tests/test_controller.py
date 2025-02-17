import time
import asyncio
import queue
from pathlib import Path
from typing import cast

import zmq

from mocks import MockController, MockControllerInfo

from sunflare.model import ModelProtocol
from sunflare.config import ControllerInfo, RedSunSessionInfo
from sunflare.virtual import VirtualBus
from sunflare.controller import Publisher, SyncSubscriber, AsyncSubscriber


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

    def retrieve_messages(q: queue.Queue) -> list[tuple[str, ...]]:
        messages: list[tuple[str, ...]] = []
        try:
            messages.append(q.get(block=False))
        except queue.Empty:
            pass
        return messages

    class TestPublisher(Publisher):
        def __init__(self, info: ControllerInfo, models: dict[str, ModelProtocol], virtual_bus: VirtualBus) -> None:
            super().__init__(virtual_bus)
            self.info = info
            self.models = models
            self.virtual_bus = virtual_bus


    class TestSubscriber(SyncSubscriber):
        def __init__(self, info: ControllerInfo, models: dict[str, ModelProtocol], virtual_bus: VirtualBus) -> None:
            super().__init__(virtual_bus, "test")
            self.info = info
            self.virtual_bus = virtual_bus
            self.msg_queue: queue.Queue[tuple[str, ...]] = queue.Queue()

        def consume(self, content: list[bytes]) -> None:
            self.msg_queue.put(tuple(c.decode() for c in content))


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

    # check the received messages
    messages = retrieve_messages(sub.msg_queue)

    assert len(messages) == 1, "Subscriber received more than one message or no message"
    assert messages == [("test", "message")], "Subscriber did not receive message"

def test_sync_single_class(bus: VirtualBus) -> None:

    def retrieve_messages(q: queue.Queue) -> list[tuple[str, ...]]:
        messages: list[tuple[str, ...]] = []
        try:
            messages.append(q.get(block=False))
        except queue.Empty:
            pass
        return messages

    class TestController(Publisher, SyncSubscriber):
        def __init__(self, ctrl_info: ControllerInfo, models: dict[str, ModelProtocol], virtual_bus: VirtualBus) -> None:
            Publisher.__init__(self, virtual_bus)
            SyncSubscriber.__init__(self, virtual_bus, "test")
            self.ctrl_info = ctrl_info
            self.models = models
            self.virtual_bus = virtual_bus
            self.msg_queue: queue.Queue[tuple[str, ...]] = queue.Queue()

        def consume(self, content: list[bytes]) -> None:
            self.msg_queue.put(tuple(c.decode() for c in content))
            

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

    # check the received messages
    messages = retrieve_messages(pub_sub.msg_queue)

    assert len(messages) == 1, "Subscriber received more than one message or no message"
    assert messages == [("test", "message")], "Subscriber did not receive message"

def test_async(bus: VirtualBus) -> None:

    async def retrieve_messages(q: asyncio.Queue[tuple[str, ...]]) -> list[tuple[str, ...]]:
        messages: list[tuple[str, ...]] = []
        try:
            messages.append(await q.get())
        except asyncio.QueueEmpty:
            pass
        return messages

    class TestPublisher(Publisher):
        def __init__(self, info: ControllerInfo, models: dict[str, ModelProtocol], virtual_bus: VirtualBus) -> None:
            super().__init__(virtual_bus)
            self.info = info
            self.models = models
            self.virtual_bus = virtual_bus

    class TestSubscriber(AsyncSubscriber):
        def __init__(self, info: ControllerInfo, models: dict[str, ModelProtocol], virtual_bus: VirtualBus) -> None:
            super().__init__(virtual_bus, "test")
            self.info = info
            self.virtual_bus = virtual_bus
            self.msg_queue: asyncio.Queue[tuple[str, ...]] = asyncio.Queue()

        async def consume(self, content: list[bytes]) -> None:
            await self.msg_queue.put(tuple(c.decode() for c in content))


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
    assert sub.sub_future is not None, "Consumer task not started"

    assert sub.sub_future.done() is False, "Consumer task not running"

    pub.pub_socket.send_multipart([b"test", b"message"])
    pub.pub_socket.send_multipart([b"other-topic", b"message"])

    # wait for wait for
    # reception
    time.sleep(0.1)

    fut = asyncio.run_coroutine_threadsafe(retrieve_messages(sub.msg_queue), sub.virtual_bus.loop)
    messages = fut.result()

    bus.shutdown()

    # wait for cleanup
    time.sleep(1)

    assert sub.sub_future.done(), "Subscriber task not terminated"

    assert len(messages) == 1, "Subscriber received more than one message or no message"
    assert messages == [("test", "message")], "Subscriber did not receive message"

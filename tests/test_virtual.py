import logging
import threading
import time
import queue
from itertools import count
from typing import Generator

import zmq
import pytest

from sunflare.virtual import Signal, VirtualBus, slot, Publisher, SyncSubscriber
from sunflare.log import Loggable

sub_cnt = count()


class MockVirtualBus(VirtualBus):
    sigMySignal = Signal(int, description="My signal")


class MockPublisher(Publisher):
    def __init__(
        self,
        virtual_bus: VirtualBus,
    ) -> None:
        super().__init__(virtual_bus)
        self.virtual_bus = virtual_bus


class MockSubscriber(SyncSubscriber, Loggable):
    def __init__(
        self,
        virtual_bus: VirtualBus,
        topics: list[str] = ["test"],
        id: int = 0,
    ) -> None:
        super().__init__(virtual_bus, topics)
        self.id = id
        self.msg_queue: queue.Queue[tuple[str, ...]] = queue.Queue()

    def consume(self, content: list[bytes]) -> None:
        msg = tuple(c.decode() for c in content)
        self.debug(f"Received message: {msg}")
        self.msg_queue.put(msg)

    @property
    def name(self) -> str:
        return "SUB[{}]".format(self.id)


class MockPubSync(Publisher, SyncSubscriber):
    def __init__(
        self,
        virtual_bus: VirtualBus,
        topics: list[str] = ["test"],
    ) -> None:
        Publisher.__init__(self, virtual_bus)
        SyncSubscriber.__init__(self, virtual_bus, topics)
        self.virtual_bus = virtual_bus
        self.msg_queue: queue.Queue[tuple[str, ...]] = queue.Queue()

    def consume(self, content: list[bytes]) -> None:
        self.msg_queue.put(tuple(c.decode() for c in content))


def retrieve_messages(q: queue.Queue) -> list[tuple[str, ...]]:
    messages: list[tuple[str, ...]] = []
    try:
        while True:
            messages.append(q.get(block=False))
            q.task_done()
    except queue.Empty:
        pass
    return messages


@pytest.fixture(scope="function")
def mock_bus() -> Generator[MockVirtualBus, None, None]:
    context = zmq.Context.instance()
    context.term()
    zmq.Context._instance = None

    _bus = MockVirtualBus()

    yield _bus

    _bus.shutdown()

    context = zmq.Context.instance()
    context.term()
    zmq.Context._instance = None


def test_virtual_bus(mock_bus: MockVirtualBus) -> None:
    """Tests the creation of a singleton virtual mock_bus."""

    assert hasattr(mock_bus, "sigMySignal")


def test_virtual_bus_psygnal_registration(mock_bus: MockVirtualBus) -> None:
    """Tests the registration of signals in the virtual mock_bus."""

    class MockOwner:
        sigMySignal = Signal(int, description="My signal")

    owner = MockOwner()

    mock_bus.register_signals(owner)

    assert "MockOwner" in mock_bus

    def test_slot(x: int) -> None:
        assert x == 5

    mock_bus["MockOwner"]["sigMySignal"].connect(lambda x: test_slot(x))
    mock_bus["MockOwner"]["sigMySignal"].emit(5)


def test_virtual_bus_no_object(
    caplog: pytest.LogCaptureFixture, mock_bus: VirtualBus
) -> None:
    """Test that trying to access a non-existent signal raises an error."""

    logger = logging.getLogger("redsun")
    logger.setLevel(logging.DEBUG)

    signals = mock_bus["MockOwner"]

    assert len(signals) == 0
    assert caplog.records[0].levelname == "ERROR"
    assert caplog.records[0].message == "Class MockOwner not found in the registry."


def test_virtual_bus_psygnal_connection(mock_bus: VirtualBus) -> None:
    """Tests the connection of signals in the virtual mock_bus."""

    class FirstMockOwner:
        sigFirstSignal = Signal(int)

        def __init__(self, mock_bus: VirtualBus) -> None:
            self.mock_bus = mock_bus

        def registration_phase(self) -> None:
            self.mock_bus.register_signals(self)

        def connection_phase(self) -> None:
            self.mock_bus["SecondMockOwner"]["sigSecondSignal"].connect(
                self.second_to_first
            )

        def second_to_first(self, x: int) -> None:
            assert x == 5

    class SecondMockOwner:
        sigSecondSignal = Signal(int)

        def __init__(self, mock_bus: VirtualBus) -> None:
            self.mock_bus = mock_bus

        def registration_phase(self) -> None:
            self.mock_bus.register_signals(self)

        def connection_phase(self) -> None:
            self.mock_bus["FirstMockOwner"]["sigFirstSignal"].connect(
                self.first_to_second
            )

        def first_to_second(self, x: int) -> None:
            assert x == 5

    first_owner = FirstMockOwner(mock_bus)
    second_owner = SecondMockOwner(mock_bus)

    first_owner.registration_phase()
    second_owner.registration_phase()

    first_owner.connection_phase()
    second_owner.connection_phase()

    assert "FirstMockOwner" in mock_bus
    assert "SecondMockOwner" in mock_bus

    first_owner.sigFirstSignal.emit(5)
    second_owner.sigSecondSignal.emit(5)


def test_virtual_bus_psygnal_connection_only(mock_bus: VirtualBus) -> None:
    """Test "register_signals" using the 'only' parameter."""

    def callback(x: int) -> None:
        assert x == 5

    class MockOwner:
        sigSignalOne = Signal(int)
        sigSignalTwo = Signal(int)

    owner = MockOwner()

    mock_bus.register_signals(owner, only=["sigSignalOne"])

    assert "MockOwner" in mock_bus
    assert len(mock_bus["MockOwner"]) == 1
    assert "sigSignalOne" in mock_bus["MockOwner"]
    assert "sigSignalTwo" not in mock_bus["MockOwner"]

    mock_bus["MockOwner"]["sigSignalOne"].connect(callback)
    owner.sigSignalOne.emit(5)


def test_slot() -> None:
    """Tests the slot decorator."""

    @slot
    def test_slot(x: int) -> None:
        assert x == 5

    assert hasattr(test_slot, "__isslot__")


def test_slot_private() -> None:
    """Tests the slot decorator when it is private."""

    @slot(private=True)
    def _test_slot(x: int) -> None:
        assert x == 5

    assert hasattr(_test_slot, "__isslot__")
    assert hasattr(_test_slot, "__isprivate__")


def test_virtual_bus_zmq(mock_bus: VirtualBus) -> None:
    """Test the mock_bus ZMQ context."""

    class Publisher(Loggable):
        def __init__(self, mock_bus: VirtualBus) -> None:
            self.mock_bus = mock_bus
            self.socket = self.mock_bus.connect_publisher()

        def send(self, msg: str) -> None:
            self.debug(f"Sending message: {msg}")
            self.socket.send_string(msg)

    class Subscriber(Loggable):
        def __init__(self, mock_bus: VirtualBus) -> None:
            self.msg = ""
            self.mock_bus = mock_bus
            self.socket, self.poller = self.mock_bus.connect_subscriber()
            self.socket.subscribe("")

            self.thread = threading.Thread(target=self._polling_thread, daemon=True)
            self.thread.start()

        def _polling_thread(self) -> None:
            try:
                while True:
                    try:
                        socks = dict(self.poller.poll())
                        if self.socket in socks:
                            self.msg = self.socket.recv_string()
                            self.debug(f"Received message: {self.msg}")
                    except zmq.error.ContextTerminated:
                        break
            finally:
                self.poller.unregister(self.socket)
                self.socket.close()
                self.debug("Subscriber socket closed.")

    pub = Publisher(mock_bus)
    sub = Subscriber(mock_bus)

    # give time for
    # subscrbier to connect
    time.sleep(0.1)

    test_msg = "Hello, World!"
    pub.send(test_msg)

    # give some time
    # for message transmission
    time.sleep(0.1)

    # shutdown the mock_bus;
    # this will kill
    # all connected
    # subscribers
    mock_bus.shutdown()

    assert sub.msg == test_msg, f"Expected '{test_msg}', but got '{sub.msg}'"


def test_virtual_bus_subscriptions(mock_bus: VirtualBus) -> None:
    """Test that subscribers only receive messages they're subscribed to."""

    logger = logging.getLogger("redsun")
    logger.setLevel(logging.DEBUG)

    class Publisher(Loggable):
        def __init__(self, mock_bus: VirtualBus) -> None:
            self.mock_bus = mock_bus
            self.socket = self.mock_bus.connect_publisher()

        def send(self, topic: str, value: float) -> None:
            msg = f"{topic} {value}"
            self.debug(f"Sending message: {msg}")
            self.socket.send_string(msg)

    class Subscriber(Loggable):
        def __init__(self, mock_bus: VirtualBus, topics: list[str]) -> None:
            self.received_messages: list[str] = []
            self.mock_bus = mock_bus
            self.socket, self.poller = self.mock_bus.connect_subscriber(topic=topics)
            self.debug(f"Subscribed to: {topics}")

            self.thread = threading.Thread(target=self._polling_thread, daemon=True)
            self.thread.start()

        def _polling_thread(self) -> None:
            try:
                while True:
                    try:
                        socks = dict(self.poller.poll())
                        if self.socket in socks:
                            msg = self.socket.recv_string()
                            self.debug(f"Received message: {msg}")
                            self.received_messages.append(msg)
                    except zmq.error.ContextTerminated:
                        break
            finally:
                self.poller.unregister(self.socket)
                self.socket.close()
                self.debug("Subscriber socket closed.")

    # Create publisher and subscribers
    pub = Publisher(mock_bus)

    # Create subscribers with different topic subscriptions
    sub_temp = Subscriber(mock_bus, ["temperature"])  # Only temperature messages
    sub_humidity = Subscriber(mock_bus, ["humidity"])  # Only humidity messages

    # Wait for subscriptions to be set up
    time.sleep(0.1)

    logger.debug(mock_bus._forwarder._sockets)

    # Send various messages
    pub.send("temperature", 25.5)
    pub.send("humidity", 60.0)
    pub.send("pressure", 1013.25)  # Neither subscriber should receive this

    # Wait for message processing
    time.sleep(0.1)

    # shutdown the mock_bus;
    # this will kill
    # all connected
    # subscribers
    mock_bus.shutdown()

    # Verify temperature subscriber
    temp_messages = sub_temp.received_messages
    assert len(temp_messages) == 1, (
        f"Expected 1 temperature message, got {len(temp_messages)}"
    )
    assert temp_messages[0] == "temperature 25.5", (
        f"Unexpected message: {temp_messages[0]}"
    )
    assert not any("humidity" in msg for msg in temp_messages), (
        "Temperature subscriber received humidity message"
    )
    assert not any("pressure" in msg for msg in temp_messages), (
        "Temperature subscriber received pressure message"
    )

    # Verify humidity subscriber
    humid_messages = sub_humidity.received_messages
    assert len(humid_messages) == 1, (
        f"Expected 1 humidity message, got {len(humid_messages)}"
    )
    assert humid_messages[0] == "humidity 60.0", (
        f"Unexpected message: {humid_messages[0]}"
    )
    assert not any("temperature" in msg for msg in humid_messages), (
        "Humidity subscriber received temperature message"
    )
    assert not any("pressure" in msg for msg in humid_messages), (
        "Humidity subscriber received pressure message"
    )


def test_sync(bus: VirtualBus) -> None:
    pub = MockPublisher(bus)
    sub = MockSubscriber(bus)

    # wait for the startup
    time.sleep(0.1)

    assert pub.pub_socket is not None, "Publisher socket not initialized"
    assert pub.pub_socket.getsockopt(zmq.TYPE) == zmq.PUB, (
        "Publisher socket not of type PUB"
    )

    assert sub.sub_socket is not None, "Subscriber socket not initialized"
    assert sub.sub_socket.getsockopt(zmq.TYPE) == zmq.SUB, (
        "Subscriber socket not of type SUB"
    )
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
    pub_sub = MockPubSync(bus)

    # wait for the startup
    time.sleep(0.1)

    assert pub_sub.pub_socket is not None, "Publisher socket not initialized"
    assert pub_sub.pub_socket.getsockopt(zmq.TYPE) == zmq.PUB, (
        "Publisher socket not of type PUB"
    )
    assert pub_sub.sub_socket is not None, "Subscriber socket not initialized"
    assert pub_sub.sub_socket.getsockopt(zmq.TYPE) == zmq.SUB, (
        "Subscriber socket not of type SUB"
    )
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


def test_one_to_many(bus: VirtualBus) -> None:
    def create_subscribers(topics: list[list[str]]) -> list[MockSubscriber]:
        subscribers = []
        for t in topics:
            sub = MockSubscriber(bus, t, next(sub_cnt))
            subscribers.append(sub)
        return subscribers

    pub = MockPublisher(bus)

    # "" is for catching all messages
    topics = ["", "topic1", "topic2", "topic3"]
    subscribers = create_subscribers(topics)

    pub.pub_socket.send_multipart([b"topic1", b"message1"])
    pub.pub_socket.send_multipart([b"topic2", b"message2"])
    pub.pub_socket.send_multipart([b"topic3", b"message3"])

    # wait for the messages to be processed
    time.sleep(0.5)

    bus.shutdown()

    # wait for cleanup
    time.sleep(0.1)

    expected_messages = {
        0: [("topic1", "message1"), ("topic2", "message2"), ("topic3", "message3")],
        1: [("topic1", "message1")],
        2: [("topic2", "message2")],
        3: [("topic3", "message3")],
    }

    for sub in subscribers:
        messages = retrieve_messages(sub.msg_queue)
        assert len(messages) == len(expected_messages[sub.id]), (
            "Subscriber received incorrect amount of messages"
        )
        assert messages == expected_messages[sub.id], (
            "Subscriber did not receive message"
        )


def test_many_to_one(bus: VirtualBus) -> None:
    topics = ["topic1", "topic2", "topic3"]
    publishers = [MockPublisher(bus) for _ in range(3)]
    sub = MockSubscriber(bus)
    sub.sub_socket.subscribe(b"topic1")
    sub.sub_socket.subscribe(b"topic2")
    sub.sub_socket.subscribe(b"topic3")

    for p, t in zip(publishers, topics):
        p.pub_socket.send_multipart([t.encode(), b"message"])

    # wait for the messages to be processed
    time.sleep(0.5)

    bus.shutdown()

    # wait for cleanup
    time.sleep(0.1)

    messages = retrieve_messages(sub.msg_queue)

    assert len(messages) == 3, "Subscriber received incorrect amount of messages"
    assert messages == [
        ("topic1", "message"),
        ("topic2", "message"),
        ("topic3", "message"),
    ], "Subscriber did not receive message"


def test_many_to_many(bus: VirtualBus) -> None:
    topics = ["topic1", "topic2", "topic3"]
    publishers = [MockPublisher(bus) for _ in range(3)]
    subscribers = [MockSubscriber(bus, topic) for _, topic in zip(range(3), topics)]

    for p, t in zip(publishers, topics):
        p.pub_socket.send_multipart([t.encode(), b"message"])

    # wait for the messages to be processed
    time.sleep(0.5)

    bus.shutdown()

    # wait for cleanup
    time.sleep(0.1)

    for sub in subscribers:
        messages = retrieve_messages(sub.msg_queue)
        assert len(messages) == 1, "Subscriber received incorrect amount of messages"
        assert messages == [(sub.sub_topics, "message")], (
            "Subscriber did not receive message"
        )

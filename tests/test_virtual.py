# type: ignore
import logging
import threading
import time

from typing import Generator

import zmq
import pytest

from sunflare.virtual import Signal, VirtualBus, slot
from sunflare.log import Loggable

class MockVirtualBus(VirtualBus):
    sigMySignal = Signal(int, description="My signal")

@pytest.fixture(scope="function")
def bus() -> Generator[MockVirtualBus, None, None]:

    context = zmq.Context.instance()
    context.term()
    zmq.Context._instance = None

    _bus = MockVirtualBus()

    yield _bus

    _bus.shutdown()

    context = zmq.Context.instance()
    context.term()
    zmq.Context._instance = None


def test_virtual_bus(bus: MockVirtualBus) -> None:
    """Tests the creation of a singleton virtual bus."""

    assert hasattr(bus, "sigMySignal")


def test_virtual_bus_psygnal_registration(bus: MockVirtualBus) -> None:
    """Tests the registration of signals in the virtual bus."""

    class MockOwner:
        sigMySignal = Signal(int, description="My signal")

    owner = MockOwner()

    bus.register_signals(owner)

    assert "MockOwner" in bus

    def test_slot(x: int) -> None:
        assert x == 5

    bus["MockOwner"]["sigMySignal"].connect(lambda x: test_slot(x))
    bus["MockOwner"]["sigMySignal"].emit(5)

def test_virtual_bus_no_object(caplog: pytest.LogCaptureFixture,bus: VirtualBus) -> None:
    """Test that trying to access a non-existent signal raises an error."""

    logger = logging.getLogger("redsun")
    logger.setLevel(logging.DEBUG)

    signals = bus["MockOwner"]

    assert len(signals) == 0
    assert caplog.records[0].levelname == "ERROR"
    assert caplog.records[0].message == "Class MockOwner not found in the registry."


def test_virtual_bus_psygnal_connection(bus: VirtualBus) -> None:
    """Tests the connection of signals in the virtual bus."""

    class FirstMockOwner:
        sigFirstSignal = Signal(int)

        def __init__(self, bus: VirtualBus) -> None:
            self.bus = bus

        def registration_phase(self) -> None:
            self.bus.register_signals(self)

        def connection_phase(self) -> None:
            self.bus["SecondMockOwner"]["sigSecondSignal"].connect(self.second_to_first)

        def second_to_first(self, x: int) -> None:
            assert x == 5

    class SecondMockOwner:
        sigSecondSignal = Signal(int)

        def __init__(self, bus: VirtualBus) -> None:
            self.bus = bus
        
        def registration_phase(self) -> None:
            self.bus.register_signals(self)
        
        def connection_phase(self) -> None:
            self.bus["FirstMockOwner"]["sigFirstSignal"].connect(self.first_to_second)

        def first_to_second(self, x: int) -> None:
            assert x == 5

    first_owner = FirstMockOwner(bus)
    second_owner = SecondMockOwner(bus)

    first_owner.registration_phase()
    second_owner.registration_phase()

    first_owner.connection_phase()
    second_owner.connection_phase()

    assert "FirstMockOwner" in bus
    assert "SecondMockOwner" in bus

    first_owner.sigFirstSignal.emit(5)
    second_owner.sigSecondSignal.emit(5)


def test_virtual_bus_psygnal_connection_only(bus: VirtualBus) -> None:
    """Test "register_signals" using the 'only' parameter. """

    def callback(x: int) -> None:
        assert x == 5

    class MockOwner:
        sigSignalOne = Signal(int)
        sigSignalTwo = Signal(int)

    owner = MockOwner()

    bus.register_signals(owner, only=["sigSignalOne"])

    assert "MockOwner" in bus
    assert len(bus["MockOwner"]) == 1
    assert "sigSignalOne" in bus["MockOwner"]
    assert "sigSignalTwo" not in bus["MockOwner"]

    bus["MockOwner"]["sigSignalOne"].connect(callback)
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


def test_virtual_bus_zmq(bus: VirtualBus) -> None:
    """Test the bus ZMQ context."""

    class Publisher(Loggable):
        def __init__(self, bus: VirtualBus) -> None:
            self.bus = bus
            self.socket = self.bus.connect(zmq.PUB)

        def send(self, msg: str) -> None:
            self.debug(f"Sending message: {msg}")
            self.socket.send_string(msg)

    class Subscriber(Loggable):
        def __init__(self, bus: VirtualBus) -> None:
            self.msg = ""
            self.bus = bus
            self.socket, self.poller = self.bus.connect(zmq.SUB)
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

    pub = Publisher(bus)
    sub = Subscriber(bus)

    # give time for
    # subscrbier to connect
    time.sleep(0.1)

    test_msg = "Hello, World!"
    pub.send(test_msg)

    # give some time
    # for message transmission
    time.sleep(0.1)

    # shutdown the bus;
    # this will kill
    # all connected
    # subscribers
    bus.shutdown()

    assert sub.msg == test_msg, f"Expected '{test_msg}', but got '{sub.msg}'"

def test_virtual_bus_subscriptions(bus: VirtualBus) -> None:
    """Test that subscribers only receive messages they're subscribed to."""

    logger = logging.getLogger("redsun")
    logger.setLevel(logging.DEBUG)

    class Publisher(Loggable):
        def __init__(self, bus: VirtualBus) -> None:
            self.bus = bus
            self.socket = self.bus.connect(zmq.PUB)

        def send(self, topic: str, value: float) -> None:
            msg = f"{topic} {value}"
            self.debug(f"Sending message: {msg}")
            self.socket.send_string(msg)

    class Subscriber(Loggable):
        def __init__(self, bus: VirtualBus, topics: list[str]) -> None:
            self.received_messages: list[str] = []
            self.bus = bus
            self.socket, self.poller = self.bus.connect(zmq.SUB, topic=topics)
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
    pub = Publisher(bus)
    
    # Create subscribers with different topic subscriptions
    sub_temp = Subscriber(bus, ["temperature"])  # Only temperature messages
    sub_humidity = Subscriber(bus, ["humidity"])  # Only humidity messages
    
    # Wait for subscriptions to be set up
    time.sleep(0.1)

    logger.debug(bus._forwarder._sockets)    

    # Send various messages
    pub.send("temperature", 25.5)
    pub.send("humidity", 60.0)
    pub.send("pressure", 1013.25)  # Neither subscriber should receive this

    # Wait for message processing
    time.sleep(0.1)

    # shutdown the bus;
    # this will kill
    # all connected
    # subscribers
    bus.shutdown()

    # Verify temperature subscriber
    temp_messages = sub_temp.received_messages
    assert len(temp_messages) == 1, f"Expected 1 temperature message, got {len(temp_messages)}"
    assert temp_messages[0] == "temperature 25.5", f"Unexpected message: {temp_messages[0]}"
    assert not any("humidity" in msg for msg in temp_messages), "Temperature subscriber received humidity message"
    assert not any("pressure" in msg for msg in temp_messages), "Temperature subscriber received pressure message"

    # Verify humidity subscriber
    humid_messages = sub_humidity.received_messages
    assert len(humid_messages) == 1, f"Expected 1 humidity message, got {len(humid_messages)}"
    assert humid_messages[0] == "humidity 60.0", f"Unexpected message: {humid_messages[0]}"
    assert not any("temperature" in msg for msg in humid_messages), "Humidity subscriber received temperature message"
    assert not any("pressure" in msg for msg in humid_messages), "Humidity subscriber received pressure message"

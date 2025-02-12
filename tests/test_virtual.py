# type: ignore
import logging

import pytest

from sunflare.log import get_logger
from sunflare.virtual import Signal, VirtualBus, slot


class MockVirtualBus(VirtualBus):
    sigMySignal = Signal(int, description="My signal")

    def __init__(self):
        super().__init__()


def test_virtual_bus() -> None:
    """Tests the creation of a singleton virtual bus."""
    bus = MockVirtualBus()

    assert hasattr(bus, "sigMySignal")


def test_virtual_bus_psygnal_registration() -> None:
    """Tests the registration of signals in the virtual bus."""

    class MockOwner:
        sigMySignal = Signal(int, description="My signal")

    owner = MockOwner()
    bus = MockVirtualBus()

    bus.register_signals(owner)

    assert "MockOwner" in bus

    def test_slot(x: int) -> None:
        assert x == 5

    bus["MockOwner"]["sigMySignal"].connect(lambda x: test_slot(x))
    bus["MockOwner"]["sigMySignal"].emit(5)

def test_virtual_bus_no_object(caplog: pytest.LogCaptureFixture) -> None:
    """Test that trying to access a non-existent signal raises an error."""

    logger = get_logger()
    logger.setLevel(logging.DEBUG)

    bus = MockVirtualBus()
    signals = bus["MockOwner"]

    assert len(signals) == 0
    assert caplog.records[0].levelname == "ERROR"
    assert caplog.records[0].message == "Class MockOwner not found in the registry."


def test_virtual_bus_psygnal_connection() -> None:
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

    bus = MockVirtualBus()

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


def test_virtual_bus_psygnal_connection_only() -> None:
    """Test "register_signals" using the 'only' parameter. """

    def callback(x: int) -> None:
        assert x == 5

    class MockOwner:
        sigSignalOne = Signal(int)
        sigSignalTwo = Signal(int)

    bus = MockVirtualBus()
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


def test_virtual_bus_zmq() -> None:
    """Test the bus ZMQ context."""

    import zmq, threading

    class Publisher():
        def __init__(self, bus: VirtualBus) -> None:
            self.bus = bus
            self.socket = self.bus.connect(self, zmq.PUB)

        def send(self, msg: str) -> None:
            self.socket.send_string(msg)

    class Subscriber():
        def __init__(self, bus: VirtualBus) -> None:
            self.msg = ""
            self.bus = bus
            self.socket, self.poller = self.bus.connect(self, zmq.SUB)

            self.thread = threading.Thread(target=self._polling_thread, daemon=True)
            self.thread.start()

        def _polling_thread(self) -> None:
            while True:
                try:
                    socks = dict(self.poller.poll())
                    if self.socket in socks:
                        self.msg = self.socket.recv_string()
                except zmq.error.ContextTerminated:
                    break

    bus = VirtualBus()
    pub = Publisher(bus)
    sub = Subscriber(bus)

    pub.send("Hello, World!")

    bus.shutdown()

    assert sub.msg == "Hello, World!"

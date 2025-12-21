import logging

import pytest

from sunflare.virtual import Signal, VirtualBus
from event_model import DocumentRouter

logger = logging.getLogger("redsun")
logger.setLevel(logging.DEBUG)


def simple_callback(name: str, doc: dict) -> None:
    logger.debug(f"received {name} document")


class MockRouter(DocumentRouter):
    def __init__(self) -> None:
        super().__init__()
        self.received_docs: list[tuple[str, dict]] = []

    def event(self, doc: dict) -> None:
        logger.debug("MockRouter received event document")

    def start(self, doc: dict) -> None:
        logger.debug("MockRouter received start document")

    def stop(self, doc: dict) -> None:
        logger.debug("MockRouter received stop document")

    def descriptor(self, doc: dict) -> None:
        logger.debug("MockRouter received descriptor document")


class MockCallback:
    def __call__(self, name: str, doc: dict) -> None:
        logger.debug(f"MockCallback received {name} document")


class MockMethodCallback:
    """Mock class with a regular method callback for testing bound methods."""

    def process_document(self, name: str, doc: dict) -> None:
        logger.debug(f"MockMethodCallback.process_document received {name} document")


def test_virtual_bus_no_object(bus: VirtualBus) -> None:
    """Test that trying to access a non-existent signal raises an error."""

    logger = logging.getLogger("redsun")
    logger.setLevel(logging.DEBUG)

    with pytest.raises(KeyError):
        bus.signals["MockOwner"]


def test_virtual_bus_psygnal_connection(bus: VirtualBus) -> None:
    """Tests the connection of signals in the virtual bus."""

    class FirstMockOwner:
        sigFirstSignal = Signal(int)

        def __init__(self, bus: VirtualBus) -> None:
            self.bus = bus

        def registration_phase(self) -> None:
            self.bus.register_signals(self)

        def connection_phase(self) -> None:
            self.bus.signals["SecondMockOwner"]["sigSecondSignal"].connect(
                self.second_to_first
            )

        def second_to_first(self, x: int) -> None:
            assert x == 5

    class SecondMockOwner:
        sigSecondSignal = Signal(int)

        def __init__(self, bus: VirtualBus) -> None:
            self.bus = bus

        def registration_phase(self) -> None:
            self.bus.register_signals(self)

        def connection_phase(self) -> None:
            self.bus.signals["FirstMockOwner"]["sigFirstSignal"].connect(
                self.first_to_second
            )

        def first_to_second(self, x: int) -> None:
            assert x == 5

    first_owner = FirstMockOwner(bus)
    second_owner = SecondMockOwner(bus)

    first_owner.registration_phase()
    second_owner.registration_phase()

    first_owner.connection_phase()
    second_owner.connection_phase()

    assert "FirstMockOwner" in bus.signals
    assert "SecondMockOwner" in bus.signals

    first_owner.sigFirstSignal.emit(5)
    second_owner.sigSecondSignal.emit(5)


def test_virtual_bus_psygnal_connection_only(bus: VirtualBus) -> None:
    """Test "register_signals" using the 'only' parameter."""

    def callback(x: int) -> None:
        assert x == 5

    class MockOwner:
        sigSignalOne = Signal(int)
        sigSignalTwo = Signal(int)

    owner = MockOwner()

    bus.register_signals(owner, only=["sigSignalOne"])

    assert "MockOwner" in bus.signals
    assert len(bus.signals["MockOwner"]) == 1
    assert "sigSignalOne" in bus.signals["MockOwner"]
    assert "sigSignalTwo" not in bus.signals["MockOwner"]

    bus.signals["MockOwner"]["sigSignalOne"].connect(callback)
    owner.sigSignalOne.emit(5)


def test_virtual_bus_callback_registration(bus: VirtualBus) -> None:
    """Test registering callbacks to the virtual bus."""

    with pytest.raises(TypeError):

        def wrong_callback(name: str) -> None:
            pass

        bus.register_callbacks(wrong_callback)

    with pytest.raises(TypeError):
        non_callable = 42
        bus.register_callbacks(non_callable)

    # Regular function - key should be function name
    bus.register_callbacks(simple_callback)
    assert len(bus.callbacks) == 1
    assert "simple_callback" in bus.callbacks

    # DocumentRouter subclass - key should be class name
    router = MockRouter()
    bus.register_callbacks(router)
    assert len(bus.callbacks) == 2
    assert "MockRouter" in bus.callbacks

    # Callable object (instance with __call__) - key should be class name
    mock_callback = MockCallback()
    bus.register_callbacks(mock_callback)
    assert len(bus.callbacks) == 3
    assert "MockCallback" in bus.callbacks

    # Bound method - key should be method name
    method_callback = MockMethodCallback()
    bus.register_callbacks(method_callback.process_document)
    assert len(bus.callbacks) == 4
    assert "process_document" in bus.callbacks

    # Bound __call__ method - key should be class name
    another_callable = MockCallback()
    bus.register_callbacks(another_callable.__call__)
    assert len(bus.callbacks) == 4  # same key as Test 3, so count stays the same
    assert "MockCallback" in bus.callbacks

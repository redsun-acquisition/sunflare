import logging

import pytest

from sunflare.virtual import Signal, VirtualContainer, IsProvider, IsInjectable
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
    def process_document(self, name: str, doc: dict) -> None:
        logger.debug(f"MockMethodCallback.process_document received {name} document")


def test_virtual_container_no_object(bus: VirtualContainer) -> None:
    """Test that accessing a non-existent signal key raises KeyError."""
    with pytest.raises(KeyError):
        bus.signals["MockOwner"]


def test_virtual_container_psygnal_connection(bus: VirtualContainer) -> None:
    """Tests signal registration and cross-component connection via VirtualContainer."""

    class FirstMockOwner(IsProvider):
        sigFirstSignal = Signal(int)

        def __init__(self, container: VirtualContainer) -> None:
            self.container = container
            self.name = "FirstMockOwner"

        def register_providers(self, container: VirtualContainer) -> None:
            container.register_signals(self)

        def second_to_first(self, x: int) -> None:
            assert x == 5

    class SecondMockOwner(IsInjectable):
        sigSecondSignal = Signal(int)

        def __init__(self, container: VirtualContainer) -> None:
            self.container = container
            self.name = "SecondMockOwner"

        def inject_dependencies(self, container: VirtualContainer) -> None:
            container.register_signals(self)
            container.signals["FirstMockOwner"]["sigFirstSignal"].connect(
                self.first_to_second
            )

        def first_to_second(self, x: int) -> None:
            assert x == 5

    first_owner = FirstMockOwner(bus)
    second_owner = SecondMockOwner(bus)

    # provider registers its own signals first
    first_owner.register_providers(bus)
    # injectable registers its signals and connects to provider's signals
    second_owner.inject_dependencies(bus)

    # first owner can now connect to second owner's signal
    bus.signals["SecondMockOwner"]["sigSecondSignal"].connect(first_owner.second_to_first)

    assert "FirstMockOwner" in bus.signals
    assert "SecondMockOwner" in bus.signals

    first_owner.sigFirstSignal.emit(5)
    second_owner.sigSecondSignal.emit(5)


def test_virtual_container_psygnal_connection_only(bus: VirtualContainer) -> None:
    """Test 'register_signals' using the 'only' parameter."""

    def callback(x: int) -> None:
        assert x == 5

    class MockOwner:
        sigSignalOne = Signal(int)
        sigSignalTwo = Signal(int)

        @property
        def name(self) -> str:
            return "MockOwner"

    owner = MockOwner()

    bus.register_signals(owner, only=["sigSignalOne"])

    assert "MockOwner" in bus.signals
    assert len(bus.signals["MockOwner"]) == 1
    assert "sigSignalOne" in bus.signals["MockOwner"]
    assert "sigSignalTwo" not in bus.signals["MockOwner"]

    bus.signals["MockOwner"]["sigSignalOne"].connect(callback)
    owner.sigSignalOne.emit(5)


def test_virtual_container_callback_registration(bus: VirtualContainer) -> None:
    """Test registering callbacks to the virtual container."""

    with pytest.raises(TypeError):

        def wrong_callback(name: str) -> None:
            pass

        bus.register_callbacks(wrong_callback)

    with pytest.raises(TypeError):
        non_callable = 42
        bus.register_callbacks(non_callable)

    bus.register_callbacks("simple_callback", simple_callback)
    assert len(bus.callbacks) == 1
    assert "simple_callback" in bus.callbacks

    router = MockRouter()
    bus.register_callbacks("MockRouter", router)
    assert len(bus.callbacks) == 2
    assert "MockRouter" in bus.callbacks

    mock_callback = MockCallback()
    bus.register_callbacks("MockCallback", mock_callback)
    assert len(bus.callbacks) == 3
    assert "MockCallback" in bus.callbacks

    method_callback = MockMethodCallback()
    bus.register_callbacks("process_document", method_callback.process_document)
    assert len(bus.callbacks) == 4
    assert "process_document" in bus.callbacks


def test_is_provider_protocol(bus: VirtualContainer) -> None:
    """Test IsProvider structural protocol check."""

    class MyPresenter(IsProvider):
        def register_providers(self, container: VirtualContainer) -> None:
            pass

    p = MyPresenter()
    assert isinstance(p, IsProvider)
    p.register_providers(bus)


def test_is_injectable_protocol(bus: VirtualContainer) -> None:
    """Test IsInjectable structural protocol check."""

    class MyView(IsInjectable):
        def inject_dependencies(self, container: VirtualContainer) -> None:
            pass

    v = MyView()
    assert isinstance(v, IsInjectable)
    v.inject_dependencies(bus)

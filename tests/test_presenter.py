import pytest
from collections.abc import Mapping
from sunflare.model import PModel
from sunflare.presenter import Presenter, Receiver, Sender, SenderReceiver, Connection
from sunflare.virtual import Signal, VirtualBus


@pytest.fixture
def virtual_bus() -> VirtualBus:
    return VirtualBus()


@pytest.fixture
def models() -> dict[str, PModel]:
    return {}


def test_base_presenter(models: Mapping[str, PModel], virtual_bus: VirtualBus) -> None:
    """Test basic Presenter functionality."""

    class TestController(Presenter):
        def __init__(
            self,
            models: Mapping[str, PModel],
            virtual_bus: VirtualBus,
        ) -> None:
            super().__init__(models, virtual_bus)

    controller = TestController(models, virtual_bus)

    assert controller.models == models
    assert controller.virtual_bus == virtual_bus


def test_sender_presenter(
    models: Mapping[str, PModel], virtual_bus: VirtualBus
) -> None:
    """Test Sender functionality."""

    class TestController(Sender):
        sigTestSignal = Signal(str)
        sigAnotherSignal = Signal(int)

        def __init__(
            self,
            models: Mapping[str, PModel],
            virtual_bus: VirtualBus,
        ) -> None:
            super().__init__(models, virtual_bus, signals=["sigTestSignal"])

    controller = TestController(models, virtual_bus)
    controller.registration_phase()

    assert "TestController" in virtual_bus.signals
    assert "sigTestSignal" in virtual_bus.signals["TestController"]
    assert "sigAnotherSignal" not in virtual_bus.signals["TestController"]


def test_receiver_presenter(
    models: Mapping[str, PModel], virtual_bus: VirtualBus
) -> None:
    """Test Receiver functionality."""

    class DummySender(Sender):
        sigDummySignal = Signal(str)

        def __init__(
            self,
            models: Mapping[str, PModel],
            virtual_bus: VirtualBus,
        ) -> None:
            super().__init__(models, virtual_bus, signals=["sigDummySignal"])

    class TestController(Receiver):
        def __init__(
            self,
            models: Mapping[str, PModel],
            virtual_bus: VirtualBus,
        ) -> None:
            connection_map = {
                "DummySender": [Connection("sigDummySignal", self.dummy_slot)]
            }
            super().__init__(models, virtual_bus, connection_map=connection_map)
            self.received_value = None

        def dummy_slot(self, value: str) -> None:
            self.received_value = value

    sender = DummySender(models, virtual_bus)
    sender.registration_phase()

    receiver = TestController(models, virtual_bus)
    receiver.connection_phase()

    # Emit signal and check reception
    sender.sigDummySignal.emit("test_value")
    assert receiver.received_value == "test_value"


def test_sender_receiver_presenter(
    models: Mapping[str, PModel], virtual_bus: VirtualBus
) -> None:
    """Test SenderReceiver functionality."""

    class TestController(SenderReceiver):
        sigOutgoing = Signal(int)
        sigOtherOutgoing = Signal(str)

        def __init__(
            self,
            models: Mapping[str, PModel],
            virtual_bus: VirtualBus,
        ) -> None:
            connection_map = {
                "TestController": [Connection("sigOutgoing", self.incoming_slot)]
            }
            super().__init__(
                models,
                virtual_bus,
                signals=["sigOutgoing", "sigOtherOutgoing"],
                connection_map=connection_map,
            )
            self.received_value = None

        def incoming_slot(self, value: int) -> None:
            self.received_value = value

    controller = TestController(models, virtual_bus)
    controller.registration_phase()
    controller.connection_phase()

    # Check signals are registered
    assert "TestController" in virtual_bus.signals
    assert "sigOutgoing" in virtual_bus.signals["TestController"]
    assert "sigOtherOutgoing" in virtual_bus.signals["TestController"]

    # Test signal emission and reception
    controller.sigOutgoing.emit(42)
    assert controller.received_value == 42

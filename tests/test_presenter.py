import pytest
from collections.abc import Mapping
from sunflare.device import PDevice
from sunflare.presenter import Presenter, Connection
from sunflare.virtual import Signal, VirtualBus


@pytest.fixture
def virtual_bus() -> VirtualBus:
    return VirtualBus()


@pytest.fixture
def devices() -> dict[str, PDevice]:
    return {}


def test_base_presenter(
    devices: Mapping[str, PDevice], virtual_bus: VirtualBus
) -> None:
    """Test basic Presenter functionality."""

    class TestController(Presenter):
        def __init__(
            self,
            devices: Mapping[str, PDevice],
            virtual_bus: VirtualBus,
        ) -> None:
            super().__init__(devices, virtual_bus)

    controller = TestController(devices, virtual_bus)

    assert controller.devices == devices
    assert controller.virtual_bus == virtual_bus

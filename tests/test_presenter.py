import pytest
from collections.abc import Mapping
from sunflare.device import Device
from sunflare.presenter import Presenter
from sunflare.virtual import VirtualBus


@pytest.fixture
def devices() -> dict[str, Device]:
    return {}


def test_base_presenter(devices: Mapping[str, Device], bus: VirtualBus) -> None:
    """Test basic Presenter functionality."""

    class TestController(Presenter):
        def __init__(
            self,
            devices: Mapping[str, Device],
            virtual_bus: VirtualBus,
        ) -> None:
            super().__init__(devices, virtual_bus)

    controller = TestController(devices, bus)

    assert controller.devices == devices
    assert controller.virtual_bus == bus

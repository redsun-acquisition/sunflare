import pytest
from collections.abc import Mapping
from sunflare.device import Device
from sunflare.presenter import Presenter
from sunflare.virtual import VirtualContainer


@pytest.fixture
def devices() -> dict[str, Device]:
    return {}


def test_base_presenter(devices: Mapping[str, Device], bus: VirtualContainer) -> None:
    """Test basic Presenter functionality."""

    class TestController(Presenter):
        def __init__(
            self,
            name: str,
            devices: Mapping[str, Device],
            virtual_container: VirtualContainer,
        ) -> None:
            super().__init__(name, devices, virtual_container)

    controller = TestController("ctrl", devices, bus)

    assert controller.name == "ctrl"
    assert controller.devices == devices
    assert controller.virtual_container == bus

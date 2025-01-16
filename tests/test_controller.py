from typing import cast
from pathlib import Path
from mocks import MockControllerInfo, MockController, MockVirtualBus
from sunflare.config import RedSunSessionInfo, ControllerInfo

def test_controller(config_path: Path) -> None:
    config_file = config_path / "controller_instance.yaml"

    config = RedSunSessionInfo.load_yaml(str(config_file))
    config_ctrl: dict[str, ControllerInfo] = {
        name: MockControllerInfo(**input)
        for name, input in config["controllers"].items()
    }

    assert len(config_ctrl) == 1

    virtual_bus = MockVirtualBus()

    for _, ctrl in config_ctrl.items():
        controller = MockController(cast(MockControllerInfo, ctrl), virtual_bus)
        assert controller.controller_info == ctrl
        assert len(controller.plans) == 2
        assert len(controller.controller_info.events.signals) == 4

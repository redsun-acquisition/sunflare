from pathlib import Path
from typing import cast

from mocks import MockController, MockControllerInfo, MockVirtualBus

from sunflare.config import ControllerInfo, RedSunSessionInfo


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
        assert controller.controller_info.plugin_name == "N/A"
        assert controller.controller_info.repository == "N/A"

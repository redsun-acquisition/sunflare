from typing import cast
from pathlib import Path
from mocks import MockControllerInfo, MockController, MockEngineHandler, MockVirtualBus
from sunflare.config import RedSunSessionInfo, ControllerInfo
from sunflare.virtual import ModuleVirtualBus
from bluesky.utils import DuringTask

def test_controller(config_path: Path) -> None:
    config_file = config_path / "controller_instance.yaml"

    config = RedSunSessionInfo.load_yaml(str(config_file))
    config_ctrl: dict[str, ControllerInfo] = {
        name: MockControllerInfo(**input)
        for name, input in config["controllers"].items()
    }

    session = RedSunSessionInfo(engine=config["engine"], controllers=config_ctrl)

    assert len(config_ctrl) == 1

    virtual_bus = MockVirtualBus()
    module_bus = ModuleVirtualBus()

    mock_handler = MockEngineHandler(
        config=session,
        virtual_bus=virtual_bus,
        module_bus=module_bus,
        during_task=DuringTask(), # type: ignore
    )

    for _, ctrl in config_ctrl.items():
        controller = MockController(cast(MockControllerInfo, ctrl), mock_handler, virtual_bus, module_bus)
        assert controller.controller_info == ctrl
        assert len(controller.plans) == 2
        assert len(controller.controller_info.events.signals) == 4

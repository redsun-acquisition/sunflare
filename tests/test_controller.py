import time
import asyncio
import queue
import pytest
from pathlib import Path
from typing import cast

import zmq

from mocks import MockController, MockControllerInfo

from sunflare.model import ModelProtocol
from sunflare.config import ControllerInfo, RedSunSessionInfo
from sunflare.virtual import VirtualBus, Publisher, SyncSubscriber


def test_controller(config_path: Path, bus: VirtualBus) -> None:
    config_file = config_path / "controller_instance.yaml"

    config = RedSunSessionInfo.load_yaml(str(config_file))
    config_ctrl: dict[str, ControllerInfo] = {
        name: MockControllerInfo(**input)
        for name, input in config["controllers"].items()
    }

    assert len(config_ctrl) == 1

    for _, ctrl in config_ctrl.items():
        controller = MockController(cast(MockControllerInfo, ctrl), bus)
        assert controller.info == ctrl
        assert len(controller.plans) == 2
        assert controller.info.plugin_name == "N/A"
        assert controller.info.repository == "N/A"

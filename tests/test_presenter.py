from pathlib import Path
from typing import Mapping

from mocks import MockController, MockControllerInfo

from sunflare.config import PresenterInfo, RedSunSessionInfo
from sunflare.virtual import HasConnection, HasRegistration
from sunflare.presenter import (
    Connection,
    Presenter,
    PPresenter,
    Receiver,
    Sender,
    SenderReceiver,
)
from sunflare.model import PModel
from sunflare.virtual import Signal, VirtualBus


def test_protocol_controller(config_path: Path, bus: VirtualBus) -> None:
    config_file = config_path / "controller_instance.yaml"

    config = RedSunSessionInfo.load_yaml(str(config_file))
    config_ctrl: dict[str, PresenterInfo] = {
        name: MockControllerInfo(**input)
        for name, input in config["controllers"].items()
    }

    assert len(config_ctrl) == 1

    for _, ctrl in config_ctrl.items():
        controller = MockController(ctrl, {}, bus)
        assert isinstance(controller, PPresenter)
        assert controller.info == ctrl
        assert len(controller.plans) == 2
        assert controller.info.plugin_name == "mocks"
        assert controller.info.plugin_id == "mock_controller"


def test_base_controller(bus: VirtualBus) -> None:
    class TestController(Presenter[PresenterInfo]):
        # changing the name of __init__ parameters does not
        # affect the protocol behavior
        def __init__(
            self,
            info: PresenterInfo,
            test_models: Mapping[str, PModel],
            bus: VirtualBus,
        ) -> None:
            super().__init__(info, test_models, bus)

    ctrl_info = PresenterInfo(plugin_name="mocks", plugin_id="mock_controller")
    ctrl = TestController(ctrl_info, {}, bus)

    assert isinstance(ctrl, PPresenter)


def test_sender_controller(bus: VirtualBus) -> None:
    cnt = 0

    def mock_slot() -> None:
        nonlocal cnt
        cnt += 1

    class TestController(Sender[PresenterInfo]):
        dummySignal = Signal()

        def __init__(
            self,
            info: PresenterInfo,
            test_models: Mapping[str, PModel],
            bus: VirtualBus,
        ) -> None:
            super().__init__(info, test_models, bus)

    info = PresenterInfo(plugin_name="mocks", plugin_id="mock_controller")
    ctrl = TestController(info, {}, bus)

    assert isinstance(ctrl, PPresenter)
    assert isinstance(ctrl, HasRegistration)

    ctrl.registration_phase()

    assert len(bus.signals) == 1
    assert len(bus.signals[ctrl.__class__.__name__]) == 1
    assert bus.signals[ctrl.__class__.__name__]["dummySignal"] == ctrl.dummySignal

    bus.signals[ctrl.__class__.__name__]["dummySignal"].connect(mock_slot)

    ctrl.dummySignal.emit()

    assert cnt == 1


def test_receiver_controller(bus: VirtualBus) -> None:
    cnt = 0

    class DummySender(Sender[PresenterInfo]):
        dummySignal = Signal()

        def __init__(
            self,
            info: PresenterInfo,
            test_models: Mapping[str, PModel],
            bus: VirtualBus,
        ) -> None:
            super().__init__(info, test_models, bus)

    class TestController(Receiver[PresenterInfo]):
        def __init__(
            self,
            info: PresenterInfo,
            test_models: Mapping[str, PModel],
            bus: VirtualBus,
        ) -> None:
            connection_map = {
                "DummySender": [Connection(signal="dummySignal", slot=self.mock_slot)]
            }
            super().__init__(info, test_models, bus, connection_map=connection_map)

        def mock_slot(self) -> None:
            nonlocal cnt
            cnt += 1

    info = PresenterInfo(plugin_name="mocks", plugin_id="mock_controller")
    sender = DummySender(info, {}, bus)
    ctrl = TestController(info, {}, bus)

    assert isinstance(ctrl, PPresenter)
    assert isinstance(ctrl, HasConnection)

    sender.registration_phase()
    ctrl.connection_phase()

    assert len(bus.signals) == 1
    assert len(bus.signals["DummySender"]) == 1
    assert bus.signals["DummySender"]["dummySignal"] == sender.dummySignal

    sender.dummySignal.emit()

    assert cnt == 1


def test_sender_receiver(bus: VirtualBus) -> None:
    cnt = 0

    class TestController(SenderReceiver[PresenterInfo]):
        dummySignal = Signal()

        def __init__(
            self,
            info: PresenterInfo,
            test_models: Mapping[str, PModel],
            bus: VirtualBus,
        ) -> None:
            # connect to myself...
            # ... for testing, ya know
            connection_map = {
                "TestController": [
                    Connection(signal="dummySignal", slot=self.mock_slot)
                ]
            }
            super().__init__(info, test_models, bus, connection_map=connection_map)

        def mock_slot(self) -> None:
            nonlocal cnt
            cnt += 1

    info = PresenterInfo(plugin_name="mocks", plugin_id="mock_controller")
    ctrl = TestController(info, {}, bus)

    assert isinstance(ctrl, PPresenter)
    assert isinstance(ctrl, HasRegistration)
    assert isinstance(ctrl, HasConnection)

    ctrl.registration_phase()
    ctrl.connection_phase()

    assert len(bus.signals) == 1
    assert len(bus.signals["TestController"]) == 1
    assert bus.signals["TestController"]["dummySignal"] == ctrl.dummySignal

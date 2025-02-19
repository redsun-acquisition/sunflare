from pathlib import Path
from typing import cast, Mapping

from mocks import MockController, MockControllerInfo

from sunflare.model import ModelProtocol
from sunflare.config import ControllerInfo, RedSunSessionInfo
from sunflare.controller import Controller, ControllerProtocol, Sender, HasRegistration, Receiver, HasConnection, SenderReceiver, Connection
from sunflare.virtual import VirtualBus, Signal


def test_protocol_controller(config_path: Path, bus: VirtualBus) -> None:
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

def test_base_controller(bus: VirtualBus) -> None:
    
    class TestInfo(ControllerInfo):
        def __init__(self, **kwargs) -> None:
            super().__init__(**kwargs)
    
    class TestController(Controller[TestInfo]):
        # changing the name of __init__ parameters does not
        # affect the protocol behavior
        def __init__(self, info: TestInfo, test_models: Mapping[str, ModelProtocol], bus: VirtualBus) -> None:
            super().__init__(info, test_models, bus)

    ctrl_info = TestInfo()
    ctrl = TestController(ctrl_info, {}, bus)

    assert isinstance(ctrl, ControllerProtocol)

def test_sender_controller(bus: VirtualBus) -> None:

    cnt = 0

    def mock_slot() -> None:
        nonlocal cnt
        cnt += 1

    class TestInfo(ControllerInfo):
        def __init__(self, **kwargs) -> None:
            super().__init__(**kwargs)

    class TestController(Sender[TestInfo]):

        dummySignal = Signal()

        def __init__(self, info: TestInfo, test_models: Mapping[str, ModelProtocol], bus: VirtualBus) -> None:
            super().__init__(info, test_models, bus)

    info = TestInfo()
    ctrl = TestController(info, {}, bus)

    assert isinstance(ctrl, ControllerProtocol)
    assert isinstance(ctrl, HasRegistration)

    ctrl.registration_phase()

    assert len(bus._cache) == 1
    assert len(bus._cache[ctrl.__class__.__name__]) == 1
    assert bus._cache[ctrl.__class__.__name__]["dummySignal"] == ctrl.dummySignal

    bus[ctrl.__class__.__name__]["dummySignal"].connect(mock_slot)

    ctrl.dummySignal.emit()

    assert cnt == 1

def test_receiver_controller(bus: VirtualBus) -> None:
    
    cnt = 0

    class TestInfo(ControllerInfo):
        def __init__(self, **kwargs) -> None:
            super().__init__(**kwargs)

    class DummySender(Sender[TestInfo]):
        dummySignal = Signal()

        def __init__(self, info: TestInfo, test_models: Mapping[str, ModelProtocol], bus: VirtualBus) -> None:
            super().__init__(info, test_models, bus)

    class TestController(Receiver[TestInfo]):

        def __init__(self, info: TestInfo, test_models: Mapping[str, ModelProtocol], bus: VirtualBus) -> None:
            connection_map = {
                "DummySender": [Connection(signal="dummySignal", slot=self.mock_slot)]
            }
            super().__init__(info, test_models, bus, connection_map=connection_map)

        def mock_slot(self) -> None:
            nonlocal cnt
            cnt += 1

    info = TestInfo()
    sender = DummySender(info, {}, bus)
    ctrl = TestController(info, {}, bus)

    assert isinstance(ctrl, ControllerProtocol)
    assert isinstance(ctrl, HasConnection)

    sender.registration_phase()
    ctrl.connection_phase()

    assert len(bus._cache) == 1
    assert len(bus._cache["DummySender"]) == 1
    assert bus._cache["DummySender"]["dummySignal"] == sender.dummySignal

    sender.dummySignal.emit()

    assert cnt == 1

def test_sender_receiver(bus: VirtualBus) -> None:
    
    cnt = 0

    class TestInfo(ControllerInfo):
        def __init__(self, **kwargs) -> None:
            super().__init__(**kwargs)


    class TestController(SenderReceiver[TestInfo]):
        dummySignal = Signal()

        def __init__(self, info: TestInfo, test_models: Mapping[str, ModelProtocol], bus: VirtualBus) -> None:
            # connect to myself...
            # ... for testing, ya know
            connection_map = {
                "TestController": [Connection(signal="dummySignal", slot=self.mock_slot)]
            }
            super().__init__(info, test_models, bus, connection_map=connection_map)

        def mock_slot(self) -> None:
            nonlocal cnt
            cnt += 1


    info = TestInfo()
    ctrl = TestController(info, {}, bus)

    assert isinstance(ctrl, ControllerProtocol)
    assert isinstance(ctrl, HasRegistration)
    assert isinstance(ctrl, HasConnection)

    ctrl.registration_phase()
    ctrl.connection_phase()

    assert len(bus._cache) == 1
    assert len(bus._cache["TestController"]) == 1
    assert bus._cache["TestController"]["dummySignal"] == ctrl.dummySignal

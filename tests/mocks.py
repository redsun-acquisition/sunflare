from typing import Any
from functools import partial

from attrs import define, field, validators

from sunflare.config import ModelInfo, ControllerInfo
from sunflare.model import ModelProtocol
from sunflare.controller import ControllerProtocol
from sunflare.virtual import VirtualBus, Signal

from bluesky.run_engine import RunEngine
from bluesky.protocols import Reading
from bluesky.utils import MsgGenerator
from bluesky.plan_stubs import open_run, close_run, read, rel_set

from event_model.documents.event_descriptor import DataKey

class MockVirtualBus(VirtualBus):
    sigFoo = Signal()

class ReadableModel(ModelProtocol):

    def read(self) -> dict[str, Any]:
        raise NotImplemented
    
class SettableModel(ModelProtocol):
    
    def set(value: Any) -> None:
        raise NotImplemented      

@define
class MockDetectorInfo(ModelInfo):
    sensor_size: tuple[int, int] = field(converter=tuple)
    exposure_egu: str = field(default="ms", converter=str)
    pixel_size: tuple[int, int, int] = field(default=(1, 1, 1), converter=tuple)

    @sensor_size.validator
    def _validate_size(self, _: str, value: tuple[int, int]) -> None:
        """Check that the sensor size is a tuple of two positive integers."""
        if any([x <= 0 for x in value]):
            raise ValueError("Sensor size must be a tuple of positive integers.")
        if len(value) != 2:
            raise ValueError("Sensor size must be a tuple of two integers.")

    @pixel_size.validator
    def _validate_pixels_size(self, _: str, value: tuple[int, int, int]) -> None:
        """Check that the pixel size is a tuple of three positive integers."""
        if any([x <= 0 for x in value]):
            raise ValueError("Pixel size must be a tuple of positive integers.")
        if len(value) != 3:
            raise ValueError("Pixel size must be a tuple of three integers.")

def _convert_axes(value: list[Any]) -> list[str]:
    """Convert a list of elements to a list of strings."""
    return [str(x) for x in value]

@define
class MockMotorInfo(ModelInfo):
    step_egu: str = field(default="μm", validator=validators.instance_of(str))
    axes: list[str] = field(factory=list, converter=_convert_axes)

    @axes.validator
    def _validate_axes(self, _: str, value: list[str]) -> None:
        """Check that all the elements of the axes are list of capital letter strings."""
        if not all([x.isalpha() for x in value]):
            raise ValueError("Axes must be a list of strings.")
        if len (value) == 0:
            raise ValueError("Axes must be a list of strings.")
        if not all([len(x) == 1 for x in value]):
            raise ValueError("Axes must be a list of single characters.")
        if not all([x.isupper() for x in value]):
            raise ValueError("Axes must be a list of capital letters.")
        
@define
class MockControllerInfo(ControllerInfo):
    integer: int = field(validator=validators.instance_of(int))
    floating: float = field(validator=validators.instance_of(float))
    boolean: bool = field(validator=validators.instance_of(bool))
    string: str = field(validator=validators.instance_of(str))

class MockDetector(ReadableModel):
    """Mock detector model."""

    def __init__(self, name: str, cfg_info: MockDetectorInfo) -> None:
        self._name = name
        self._cfg_info = cfg_info        

    def read(self) -> dict[str, Any]:
        raise NotImplemented
    
    def read_configuration(self) -> dict[str, Reading[Any]]:
        raise NotImplemented
    
    def describe_configuration(self) -> dict[str, DataKey]:
        raise NotImplemented

    def configure(self, name: str, value: Any, /, **kwargs: Any) -> None:
        raise NotImplemented

    def shutdown(self) -> None:
        ...

    @property
    def name(self) -> str:
        return self._name
    
    @property
    def parent(self) -> None:
        return None
    
    @property
    def model_info(self) -> MockDetectorInfo:
        return self._cfg_info

class MockMotor(SettableModel):
    """Mock motor model."""

    def __init__(self, name: str, cfg_info: MockMotorInfo) -> None:
        self._name = name
        self._cfg_info = cfg_info

    def set(value: Any) -> None:
        raise NotImplemented
    
    def read_configuration(self) -> dict[str, Reading[Any]]:
        raise NotImplemented
    
    def describe_configuration(self) -> dict[str, DataKey]:
        raise NotImplemented
    
    def configure(self, name: str, value: Any, /, **kwargs: Any) -> None:
        raise NotImplemented
    
    def shutdown(self) -> None:
        ...
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def parent(self) -> None:
        return None
    
    @property
    def model_info(self) -> MockMotorInfo:
        return self._cfg_info


mock_detector_info = MockDetectorInfo(
    model_name="MockDetectorModel",
    sensor_size=(1024, 1024),
    exposure_egu="ms",
    pixel_size=(1, 1, 1)
)

mock_motor_info = MockMotorInfo(
    model_name="MockMotorModel",
    step_egu="μm",
    axes=["X", "Y", "Z"]
)

mock_motor = MockMotor("motor", mock_motor_info)
mock_detector = MockDetector("detector", mock_detector_info)

class MockController(ControllerProtocol):

    sigBar = Signal()
    sigNewPlan = Signal(object)

    def __init__(self, 
                ctrl_info: MockControllerInfo,
                virtual_bus: MockVirtualBus) -> None:
        self._ctrl_info = ctrl_info
        self._engine = RunEngine({})
        self._virtual_bus = virtual_bus
        self._plans: list[partial[MsgGenerator[Any]]] = []

        def mock_plan_no_device() -> MsgGenerator[Any]:
            yield from [open_run(), close_run()]
        
        def mock_plan_device(det: ReadableModel, mot: SettableModel) -> MsgGenerator[Any]:
            yield from open_run()
            yield from read(det)
            yield from rel_set(mot, 1)
            yield from close_run()

        self._plans.append(partial(mock_plan_no_device))
        self._plans.append(partial(mock_plan_device, mock_detector, mock_motor))
        

    def registration_phase(self) -> None:
        ...
    
    def connection_phase(self) -> None:
        ...
    
    def shutdown(self) -> None:
        ...
    
    @property
    def controller_info(self) -> MockControllerInfo:
        return self._ctrl_info

    @property
    def plans(self) -> list[partial[MsgGenerator[Any]]]:
        return self._plans

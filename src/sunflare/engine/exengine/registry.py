"""ExEngine device registry module."""

from typing import TYPE_CHECKING

from sunflare.engine.registry import DeviceRegistry

if TYPE_CHECKING:
    from typing import Union, TypeAlias

    from sunflare.virtualbus import VirtualBus

    from .motor import (
        ExEngineSingleMotorModel,
        ExEngineMMSingleMotorModel,
        ExEngineDoubleMotorModel,
        ExEngineMMDoubleMotorModel,
    )
    from .detector import ExEngineDetectorModel, ExEngineMMCameraModel

ExEngineMotor: TypeAlias = Union[
    ExEngineSingleMotorModel,
    ExEngineMMSingleMotorModel,
    ExEngineDoubleMotorModel,
    ExEngineMMDoubleMotorModel,
]
ExEngineDetector: TypeAlias = Union[ExEngineDetectorModel, ExEngineMMCameraModel]

Registry: TypeAlias = dict[str, Union[ExEngineMotor, ExEngineDetector]]


class ExEngineDeviceRegistry(DeviceRegistry[ExEngineMotor, ExEngineDetector]):
    """Bluesky device registry class."""

    def __init__(
        self,
        virtual_bus: VirtualBus,
        module_bus: VirtualBus,
    ) -> None:
        self._virtual_bus = virtual_bus
        self._module_bus = module_bus
        self._motors: dict[str, ExEngineMotor] = dict()
        self._detectors: dict[str, ExEngineDetector] = dict()

    @property
    def motors(self) -> dict[str, ExEngineMotor]:
        """Get the motors dictionary."""
        return self._motors

    @property
    def detectors(self) -> dict[str, ExEngineDetector]:
        """Get the detectors dictionary."""
        return self._detectors

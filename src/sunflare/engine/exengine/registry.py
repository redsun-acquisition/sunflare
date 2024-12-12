"""ExEngine device registry module."""

from typing import TYPE_CHECKING, cast

from sunflare.engine.registry import DeviceRegistry

if TYPE_CHECKING:
    from typing import Union, TypeAlias, Literal

    from sunflare.config import RedSunInstanceInfo
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
        config: RedSunInstanceInfo,
        virtual_bus: VirtualBus,
        module_bus: VirtualBus,
    ) -> None:
        self._config = config
        self._virtual_bus = virtual_bus
        self._module_bus = module_bus
        self._motors: dict[str, ExEngineMotor] = dict()
        self._detectors: dict[str, ExEngineDetector] = dict()

    def registration_phase(self) -> None:  # noqa: D102
        # nothing to do
        ...

    def connection_phase(self) -> None:  # noqa: D102
        # sigNewDevices is defined in the HardwareVirtualBus class,
        # which is declared in the Redsun package;
        # it is not accessed in order to avoid circular imports;
        # this signal is built-in and not exposed to other users so it's safe to ignore
        self._virtual_bus.sigNewDevices.connect(self._on_new_devices)  # type: ignore

    @property
    def motors(self) -> dict[str, ExEngineMotor]:
        """Get the motors dictionary."""
        return self._motors

    @property
    def detectors(self) -> dict[str, ExEngineDetector]:
        """Get the detectors dictionary."""
        return self._detectors

    def _on_new_devices(
        self, group: Literal["motors", "detectors"], devices: Registry
    ) -> None:
        """Add the newly created devices to the respective dictionaries.

        Parameters
        ----------
        group : str
            The group of the devices.
        devices : dict[str, dict[str, str]]
            The dictionary of newly built devices.
        """
        if group == "motors":
            self._motors.update(cast(dict[str, ExEngineMotor], devices))
        elif group == "detectors":
            self._detectors.update(cast(dict[str, ExEngineDetector], devices))
        else:
            raise ValueError(f"Invalid group: {group}")

"""Bluesky device registry module."""

from __future__ import annotations

from typing import TYPE_CHECKING, TypeAlias

from sunflare.engine.registry import DeviceRegistry

if TYPE_CHECKING:
    from typing import Union

    from sunflare.virtualbus import VirtualBus

    from .motor import BlueskyMotorModel
    from .detector import BlueskyDetectorModel

Registry: TypeAlias = dict[str, Union[BlueskyDetectorModel, BlueskyMotorModel]]


class BlueskyDeviceRegistry(DeviceRegistry[BlueskyMotorModel, BlueskyDetectorModel]):
    """Bluesky device registry class."""

    def __init__(
        self,
        virtual_bus: VirtualBus,
        module_bus: VirtualBus,
    ) -> None:
        self._virtual_bus = virtual_bus
        self._module_bus = module_bus
        self._motors: dict[str, BlueskyMotorModel] = {}
        self._detectors: dict[str, BlueskyDetectorModel] = {}

    @property
    def motors(self) -> dict[str, BlueskyMotorModel]:
        """Get the motors dictionary."""
        return self._motors

    @property
    def detectors(self) -> dict[str, BlueskyDetectorModel]:
        """Get the detectors dictionary."""
        return self._detectors

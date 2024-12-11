"""Bluesky device registry module."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sunflare.engine.registry import DeviceRegistry

if TYPE_CHECKING:
    from sunflare.config import RedSunInstanceInfo
    from sunflare.virtualbus import VirtualBus

    from .motor import BlueskyMotorModel
    from .detector import BlueskyDetectorModel


class BlueskyDeviceRegistry(DeviceRegistry[BlueskyMotorModel, BlueskyDetectorModel]):
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
        self._motors: dict[str, BlueskyMotorModel] = dict()
        self._detectors: dict[str, BlueskyDetectorModel] = dict()

    @property
    def motors(self) -> dict[str, BlueskyMotorModel]:
        """Get the motors dictionary."""
        return self._motors

    @property
    def detectors(self) -> dict[str, BlueskyDetectorModel]:
        """Get the detectors dictionary."""
        return self._detectors

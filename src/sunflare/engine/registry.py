"""Bluesky device registry module."""

from __future__ import annotations

from sunflare.virtualbus import VirtualBus
from sunflare.engine.motor import MotorProtocol
from sunflare.engine.detector import DetectorProtocol


class DeviceRegistry:
    """Bluesky device registry class."""

    def __init__(
        self,
        virtual_bus: VirtualBus,
        module_bus: VirtualBus,
    ) -> None:
        self._virtual_bus = virtual_bus
        self._module_bus = module_bus
        self._motors: dict[str, MotorProtocol] = {}
        self._detectors: dict[str, DetectorProtocol] = {}

    @property
    def motors(self) -> dict[str, MotorProtocol]:
        """Get the motors dictionary."""
        return self._motors

    @property
    def detectors(self) -> dict[str, DetectorProtocol]:
        """Get the detectors dictionary."""
        return self._detectors

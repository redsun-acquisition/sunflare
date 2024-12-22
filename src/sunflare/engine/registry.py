"""``registry`` module."""

from __future__ import annotations

from sunflare.engine.detector import DetectorProtocol
from sunflare.engine.motor import MotorProtocol
from sunflare.virtualbus import VirtualBus


class DeviceRegistry:
    """Device registry class.

    The registry holds references to the devices currently loaded in RedSun;
    it provides a unique point of interaction for controllers to actively manage workflows
    and assign specific devices to them.

    Parameters
    ----------
    virtual_bus: :class:`~sunflare.virtualbus.VirtualBus`
        Intra-module communication bus.
    module_bus: :class:`~sunflare.virtualbus.VirtualBus`
        Inter-module communication bus.
    """

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

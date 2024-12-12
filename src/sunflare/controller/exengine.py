"""ExEngine base controller module."""

from __future__ import annotations

from typing import TYPE_CHECKING

from abc import ABCMeta

from .base import ControllerProtocol

from sunflare.log import Loggable

if TYPE_CHECKING:
    from sunflare.config import ControllerInfo
    from sunflare.virtualbus import VirtualBus
    from sunflare.engine.exengine.registry import ExEngineDeviceRegistry


class ExEngineController(
    ControllerProtocol[ExEngineDeviceRegistry], Loggable, metaclass=ABCMeta
):
    """ExEngine base controller class."""

    def __init__(
        self,
        ctrl_info: ControllerInfo,
        registry: ExEngineDeviceRegistry,
        virtual_bus: VirtualBus,
        module_bus: VirtualBus,
    ) -> None:
        self._registry = registry
        self._ctrl_info = ctrl_info
        self._virtual_bus = virtual_bus
        self._module_bus = module_bus

    @property
    def registry(self) -> ExEngineDeviceRegistry:
        """ExEngine device registry."""
        return self._registry

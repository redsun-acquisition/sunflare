"""ExEngine base controller module."""

from typing import TYPE_CHECKING

from abc import ABCMeta

from .base import AbstractController

from sunflare.log import Loggable

if TYPE_CHECKING:
    from sunflare.config import ControllerInfo
    from sunflare.virtualbus import VirtualBus
    from sunflare.engine.exengine.registry import ExEngineDeviceRegistry


class ExEngineController(
    AbstractController["ExEngineDeviceRegistry"], Loggable, metaclass=ABCMeta
):
    """ExEngine base controller class."""

    def __init__(
        self,
        ctrl_info: "ControllerInfo",
        registry: "ExEngineDeviceRegistry",
        virtual_bus: "VirtualBus",
        module_bus: "VirtualBus",
    ) -> None:
        super().__init__(ctrl_info, registry, virtual_bus, module_bus)

    @property
    def registry(self) -> "ExEngineDeviceRegistry":
        """ExEngine device registry."""
        return self._registry

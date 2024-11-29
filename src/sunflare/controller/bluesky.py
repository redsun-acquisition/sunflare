"""Bluesky base controller module."""

from typing import TYPE_CHECKING

from abc import ABCMeta

from .base import AbstractController

if TYPE_CHECKING:
    from sunflare.config import ControllerInfo
    from sunflare.virtualbus import VirtualBus
    from sunflare.engine.bluesky.registry import BlueskyDeviceRegistry


class BlueskyController(AbstractController["BlueskyDeviceRegistry"], metaclass=ABCMeta):
    """ExEngine base controller class."""

    def __init__(
        self,
        ctrl_info: "ControllerInfo",
        registry: "BlueskyDeviceRegistry",
        virtual_bus: "VirtualBus",
        module_bus: "VirtualBus",
    ) -> None:
        super().__init__(ctrl_info, registry, virtual_bus, module_bus)

    @property
    def registry(self) -> "BlueskyDeviceRegistry":
        """ExEngine device registry."""
        return self._registry

"""Bluesky base controller module."""

from __future__ import annotations

from abc import ABCMeta, abstractmethod

from .base import ControllerProtocol

from sunflare.config import ControllerInfo, ControllerTypes, AcquisitionEngineTypes
from sunflare.virtualbus import VirtualBus
from sunflare.engine.bluesky.registry import BlueskyDeviceRegistry


class BlueskyController(ControllerProtocol[BlueskyDeviceRegistry], metaclass=ABCMeta):
    """Bluesky base controller class."""

    def __init__(
        self,
        ctrl_info: ControllerInfo,
        registry: BlueskyDeviceRegistry,
        virtual_bus: VirtualBus,
        module_bus: VirtualBus,
    ) -> None:
        self._registry = registry
        self._ctrl_info = ctrl_info
        self._virtual_bus = virtual_bus
        self._module_bus = module_bus

    @abstractmethod
    def shutdown(self) -> None:  # noqa: D102
        # inherited docstring
        ...

    @abstractmethod
    def registration_phase(self) -> None:  # noqa: D102
        # inherited docstring
        ...

    @abstractmethod
    def connection_phase(self) -> None:  # noqa: D102
        # inherited docstring
        ...

    @property
    def category(self) -> "set[ControllerTypes]":  # noqa: D102
        return self._ctrl_info.category

    @property
    def controller_name(self) -> str:  # noqa: D102
        # inherited docstring
        return self._ctrl_info.controller_name

    @property
    def supported_engines(self) -> list[AcquisitionEngineTypes]:  # noqa: D102
        return self._ctrl_info.supported_engines

    @property
    def registry(self) -> BlueskyDeviceRegistry:  # noqa: D102
        return self._registry

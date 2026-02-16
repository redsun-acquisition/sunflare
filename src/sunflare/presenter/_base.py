from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from collections.abc import Mapping
    from typing import Any

    from sunflare.device import Device
    from sunflare.virtual import VirtualBus

__all__ = ["PPresenter", "Presenter"]


@runtime_checkable
class PPresenter(Protocol):  # pragma: no cover
    """Presenter protocol class.

    Provides the interface for a class
    that Redsun can recognize as a presenter by
    implementing the defined attributes.

    Attributes
    ----------
    devices : Mapping[str, sunflare.device.Device]
        Reference to the devices used in the presenter.
    virtual_bus : VirtualBus
        Reference to the virtual bus.
    """

    virtual_bus: VirtualBus
    devices: Mapping[str, Device]


class Presenter(PPresenter, ABC):
    """Presenter base class.

    Classes that do not directly inherit from it
    will need to match the `__init__` signature
    to ensure that at runtime Redsun registers
    them as virtual subclasses.

    Parameters
    ----------
    devices : Mapping[str, sunflare.device.Device]
        Reference to the devices used in the presenter.
    virtual_bus : sunflare.virtual.VirtualBus
        Reference to the virtual bus.
    kwargs : Any, optional
        Additional keyword arguments for presenter subclasses.
        These are parsed from the session configuration file.
    """

    @abstractmethod
    def __init__(
        self, devices: Mapping[str, Device], virtual_bus: VirtualBus, /, **kwargs: Any
    ) -> None:
        self.devices = devices
        self.virtual_bus = virtual_bus
        super().__init__(**kwargs)

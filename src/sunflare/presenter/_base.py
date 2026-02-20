from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from collections.abc import Mapping
    from typing import Any

    from sunflare.device import Device
    from sunflare.virtual import VirtualContainer

__all__ = ["PPresenter", "Presenter"]


@runtime_checkable
class PPresenter(Protocol):  # pragma: no cover
    """Presenter protocol class.

    Attributes
    ----------
    name : str
        Identity key of the presenter in the virtual container.
    devices : Mapping[str, sunflare.device.Device]
        Reference to the devices used in the presenter.
    virtual_container : VirtualContainer
        Reference to the virtual container.
    """

    name: str
    virtual_container: VirtualContainer
    devices: Mapping[str, Device]


class Presenter(PPresenter, ABC):
    """Presenter base class.

    Parameters
    ----------
    name : str
        Identity key of the presenter in the virtual container.
        Passed as positional-only argument.
    devices : Mapping[str, sunflare.device.Device]
        Reference to the devices used in the presenter.
    virtual_container : sunflare.virtual.VirtualContainer
        Reference to the virtual container.
    kwargs : Any, optional
        Additional keyword arguments for presenter subclasses.
        These are parsed from the session configuration file.
    """

    @abstractmethod
    def __init__(
        self,
        name: str,
        devices: Mapping[str, Device],
        virtual_container: VirtualContainer,
        /,
        **kwargs: Any,
    ) -> None:
        self.name = name
        self.devices = devices
        self.virtual_container = virtual_container
        super().__init__(**kwargs)

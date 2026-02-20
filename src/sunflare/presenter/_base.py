from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from collections.abc import Mapping
    from typing import Any

    from sunflare.device import Device

__all__ = ["PPresenter", "Presenter"]


@runtime_checkable
class PPresenter(Protocol):  # pragma: no cover
    """Presenter protocol class.

    Attributes
    ----------
    name : str
        Identity key of the presenter.
    devices : Mapping[str, sunflare.device.Device]
        Reference to the devices used in the presenter.

    Notes
    -----
    Access to the virtual container is optional and should be acquired
    by implementing :class:`~sunflare.virtual.IsProvider` or
    :class:`~sunflare.virtual.IsInjectable`.
    """

    name: str
    devices: Mapping[str, Device]


class Presenter(PPresenter, ABC):
    """Presenter base class.

    Parameters
    ----------
    name : str
        Identity key of the presenter. Passed as positional-only argument.
    devices : Mapping[str, sunflare.device.Device]
        Reference to the devices used in the presenter.
    kwargs : Any, optional
        Additional keyword arguments for presenter subclasses.
    """

    @abstractmethod
    def __init__(
        self,
        name: str,
        devices: Mapping[str, Device],
        /,
        **kwargs: Any,
    ) -> None:
        self.name = name
        self.devices = devices
        super().__init__(**kwargs)

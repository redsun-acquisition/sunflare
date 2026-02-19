from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from typing import Any

    from sunflare.view import ViewPosition
    from sunflare.virtual import VirtualBus


@runtime_checkable
class PView(Protocol):
    """Minimmal protocol a view component should implement.

    Attributes
    ----------
    virtual_bus : VirtualBus
        Main virtual bus for the Redsun instance.
    """

    virtual_bus: VirtualBus

    @property
    @abstractmethod
    def view_position(self) -> ViewPosition:
        """Position of the view component in the main view of the UI."""


class View(PView, ABC):
    """Base view class.

    Parameters
    ----------
    virtual_bus : VirtualBus
        Main virtual bus for the Redsun instance.
    kwargs : ``Any``, optional
        Additional keyword arguments for view subclasses.
    """

    @abstractmethod
    def __init__(self, virtual_bus: VirtualBus, /, **kwargs: Any) -> None:
        self.virtual_bus = virtual_bus
        super().__init__(**kwargs)

    @property
    @abstractmethod
    def view_position(self) -> ViewPosition:
        """Position of the view component in the main view of the UI."""

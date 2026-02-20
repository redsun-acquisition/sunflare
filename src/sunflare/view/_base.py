from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from typing import Any

    from sunflare.view import ViewPosition
    from sunflare.virtual import VirtualContainer


@runtime_checkable
class PView(Protocol):
    """Minimal protocol a view component should implement.

    Attributes
    ----------
    name : str
        Identity key of the view in the virtual container.
    virtual_container : VirtualContainer
        Main virtual container for the Redsun instance.
    """

    name: str
    virtual_container: VirtualContainer

    @property
    @abstractmethod
    def view_position(self) -> ViewPosition:
        """Position of the view component in the main view of the UI."""


class View(PView, ABC):
    """Base view class.

    Parameters
    ----------
    name : str
        Identity key of the view in the virtual container.
        Passed as positional-only argument.
    virtual_container : VirtualContainer
        Main virtual container for the Redsun instance.
    kwargs : ``Any``, optional
        Additional keyword arguments for view subclasses.
    """

    @abstractmethod
    def __init__(
        self,
        name: str,
        virtual_container: VirtualContainer,
        /,
        **kwargs: Any,
    ) -> None:
        self.name = name
        self.virtual_container = virtual_container
        super().__init__(**kwargs)

    @property
    @abstractmethod
    def view_position(self) -> ViewPosition:
        """Position of the view component in the main view of the UI."""

from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING

from qtpy.QtWidgets import QWidget

from sunflare.view import View

if TYPE_CHECKING:
    from typing import Any

    from sunflare.view import ViewPosition
    from sunflare.virtual import VirtualContainer


class QtView(QWidget):
    """Abstract base Qt widget implementing the View protocol.

    Parameters
    ----------
    name : str
        Identity key of the view in the virtual container.
        Passed as positional-only argument.
    virtual_container : VirtualContainer
        Main virtual container for the Redsun instance.
    kwargs : ``Any``, optional
        Additional keyword arguments for view subclasses.

    !!! note
        For `QtView` subclasses, `kwargs` are kept for consistency,
        but they're not passed to `super().__init__` since `QWidget` does not accept them.
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
        super().__init__()

    @property
    @abstractmethod
    def view_position(self) -> ViewPosition:
        """Position of the view component in the main view of the UI."""


View.register(QtView)  # type: ignore[type-abstract]

__all__ = ["QtView"]

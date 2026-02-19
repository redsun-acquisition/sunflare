from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING

from qtpy.QtWidgets import QWidget

from sunflare.view import View

if TYPE_CHECKING:
    from typing import Any

    from sunflare.view import ViewPosition
    from sunflare.virtual import VirtualBus


class QtView(QWidget):
    """Abstract base Qt widget implementing the View protocol.

    Parameters
    ----------
    virtual_bus : VirtualBus
        Main virtual bus for the Redsun instance.
    kwargs : ``Any``, optional
        Additional keyword arguments for view subclasses.

    !!! note
        For `QtView` subclasses, `kwargs` are kept for consistency,
        but they're not passed to `super().__init__` since `QWidget` does not accept them.
    """

    @abstractmethod
    def __init__(
        self,
        virtual_bus: VirtualBus,
        /,
        **kwargs: Any,
    ) -> None:
        self.virtual_bus = virtual_bus
        super().__init__()

    @property
    @abstractmethod
    def view_position(self) -> ViewPosition:
        """Position of the view component in the main view of the UI."""


# working with mixing QWidget with
# a non-Qt cooperative class causes MRO issues;
# our best bet is to just register the class
# as a virtual subclass of View and avoid direct inheritance;
# furthermore mypy complains that QWidget has
# __init__ marked as abstract method and causes it not to be
# directly instantiable; we can just ignore this
# as it is the duty of the concrete subclasses to directly
# implement __init__ and call super().__init__ to ensure proper initialization
View.register(QtView)  # type: ignore[type-abstract]

__all__ = ["QtView"]

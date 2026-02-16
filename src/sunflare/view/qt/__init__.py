from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING

from qtpy.QtWidgets import QWidget

from sunflare.view import View

if TYPE_CHECKING:
    from typing import Any

    from sunflare.virtual import VirtualBus


class QtView(QWidget):
    """Abstract base Qt widget implementing the View protocol.

    ``QtView`` does not directly inherit from :class:`~sunflare.view.View`
    to avoid MRO conflicts with Qt's cooperative ``__init__`` chain.
    It is registered as a virtual subclass of ``View`` so that
    ``isinstance(qt_view, View)`` returns ``True``.
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

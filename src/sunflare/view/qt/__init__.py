from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING

from qtpy.QtWidgets import QWidget

from sunflare.view import PView

if TYPE_CHECKING:
    from sunflare.virtual import VirtualBus

QWidgetMeta = type(QWidget)


# Create a common metaclass that inherits from both metaclasses.
# This apparently seem to work when launching redsun empty, but
# it has not been tested yet; anyway we keep mypy happy by ignoring it
# https://stackoverflow.com/a/76681565/4437552
class _QWidgetBaseMeta(QWidgetMeta, PView):  # type: ignore[valid-type,misc]
    """Common metaclass for QWidget and PView."""


class QtView(QWidget, metaclass=_QWidgetBaseMeta):
    """Qt base widget class that implemenents the PView.

    Parameters
    ----------
    virtual_bus : VirtualBus
        Virtual bus for the Redsun session.
    parent : QWidget | None, optional
        Parent widget. Default is `None`.
    """

    @abstractmethod
    def __init__(
        self,
        virtual_bus: VirtualBus,
        /,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent=parent)
        self.virtual_bus = virtual_bus


__all__ = ["QtView"]

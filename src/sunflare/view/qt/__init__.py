from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING

from qtpy.QtWidgets import QWidget

from sunflare.view import ViewProtocol

if TYPE_CHECKING:
    from typing import Any

    from sunflare.config import ViewInfoProtocol
    from sunflare.virtual import VirtualBus

QWidgetMeta = type(QWidget)


# Create a common metaclass that inherits from both metaclasses.
# This apparently seem to work when launching redsun empty, but
# it has not been tested yet; anyway we keep mypy happy by ignoring it
# https://stackoverflow.com/a/76681565/4437552
class _QWidgetBaseMeta(QWidgetMeta, ViewProtocol):  # type: ignore[valid-type,misc]
    """Common metaclass for QWidget and ViewProtocol."""


class BaseQtWidget(QWidget, metaclass=_QWidgetBaseMeta):
    """Qt base widget class that implemenents the ViewProtocol.

    Parameters
    ----------
    view_info : ViewInfo
        View information.
    virtual_bus : VirtualBus
        Virtual bus for the Redsun session.
    """

    @abstractmethod
    def __init__(
        self,
        view_info: ViewInfoProtocol,
        virtual_bus: VirtualBus,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.view_info = view_info
        self.virtual_bus = virtual_bus


__all__ = ["BaseQtWidget"]

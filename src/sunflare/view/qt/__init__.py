from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING

from qtpy.QtWidgets import QWidget

from sunflare.view import WidgetProtocol

if TYPE_CHECKING:
    from typing import Any

    from sunflare.config import RedSunSessionInfo
    from sunflare.virtual import VirtualBus

QWidgetMeta = type(QWidget)


# Create a common metaclass that inherits from both metaclasses.
# This apparently seem to work when launching redsun empty, but
# it has not been tested yet; anyway we keep mypy happy by ignoring it
# https://stackoverflow.com/a/76681565/4437552
class _QWidgetBaseMeta(QWidgetMeta, WidgetProtocol):  # type: ignore[valid-type,misc]
    """Common metaclass for QWidget and WidgetProtocol."""


class BaseQtWidget(QWidget, metaclass=_QWidgetBaseMeta):
    """Qt base widget class that implemenents the WidgetProtocol.

    Parameters
    ----------
    config : RedSunSessionInfo
        The session configuration.
    virtual_bus : VirtualBus
        Virtual bus for the Redsun session.
    *args : Any
        Additional positional arguments for QWidget.
    **kwargs : Any
        Additional keyword arguments for QWidget.
    """

    @abstractmethod
    def __init__(
        self,
        config: RedSunSessionInfo,
        virtual_bus: VirtualBus,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.config = config
        self.virtual_bus = virtual_bus


__all__ = ["BaseQtWidget"]

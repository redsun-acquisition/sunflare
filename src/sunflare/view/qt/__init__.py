from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING

from qtpy.QtWidgets import QWidget

from sunflare.view import WidgetProtocol

if TYPE_CHECKING:
    from typing import Any

    from sunflare.config import RedSunSessionInfo
    from sunflare.virtual import VirtualBus


class BaseQtWidget(QWidget, WidgetProtocol):
    """Qt base widget class that implemenents the WidgetProtocol.

    Parameters
    ----------
    config : RedSunSessionInfo
        The session configuration.
    virtual_bus : VirtualBus
        Virtual bus for the RedSun session.
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
        self._config = config
        self._virtual_bus = virtual_bus

    @abstractmethod
    def registration_phase(self) -> None:  # noqa: D102
        ...

    @abstractmethod
    def connection_phase(self) -> None:  # noqa: D102
        ...

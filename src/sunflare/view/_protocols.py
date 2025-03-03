from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, runtime_checkable

from typing_extensions import Protocol

if TYPE_CHECKING:
    from typing import Any

    from sunflare.config import RedSunSessionInfo
    from sunflare.virtual import VirtualBus


@runtime_checkable
class WidgetProtocol(Protocol):
    """Minimmal protocol a widget should implement.

    All widgets, regardless of the chosen front-end,
    must implement the methods defined in this protocol.

    Parameters
    ----------
    config : RedSunSessionInfo
        The Redsun instance configuration.
    virtual_bus : VirtualBus
        Main virtual bus for the Redsun instance.
    """

    @abstractmethod
    def __init__(
        self,
        config: RedSunSessionInfo,
        virtual_bus: VirtualBus,
        *args: Any,
        **kwargs: Any,
    ) -> None: ...

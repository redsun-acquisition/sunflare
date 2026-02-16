from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from typing import Any

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


class View(PView, ABC):
    """Base view class.

    Classes that do not directly inherit from it
    will need to match the ``__init__`` signature
    to ensure that at runtime Redsun registers
    them as valid view components.
    """

    @abstractmethod
    def __init__(self, virtual_bus: VirtualBus, /, **kwargs: Any) -> None:
        self.virtual_bus = virtual_bus

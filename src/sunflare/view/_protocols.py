from __future__ import annotations

from typing import TYPE_CHECKING

from typing_extensions import Protocol, runtime_checkable

if TYPE_CHECKING:
    from sunflare.config import PViewInfo
    from sunflare.virtual import VirtualBus


@runtime_checkable
class ViewProtocol(Protocol):
    """Minimmal protocol a view component should implement.

    All views, regardless of the chosen front-end,
    must implement the methods defined in this protocol.

    Attributes
    ----------
    view_info : ViewInfo
        View information model.
    virtual_bus : VirtualBus
        Main virtual bus for the Redsun instance.
    """

    view_info: PViewInfo
    virtual_bus: VirtualBus

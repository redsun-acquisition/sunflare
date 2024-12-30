"""Models represent device interfaces that Bluesky can interact with.

Models are "providers", meaning that they offer a subset of Bluesky protocols to execute actions.
A minimal recognizable device in RedSun must implement the :class:`~sunflare.model.DeviceProtocol` protocol.
"""

from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from typing import Any, Optional

    from sunflare.config import ModelInfo

__all__ = ["ModelProtocol"]


@runtime_checkable
class ModelProtocol(Protocol):
    """Minimal required protocol for a recognizable device in RedSun.

    Implements the following protocols:

    - :class:`~bluesky.protocols.HasName`
    - :class:`~bluesky.protocols.HasParent`
    """

    @abstractmethod
    def __init__(self, name: str, model_info: ModelInfo) -> None: ...

    @property
    @abstractmethod
    def name(self) -> str:
        """Used to populate object_keys in the Event DataKey.

        https://blueskyproject.io/event-model/event-descriptors.html#object-keys
        """
        ...

    @property
    @abstractmethod
    def parent(self) -> Optional[Any]:
        """``None``, or a reference to a parent device.

        Used by the RE to stop duplicate stages.
        """
        ...

    @property
    @abstractmethod
    def model_info(self) -> ModelInfo:
        """The object associated model information.

        Must be a subclass of :class:`~sunflare.config.DeviceModelInfo`.
        """
        ...

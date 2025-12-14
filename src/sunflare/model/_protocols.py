from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, Any

from bluesky.protocols import Configurable, HasName, HasParent
from typing_extensions import Protocol, runtime_checkable

if TYPE_CHECKING:
    from sunflare.config import ModelInfoProtocol

__all__ = ["ModelProtocol"]


@runtime_checkable
class ModelProtocol(
    HasName, HasParent, Configurable[Any], Protocol
):  # pragma: no cover
    """Minimal required protocol for a recognizable device in Redsun.

    Exposes the following Bluesky protocols:

    - :class:`~bluesky.protocols.HasName`
    - :class:`~bluesky.protocols.HasParent`
    - :class:`~bluesky.protocols.Configurable`
    """

    @property
    @abstractmethod
    def model_info(self) -> ModelInfoProtocol:
        """The associated model information.

        It can return a subclass of :class:`~sunflare.config.ModelInfo`.
        """
        ...

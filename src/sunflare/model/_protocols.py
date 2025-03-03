from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, runtime_checkable

from typing_extensions import Protocol

if TYPE_CHECKING:
    from typing import Any, Optional

    from bluesky.protocols import Descriptor, Reading, SyncOrAsync

    from sunflare.config import ModelInfoProtocol

__all__ = ["ModelProtocol"]


@runtime_checkable
class ModelProtocol(Protocol):  # pragma: no cover
    """Minimal required protocol for a recognizable device in Redsun.

    Exposes the following Bluesky protocols:

    - :class:`~bluesky.protocols.HasName`
    - :class:`~bluesky.protocols.HasParent`
    - :class:`~bluesky.protocols.Configurable`

    Parameters
    ----------
    name : ``str``
        Name of the model. Serves as a unique identifier for the object created from it.
    model_info : :class:`~sunflare.config.ModelInfoProtocol`
        Object implementing :class:`~sunflare.config.ModelInfoProtocol`.
    """

    @abstractmethod
    def __init__(self, name: str, model_info: ModelInfoProtocol) -> None: ...

    @abstractmethod
    def read_configuration(self) -> SyncOrAsync[dict[str, Reading[Any]]]:
        """Read the model configuration.

        Provides a dictionary with the current values of the model configuration.

        The method can be normal or `async`.

        Returns
        -------
        dict[``str``, :class:`~bluesky.protocols.Reading`]
            A dictionary with the current values of the model configuration.
        """
        ...

    @abstractmethod
    def describe_configuration(self) -> SyncOrAsync[dict[str, Descriptor]]:
        """Describe the model configuration.

        Provides a description of each field of the model configuration.

        The method can be normal or `async`.

        Returns
        -------
        dict[``str``, :class:`~bluesky.protocols.Descriptor`]
            A dictionary with the description of each field of the model configuration.
        """
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        """Model identifier.

        Used to populate object_keys in :class:`~event_model.DataKey`.

        See the following link for more information:
        https://blueskyproject.io/event-model/main/explanations/event-descriptors.html
        """
        ...

    @property
    @abstractmethod
    def parent(self) -> Optional[Any]:
        """``None``, or a reference to a parent device.

        Used by the RE to stop duplicate stages.
        In Redsun (for now) should always return ``None``.
        """
        ...

    @property
    @abstractmethod
    def model_info(self) -> ModelInfoProtocol:
        """The associated model information.

        It can return a subclass of :class:`~sunflare.config.ModelInfo`.
        """
        ...

"""Models represent device interfaces that Bluesky can interact with.

Models offer a subset of Bluesky protocols to execute actions.
A minimal recognizable device in RedSun must implement the :class:`~sunflare.model.ModelProtocol` protocol.
"""

from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from typing import Any, Optional

    from bluesky.protocols import Reading, SyncOrAsync
    from event_model.documents.event_descriptor import DataKey

    from sunflare.config import ModelInfo

__all__ = ["ModelProtocol"]


@runtime_checkable
class ModelProtocol(Protocol):
    """Minimal required protocol for a recognizable device in RedSun.

    Implements the following protocols:

    - :class:`~bluesky.protocols.HasName`
    - :class:`~bluesky.protocols.HasParent`
    - :class:`~bluesky.protocols.Configurable`
    """

    @abstractmethod
    def __init__(self, name: str, model_info: ModelInfo) -> None: ...

    @abstractmethod
    def configure(self, name: str, value: Any) -> None:
        """Configure the model.

        Parameters
        ----------
        name : ``str``
            The name of the configuration parameter to set.
        value : ``Any``
            The value to set for the configuration parameter.
        """
        ...

    @abstractmethod
    def read_configuration(self) -> SyncOrAsync[dict[str, Reading[Any]]]:
        """Read the model configuration.

        Provides a dictionary with the current values of the model configuration.

        Returns
        -------
        ``dict[str, Reading]``
            A dictionary with the current values of the model configuration.
        """
        ...

    @abstractmethod
    def describe_configuration(self) -> SyncOrAsync[dict[str, DataKey]]:
        """Describe the model configuration.

        Provides a description of each field of the model configuration.

        Returns
        -------
        ``dict[str, DataKey]``
            A dictionary with the description of each field of the model configuration.
        """
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        """Model identifier.

        Used to populate object_keys in the Event DataKey.

        See the following link for more information:
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

        Must be a subclass of :class:`~sunflare.config.ModelInfo`.
        """
        ...

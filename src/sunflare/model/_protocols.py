from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, runtime_checkable

from typing_extensions import Protocol

if TYPE_CHECKING:
    from typing import Any, Optional

    from bluesky.protocols import Reading, SyncOrAsync
    from event_model.documents.event_descriptor import DataKey

    from sunflare.config import ModelInfo

__all__ = ["ModelProtocol"]


@runtime_checkable
class ModelProtocol(Protocol):
    """Minimal required protocol for a recognizable device in Redsun.

    Exposes the following Bluesky protocols:

    - :class:`~bluesky.protocols.HasName`
    - :class:`~bluesky.protocols.HasParent`
    - :class:`~bluesky.protocols.Configurable`

    Additionally provides a `shutdown` method
    to (optionally) perform cleanup operations.
    """

    @abstractmethod
    def __init__(self, name: str, model_info: ModelInfo) -> None: ...

    @abstractmethod
    def configure(
        self, *args: Any, **kwargs: Any
    ) -> SyncOrAsync[tuple[Reading[Any], Reading[Any]]]:
        """Configure the model.

        The protocol allows to set new values for slow-changing parameters.

        The method can be normal or `async`.

        Parameters
        ----------
        *args
            Positional arguments.
        **kwargs
            Keyword arguments.

        Returns
        -------
        tuple[:class:`~bluesky.protocols.Reading`, :class:`~bluesky.protocols.Reading`]
            A two-element tuple: the first element is the old configuration value;
            the second element is the new configuration value set by the model.
        """
        ...

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
    def describe_configuration(self) -> SyncOrAsync[dict[str, DataKey]]:
        """Describe the model configuration.

        Provides a description of each field of the model configuration.

        The method can be normal or `async`.

        Returns
        -------
        dict[``str``, :class:`~event_model.DataKey`]
            A dictionary with the description of each field of the model configuration.
        """
        ...

    @abstractmethod
    def shutdown(self) -> None:
        """Perform cleanup operation of the model.

        If not necessary, it can be left as a no-op.
        """
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        """Model identifier.

        Used to populate object_keys in the Event :class:`~event_model.DataKey`.

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
    def model_info(self) -> ModelInfo:
        """The associated model information.

        It can return a subclass of :class:`~sunflare.config.ModelInfo`.
        """
        ...

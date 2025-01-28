"""Models represent device interfaces that Bluesky can interact with.

Models offer a subset of Bluesky protocols to execute actions.
A minimal recognizable device in RedSun must implement the :class:`~sunflare.model.ModelProtocol` protocol.
"""

from __future__ import annotations

import sys

if sys.version_info >= (3, 11):
    from typing import Protocol
else:
    from typing_extensions import Protocol

from abc import abstractmethod
from typing import TYPE_CHECKING, runtime_checkable

if TYPE_CHECKING:
    from typing import Any, Optional

    from bluesky.protocols import Reading, SyncOrAsync
    from event_model.documents.event_descriptor import DataKey

    from sunflare.config import ModelInfo

__all__ = ["ModelProtocol"]


@runtime_checkable
class ModelProtocol(Protocol):
    """Minimal required protocol for a recognizable device in RedSun.

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
    def configure(self, name: str, value: Any, /, **kwargs: Any) -> None:
        """Configure the model.

        The protocol allows to set new values for slow-changing parameters.

        Parameters
        ----------
        name : ``str``
            The name of the configuration parameter to set.
        value : ``Any``
            The value to set for the configuration parameter.
        kwargs : ``Any``
            Additional keyword arguments.
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
        In Redsun (for now) should always return ``None``.
        """
        ...

    @property
    @abstractmethod
    def model_info(self) -> ModelInfo:
        """The object associated model information.

        It can return a subclass of :class:`~sunflare.config.ModelInfo`.
        """
        ...

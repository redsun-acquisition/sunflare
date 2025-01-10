"""Models represent device interfaces that Bluesky can interact with.

Models offer a subset of Bluesky protocols to execute actions.
A minimal recognizable device in RedSun must implement the :class:`~sunflare.model.ModelProtocol` protocol.
"""

from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from typing import Any, Optional, Union

    from bluesky.protocols import Reading, Location, SyncOrAsync
    from event_model.documents.event_descriptor import DataKey

    from sunflare.config import ModelInfo
    from sunflare.engine import Status

__all__ = ["ModelProtocol", "MotorModel"]


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


@runtime_checkable
class MotorModelProtocol(ModelProtocol, Protocol):
    """Expected protocol for motor models.

    To be recognized as such, a ``MotorModel`` must implemement the methods listed below,
    together with the interface defined in :class:`~sunflare.model.ModelProtocol``.

    Exposes the following Bluesky protocols:

    - :meth:`~bluesky.protocols.Locatable` (``locate``)
    - :meth:`~bluesky.protocols.Settable` (``set``)
    """

    @abstractmethod
    def locate(self) -> Location[Union[int, float]]:
        """Get the current motor location.

        Returns
        -------
        ``Location[Union[int, float]]``
            Motor location.
        """
        ...

    @abstractmethod
    def set(self, value: Union[int, float], axis: Optional[str] = None) -> Status:
        """Set the motor location on a specific axis.

        Parameters
        ----------
        value : ``Union[int, float]``
            New motor location.
        axis : ``str``, optional
            Motor axis along which movement occurs, by default None.

        Returns
        -------
        Status
            Status object monitoring the operation.
        """
        ...


@runtime_checkable
class DetectorModelProtocol(ModelProtocol, Protocol):
    """Expected protocol for detector models.

    To be recognized as such, a ``DetectorModel`` must implemement the methods listed below,
    together with the interface defined in :class:`~sunflare.model.ModelProtocol``.

    Exposes the following Bluesky protocols:

    - :meth:`~bluesky.protocols.Stageable` (``locate``)
    - :meth:`~bluesky.protocols.Readable` (``set``)
    """

    @abstractmethod
    def __init__(self, name: str, model_info: ModelInfo) -> None: ...

    @abstractmethod
    def stage(self) -> Status:
        """Stage the detector for acquisition.

        The method implies a mechanism for the detector to start acquiring data.

        Returns
        -------
        Status
            Status object monitoring the operation.
        """
        ...

    @abstractmethod
    def unstage(self) -> Status:
        """Unstage the detector.

        The method implies a mechanism for the detector to stop acquiring data.
        It's the opposite of the ``stage`` method.

        Returns
        -------
        Status
            Status object monitoring the operation.
        """
        ...

    @abstractmethod
    def read(self) -> dict[str, Reading[Any]]:
        """Return a mapping of field names to the last value read.

        Example return value:

        .. code-block:: python

            OrderedDict(
                ("channel1", {"value": 5, "timestamp": 1472493713.271991}),
                ("channel2", {"value": 16, "timestamp": 1472493713.539238}),
            )

        Returns
        -------
        dict[str, Reading[Any]]
            Mapping of field names to the last value read.
        """
        ...

    @abstractmethod
    def describe(self) -> dict[str, DataKey]:
        """Return a dictionary with exactly the same keys as the ``read``.

        It provides a description of the data that will be returned by the ``read`` method.

        Example return value:

        .. code-block:: python

            OrderedDict(
                (
                    "channel1",
                    {"source": "XF23-ID:SOME_PV_NAME", "dtype": "number", "shape": []},
                ),
                (
                    "channel2",
                    {"source": "XF23-ID:SOME_PV_NAME", "dtype": "number", "shape": []},
                ),
            )
        """
        ...

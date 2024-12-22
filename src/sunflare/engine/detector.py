"""``detector`` module."""

from __future__ import annotations

from abc import ABCMeta, abstractmethod
from collections import OrderedDict
from typing import Any, Generic, Protocol, Tuple, TypeVar, runtime_checkable

from bluesky.protocols import Reading

# TODO: rather than using the event_model package,
# we should switch to a local TypedDict;
# for now we start with this
from event_model.documents.event_descriptor import DataKey

from sunflare.config import DetectorModelInfo, DetectorModelTypes
from sunflare.engine.status import Status
from sunflare.log import Loggable

__all__ = ["DetectorModel", "DetectorProtocol"]

M = TypeVar("M", bound=DetectorModelInfo, covariant=True)


@runtime_checkable
class DetectorProtocol(Protocol[M]):
    """Bluesky-compatible detector protocol.

    This model implements the following protocols:

    - :class:`bluesky.protocols.Readable`
    - :class:`bluesky.protocols.Stageable`
    - :class:`bluesky.protocols.Pausable`
    - :class:`bluesky.protocols.Flyable`
    - :class:`bluesky.protocols.Completable`
    """

    _name: str
    _model_info: DetectorModelInfo

    @abstractmethod
    def __init__(self, name: str, model_info: DetectorModelInfo) -> None:
        # the __init__ method is provided only for type checking
        ...

    def shutdown(self) -> None:
        """Shutdown the detector.

        Optional method.
        Implement this to for graceful shutdown.
        """
        ...

    @abstractmethod
    def stage(self) -> Status:
        """Set up the device for acquisition.

        Returns
        -------
        :class:`~sunflare.engine.status.Status`
            A status object that is marked done when the device is done staging.
        """
        ...

    @abstractmethod
    def unstage(self) -> Status:
        """Disables device.

        Returns
        -------
        :class:`~sunflare.engine.status.Status`
            A status object that is marked done when the device is done unstaging.
        """
        ...

    @abstractmethod
    def describe(self) -> OrderedDict[str, DataKey]:
        """Return an OrderedDict with exactly the same keys as the ``read`` method, here mapped to per-scan metadata about each field.

        A base example of a return value is shown below:

        .. code-block:: python

            OrderedDict(('channel1',
                         {'source': 'XF23-ID:SOME_PV_NAME',
                          'dtype': 'number',
                          'shape': []}),
                        ('channel2',
                         {'source': 'XF23-ID:SOME_PV_NAME',
                          'dtype': 'number',
                          'shape': []}))

        For a more detailed description, see the ``DataKey`` class.

        Returns
        -------
        :class:`~collections.OrderedDict`
            An ordered dictionary of data keys.
        """
        ...

    @abstractmethod
    def read(self) -> OrderedDict[str, Reading[Any]]:
        """Return an OrderedDict mapping string field name(s) to dictionaries of values and timestamps and optional per-point metadata.

        Example return value:

        .. code-block:: python

            OrderedDict(('channel1',
                         {'value': 5, 'timestamp': 1472493713.271991}),
                         ('channel2',
                         {'value': 16, 'timestamp': 1472493713.539238}))

        For a more detailed description, see the ``Reading`` class.

        Returns
        -------
        :class:`~collections.OrderedDict`
            An ordered dictionary of readings.
        """
        ...

    @abstractmethod
    def pause(self) -> None:
        """Perform device-specific work when the RunEngine pauses."""
        ...

    @abstractmethod
    def resume(self) -> None:
        """Perform device-specific work when the RunEngine resumes after a pause."""
        ...

    @abstractmethod
    def kickoff(self) -> Status:
        """Start the device for asynchronous acquisition.

        Returns
        -------
        :class:`~sunflare.engine.status.Status`
            A status object that is marked done when the device is done starting.
        """
        ...

    @abstractmethod
    def complete(self) -> Status:
        """Wait for the device to complete if it is running asynchronously.

        Returns
        -------
        :class:`~sunflare.engine.status.Status`
            A status object that is marked done when the device is done completing.
        """
        ...

    @abstractmethod
    def read_configuration(self) -> OrderedDict[str, Reading[Any]]:
        """Provide same API as ``read`` but for slow-changing fields related to configuration.

        Example: exposure time. These will typically be read only once per run.

        Returns
        -------
        :class:`~collections.OrderedDict`
            An ordered dictionary of configuration readings.
        """
        ...

    @abstractmethod
    def describe_configuration(self) -> OrderedDict[str, DataKey]:
        """Provide same API as ``describe``, but corresponding to the keys in ``read_configuration``.

        Returns
        -------
        :class:`~collections.OrderedDict`
            An ordered dictionary of configuration data keys.
        """
        ...

    @property
    def name(self) -> str:
        """The name of the detector."""
        ...

    @property
    def model_info(self) -> M:
        """The model information for the detector."""
        ...


class DetectorModel(Loggable, Generic[M]):
    """
    ``DetectorModel`` abstract base class. Supports logging via :class:`~sunflare.log.Loggable`.

    The ``DetectorModel`` is the base class from which all detectors must inherit.
    It provides the basic information about the detector model and the properties exposable to the upper layers for user interaction.

    It does **not** provide APIs for performing actions, which are instead defined by :class:`~sunflare.engine.detector.DetectorProtocol`.

    Parameters
    ----------
    name: str
        - Detector instance unique identifier name.
        - User defined.
    model_info: DetectorModelInfo
        - Detector model information dataclass.
        - Provided by RedSun configuration.
    """

    @abstractmethod
    def __init__(
        self,
        name: str,
        model_info: M,
    ) -> None:
        self._name = name
        self._model_info = model_info

    @property
    def name(self) -> str:
        """Detector instance unique identifier uid."""
        return self._name

    @property
    def model_info(self) -> M:
        """Detector model informations."""
        return self._model_info

    @property
    def model_name(self) -> str:
        """Detector model name."""
        return self._model_info.model_name

    @property
    def vendor(self) -> str:
        """Detector vendor."""
        return self._model_info.vendor

    @property
    def serial_number(self) -> str:
        """Detector serial number."""
        return self._model_info.serial_number

    @property
    def category(self) -> DetectorModelTypes:
        """Detector type."""
        return self._model_info.category

    @property
    def sensor_size(self) -> Tuple[int, int]:
        """Detector sensor size in pixels: represents the 2D axis (Y, X). Only applicable for 'line' and 'area' detectors."""
        return self._model_info.sensor_size

    @property
    def pixel_size(self) -> Tuple[float, float, float]:
        """Detector pixel size in micrometers: represents the 3D axis (Z, Y, X)."""
        return self._model_info.pixel_size

    @property
    def exposure_egu(self) -> str:
        """Detector exposure unit."""
        return self._model_info.exposure_egu

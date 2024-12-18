# ruff: noqa
from __future__ import annotations

from abc import abstractmethod
from typing import Protocol, TypeVar, Union, runtime_checkable, Any

from sunflare.config import MotorModelInfo, DetectorModelInfo
from sunflare.engine.motor import MotorModel
from sunflare.engine.light import LightModel
from sunflare.engine.detector import DetectorModel
from sunflare.types import AxisLocation

from bluesky.protocols import Reading

# TODO: rather than using the event_model package,
# we should switch to a local TypedDict;
# for now we start with this
from event_model.documents.event_descriptor import DataKey

from collections import OrderedDict

from ._status import Status

# specific device types
M = TypeVar("M", bound=MotorModel)
L = TypeVar("L", bound=LightModel)
D = TypeVar("D", bound=DetectorModel)


@runtime_checkable
class HasMotors(Protocol):
    """A protocol describing that the registry has motors."""

    @property
    def motors(self) -> dict[str, M]: ...


@runtime_checkable
class HasDetectors(Protocol):
    """A protocol describing that the registry has detectors."""

    @property
    def detectors(self) -> dict[str, D]: ...


# TODO: more protocols for this?
@runtime_checkable
class MotorProtocol(Protocol):
    """Bluesky motor.

    Implements the following protocols

    - :class:`bluesky.protocols.Movable`
    - :class:`bluesky.protocols.Locatable`
    """

    _model_info: MotorModelInfo

    def shutdown(self) -> None:
        """Shutdown the motor.

        Optional method.
        Implement this to for graceful shutdown.
        """
        ...

    @abstractmethod
    def set(self, value: AxisLocation[Union[float, int, str]]) -> Status:
        """Return a ``Status`` that is marked done when the device is done moving."""
        ...

    @abstractmethod
    def locate(self) -> AxisLocation[Union[float, int, str]]:
        """Return the current location of a Device.

        While a ``Readable`` reports many values, a ``Movable`` will have the
        concept of location. This is where the Device currently is, and where it
        was last requested to move to. This protocol formalizes how to get the
        location from a ``Movable``.
        """
        ...

    @property
    def model_info(self) -> MotorModelInfo:
        """Return the model information for the motor."""
        ...


@runtime_checkable
class DetectorProtocol(Protocol):
    """Bluesky detector base model.

    This model implements the following protocols:

    - :class:`bluesky.protocols.Readable`
    - :class:`bluesky.protocols.Stageable`
    - :class:`bluesky.protocols.Pausable`
    - :class:`bluesky.protocols.Flyable`
    - :class:`bluesky.protocols.Completable`
    """

    _model_info: DetectorModelInfo

    def shutdown(self) -> None:
        """Shutdown the detector.

        Optional method.
        Implement this to for graceful shutdown.
        """
        ...

    @abstractmethod
    def stage(self) -> Status:
        """Set up the device for acquisition.

        It should return a ``Status`` that is marked done when the device is
        done staging.
        """
        ...

    @abstractmethod
    def unstage(self) -> Status:
        """Disables device.

        It should return a ``Status`` that is marked done when the device is finished
        unstaging.
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
        """

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

        Returns a ``Status`` that is marked done when the device is finished
        starting.
        """
        ...

    @abstractmethod
    def complete(self) -> Status:
        """Wait for the device to complete.

        Returns ``Status`` that is marked done when the device is finished
        completing.
        """
        ...

    @abstractmethod
    def read_configuration(self) -> OrderedDict[str, Reading[Any]]:
        """Provide same API as ``read`` but for slow-changing fields related to configuration.

        Example: exposure time. These will typically be read only once per run.
        """
        ...

    @abstractmethod
    def describe_configuration(self) -> OrderedDict[str, DataKey]:
        """Provide same API as ``describe``, but corresponding to the keys in ``read_configuration``."""
        ...

    @property
    def model_info(self) -> DetectorModelInfo:
        """Return the model information for the detector."""
        ...

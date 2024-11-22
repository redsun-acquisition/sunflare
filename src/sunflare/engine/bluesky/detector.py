"""Bluesky detector interface."""

from abc import abstractmethod

from typing import TYPE_CHECKING

from bluesky.protocols import Reading

# TODO: rather than using the event_model package,
# we should switch to a local TypedDict;
# for now we start with this
from event_model.documents.event_descriptor import DataKey

from collections import OrderedDict

from ._status import Status

from sunflare.engine import DetectorModel

if TYPE_CHECKING:
    from typing import Any

    from sunflare.config import DetectorModelInfo


class BlueskyDetectorModel(DetectorModel):
    """Bluesky detector base model.

    This model implements the following protocols:

    - :class:`bluesky.protocols.Readable`
    - :class:`bluesky.protocols.Stageable`
    - :class:`bluesky.protocols.Pausable`
    - :class:`bluesky.protocols.Flyable`
    - :class:`bluesky.protocols.Completable`
    """

    def __init__(self, name: str, model_info: "DetectorModelInfo") -> None:
        super().__init__(name, model_info)

    def shutdown(self) -> None:
        """Shutdown the detector.

        Optional method.
        Implement this to perform any necessary cleanup when the detector is shut down.
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

"""Bluesky detector interface."""

from abc import abstractmethod

from typing import TYPE_CHECKING

from bluesky.protocols import Readable, Flyable

from ._status import Status

from sunflare.engine import DetectorModel

if TYPE_CHECKING:
    from sunflare.config import DetectorModelInfo


class BlueskyDetectorModel(DetectorModel, Readable, Flyable):
    """Bluesky detector base model."""

    def __init__(self, name: str, model_info: "DetectorModelInfo") -> None:
        super().__init__(name, model_info)

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

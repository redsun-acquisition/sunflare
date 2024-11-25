"""Bluesky detector interface."""

from abc import abstractmethod

from typing import TYPE_CHECKING, Union

from sunflare.engine import MotorModel

from bluesky.protocols import Location

from ._status import Status

if TYPE_CHECKING:
    from sunflare.config import MotorModelInfo


# TODO: more protocols for this?
class BlueskyMotorModel(MotorModel):
    """Bluesky detector base model.

    Implements the following protocols

    - :class:`bluesky.protocols.Movable`
    - :class:`bluesky.protocols.Locatable`
    """

    def __init__(self, name: str, model_info: "MotorModelInfo"):
        super().__init__(name, model_info)

    def shutdown(self) -> None:
        """Shutdown the motor.

        Optional method.
        Implement this to for graceful shutdown.
        """
        ...

    # TODO: define a proper type
    # for the value parameter
    @abstractmethod
    def set(self, value: int) -> Status:
        """Return a ``Status`` that is marked done when the device is done moving."""
        ...

    @abstractmethod
    def locate(self) -> Location[Union[float, int]]:
        """Return the current location of a Device.

        While a ``Readable`` reports many values, a ``Movable`` will have the
        concept of location. This is where the Device currently is, and where it
        was last requested to move to. This protocol formalizes how to get the
        location from a ``Movable``.
        """
        ...

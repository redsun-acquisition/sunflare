"""Bluesky detector interface."""

from __future__ import annotations

from abc import abstractmethod

from typing import TYPE_CHECKING

from sunflare.engine import MotorModel

if TYPE_CHECKING:
    from sunflare.config import MotorModelInfo
    from sunflare.types import AxisLocation

    from typing import Union

    from ._status import Status


# TODO: more protocols for this?
class BlueskyMotorModel(MotorModel):
    """Bluesky detector base model.

    Implements the following protocols

    - :class:`bluesky.protocols.Movable`
    - :class:`bluesky.protocols.Locatable`
    """

    def __init__(self, name: str, model_info: MotorModelInfo):
        super().__init__(name, model_info)

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

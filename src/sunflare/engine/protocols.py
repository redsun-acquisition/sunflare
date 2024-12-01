# ruff: noqa

from typing import Protocol, TypeVar

from sunflare.engine.motor import MotorModel
from sunflare.engine.light import LightModel
from sunflare.engine.detector import DetectorModel

# specific device types
M = TypeVar("M", bound=MotorModel)
L = TypeVar("L", bound=LightModel)
D = TypeVar("D", bound=DetectorModel)


class HasMotors(Protocol):
    """A protocol describing that the registry has motors."""

    @property
    def motors(self) -> dict[str, M]: ...


class HasLights(Protocol):
    """A protocol describing that the registry has lights."""

    @property
    def lights(self) -> dict[str, L]: ...


class HasDetectors(Protocol):
    """A protocol describing that the registry has detectors."""

    @property
    def detectors(self) -> dict[str, D]: ...

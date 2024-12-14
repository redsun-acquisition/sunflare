"""Device registry protocol module."""

from typing import Generic, TypeVar, Protocol, Optional

from sunflare.engine.motor import MotorModel
from sunflare.engine.detector import DetectorModel

M = TypeVar("M", bound="MotorModel")
D = TypeVar("D", bound="DetectorModel")

__all__ = ["DeviceRegistry"]


class DeviceRegistry(Generic[M, D], Protocol):
    """Device registry protocol."""

    @property
    def motors(self) -> Optional[dict[str, M]]:
        """Get the motors dictionary."""
        ...

    @property
    def detectors(self) -> Optional[dict[str, D]]:
        """Get the detectors dictionary."""
        ...

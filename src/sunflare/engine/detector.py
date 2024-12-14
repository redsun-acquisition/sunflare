"""Detector model abstract base class definition."""

from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import Tuple

from sunflare.log import Loggable
from sunflare.config import AcquisitionEngineTypes, DetectorModelInfo


class DetectorModel(Loggable, metaclass=ABCMeta):
    """
    `DetectorModel` abstract base class. Supports logging via `Loggable`.

    The `DetectorModel` is the base class from which all detectors, regardless of the supported engine, must inherit.
    It provides the basic information about the detector model and the properties exposable to the upper layers for user interaction.

    It does **not** provide APIs for performing actions, which must be instead defined by the engine-specific detector classes.

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
        model_info: DetectorModelInfo,
    ) -> None:
        self.__name = name
        self._model_info = model_info

    @property
    def name(self) -> str:
        """Detector instance unique identifier uid."""
        return self.__name

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
    def supported_engines(self) -> list[AcquisitionEngineTypes]:
        """Supported acquisition engines list."""
        return self._model_info.supported_engines

    @property
    def category(self) -> str:
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

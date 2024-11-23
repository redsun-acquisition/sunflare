"""Detector model abstract base class definition."""

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING

from sunflare.log import Loggable

if TYPE_CHECKING:
    from typing import Tuple

    from sunflare.config import AcquisitionEngineTypes, DetectorModelInfo


class DetectorModel(Loggable, metaclass=ABCMeta):
    """
    `DetectorModel` abstract base class. Supports logging via `Loggable`.

    The `DetectorModel` is the base class from which all detectors, regardless of the supported engine, must inherit.
    It provides the basic information about the detector model and the properties exposable to the upper layers for user interaction.

    It does **not** provide APIs for performing actions, which must be instead defined by the engine-specific detector classes.

    The `DetectorModel` contains an extended, evented dataclass that allows the user to expose new properties to the upper layers using `psygnal`.

    Parameters
    ----------
    name: str
        - Detector instance unique identifier name.
        - User defined.
    model_info: DetectorModelInfo
        - Detector model information dataclass.
        - Provided by RedSun configuration.
    exposure: Union[int, float]
        - Detector exposure time at startup (time scale defined by `exposure_egu`).
        - User defined.
    pixel_photometric: list[PixelPhotometricTypes]
        - List of supported pixel colors.
        - User defined.
        - Defaults to `gray`.
    bits_per_pixel: set[int]
        - Set of supported values for pixel width in bits.
        - User defined.
        - Defaults to `{8}`.
    offset: Tuple[int, int]
        - Detector offset at startup (Y, X).
        - User-defined.
        - Only applicable for 'line' and 'area' detectors. Defaults to `(0, 0)`.
    shape: Tuple[int, int]
        - Detector shape at startup (Y, X).
        - User-defined.
        - If set to `None`, it defaults to the sensor size.
        - Only applicable for 'line' and 'area' detectors. Defaults to `None`.
    """

    @abstractmethod
    def __init__(
        self,
        name: "str",
        model_info: "DetectorModelInfo",
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
    def supported_engines(self) -> "list[AcquisitionEngineTypes]":
        """Supported acquisition engines list."""
        return self._model_info.supported_engines

    @property
    def category(self) -> str:
        """Detector type."""
        return self._model_info.category

    @property
    def sensor_size(self) -> "Tuple[int, int]":
        """Detector sensor size in pixels: represents the 2D axis (Y, X). Only applicable for 'line' and 'area' detectors."""
        return self._model_info.sensor_size

    @property
    def pixel_size(self) -> "Tuple[float, float, float]":
        """Detector pixel size in micrometers: represents the 3D axis (Z, Y, X)."""
        return self._model_info.pixel_size

    @property
    def exposure_egu(self) -> str:
        """Detector exposure unit."""
        return self._model_info.exposure_egu

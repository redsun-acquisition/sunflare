"""Light source model abstract base class definition."""

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING

from sunflare.log import Loggable

if TYPE_CHECKING:
    from typing import Any, Union

    from sunflare.config import (
        AcquisitionEngineTypes,
        LightModelInfo,
        LightModelTypes,
    )


class LightModel(Loggable, metaclass=ABCMeta):
    """
    `LightModel` abstract base class. Supports logging via `Loggable`.

    The `LightModel` is the base class from which all light sources, regardless of the supported engine, must inherit.
    It provides the basic information about the light source model and the properties exposable to the upper layers for user interaction.

    It does **not** provide APIs for performing actions, which must be instead defined by the engine-specific light source classes.

    The `LightModel` contains an extended, evented dataclass that allows the user to expose new properties to the upper layers using `psygnal`.

    Parameters
    ----------
    name: str
        - Light source instance unique identifier name.
        - User defined.
    model_info: LightModelInfo
        - Light source model information dataclass.
        - Provided by RedSun configuration.
    """

    @abstractmethod
    def __init__(self, name: str, model_info: "LightModelInfo") -> None:
        self.__name = name
        self._modelInfo = model_info

    @property
    def name(self) -> str:
        """Light source instance unique identifier name."""
        return self.__name

    @property
    def modelName(self) -> str:
        """Light source model name."""
        return self._modelInfo.modelName

    @property
    def modelParams(self) -> "dict[str, Any]":
        """Light source model parameters."""
        return self._modelInfo.modelParams

    @property
    def vendor(self) -> str:
        """Light source vendor."""
        return self._modelInfo.vendor

    @property
    def serialNumber(self) -> str:
        """Light source serial number."""
        return self._modelInfo.serialNumber

    @property
    def supportedEngines(self) -> "list[AcquisitionEngineTypes]":
        """List of supported acquisition engines."""
        return self._modelInfo.supportedEngines

    @property
    def category(self) -> "LightModelTypes":
        """Light source type."""
        return self._modelInfo.category

    @property
    def wavelength(self) -> int:
        """Light source wavelength."""
        return self._modelInfo.wavelength

    @property
    def powerEGU(self) -> str:
        """Light source power EGU."""
        return self._modelInfo.powerEGU

    @property
    def minPower(self) -> "Union[float, int]":
        """Minimum light source power, expressed in EGU."""
        return self._modelInfo.minPower

    @property
    def maxPower(self) -> "Union[float, int]":
        """Maximum light source power, expressed in EGU."""
        return self._modelInfo.maxPower

    @property
    def powerStep(self) -> "Union[float, int]":
        """Light source power step, expressed in EGU."""
        return self._modelInfo.powerStep

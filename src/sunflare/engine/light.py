"""Light source model abstract base class definition."""

from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import Union, Optional, Tuple

from sunflare.log import Loggable
from sunflare.config import (
    LightModelInfo,
    LightModelTypes,
)


class LightModel(Loggable, metaclass=ABCMeta):
    """
    `LightModel` abstract base class. Supports logging via :class:`~sunflare.log.Loggable`.

    The `LightModel` is the base class from which all light sources, regardless of the supported engine, must inherit.
    It provides the basic information about the light source model and the properties exposable to the upper layers for user interaction.

    It does **not** provide APIs for performing actions, which must be instead defined by the engine-specific light source classes.

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
    def __init__(self, name: str, model_info: LightModelInfo) -> None:
        self.__name = name
        self._model_info = model_info

    @property
    def name(self) -> str:
        """Light source instance unique identifier name."""
        return self.__name

    @property
    def model_name(self) -> str:
        """Light source model name."""
        return self._model_info.model_name

    @property
    def vendor(self) -> str:
        """Light source vendor."""
        return self._model_info.vendor

    @property
    def serial_number(self) -> str:
        """Light source serial number."""
        return self._model_info.serial_number

    @property
    def category(self) -> LightModelTypes:
        """Light source type."""
        return self._model_info.category

    @property
    def wavelength(self) -> Optional[int]:
        """Light source wavelength. Returns `None` if not applicable."""
        return self._model_info.wavelength

    @property
    def power_egu(self) -> str:
        """Light source power EGU."""
        return self._model_info.power_egu

    @property
    def range(self) -> Union[Tuple[float, float], Tuple[int, int]]:
        """Light source power range, expressed in EGU.

        Formatted as (min, max).
        """
        return self._model_info.range

    @property
    def power_step(self) -> Union[float, int]:
        """Light source power step, expressed in EGU."""
        return self._model_info.power_step

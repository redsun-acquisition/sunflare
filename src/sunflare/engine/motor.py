"""
Motors are a category of hardware devices capable of moving objects in a controlled manner.

Belonging to this category fall devices such as stage axis, focusing units, generic stepper motors, and so on.
"""

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING

from sunflare.log import Loggable

if TYPE_CHECKING:
    from sunflare.config import (
        AcquisitionEngineTypes,
        MotorModelInfo,
        MotorModelTypes,
    )


class MotorModel(Loggable, metaclass=ABCMeta):
    """
    `MotorModel` abstract base class. Supports logging via `Loggable`.

    The `MotorModel` is the base class from which all motors, regardless of the supported engine, must inherit.
    It provides the basic information about the motor model and the properties exposable to the upper layers for user interaction.

    It does **not** provide APIs for performing actions, which must be instead defined by the engine-specific motor classes.

    Parameters
    ----------
    name : str
        - Motor unique identifier name.
        - User defined.
    model_info: MotorModelInfo
        - Motor model information dataclass.
        - Provided by RedSun configuration.

    Properties
    ----------
    axes : list[str]
        - Motor axes.
    return_home : bool
        - If `True`, motor will return to home position
        (defined as  the initial position the motor had at RedSun's startup)
        after RedSun is closed. Defaults to `False`.
    """

    @abstractmethod
    def __init__(self, name: str, model_info: "MotorModelInfo"):
        self.__name = name
        self._model_info = model_info

    @property
    def name(self) -> str:
        """Motor instance unique identifier name."""
        return self.__name

    @property
    def model_name(self) -> str:
        """Motor model name."""
        return self._model_info.model_name

    @property
    def vendor(self) -> str:
        """Motor vendor."""
        return self._model_info.vendor

    @property
    def serial_number(self) -> str:
        """Motor serial number."""
        return self._model_info.serial_number

    @property
    def supported_engines(self) -> "list[AcquisitionEngineTypes]":
        """Supported acquisition engines list."""
        return self._model_info.supported_engines

    @property
    def category(self) -> "MotorModelTypes":
        """Motor type."""
        return self._model_info.category

    @property
    def step_egu(self) -> str:
        """Motor step unit."""
        return self._model_info.step_egu

    @property
    def step_size(self) -> float:
        """Motor step size."""
        return self._model_info.step_size

    @property
    def axes(self) -> list[str]:
        """Motor axes list."""
        return self._model_info.axes

    @property
    def return_home(self) -> bool:
        """
        If `True`, motor will return to home position (defined as  the initial position the motor had at RedSun's startup) after RedSun is closed.

        Defaults to `False`.
        """
        return self._model_info.return_home

"""``motors`` module."""

from __future__ import annotations

from abc import abstractmethod
from typing import (
    TYPE_CHECKING,
    Any,
    Generic,
    Protocol,
    TypeVar,
    Union,
    runtime_checkable,
)

from sunflare.config import MotorModelInfo, MotorModelTypes
from sunflare.log import Loggable

if TYPE_CHECKING:
    from bluesky.protocols import Location

    from sunflare.engine.status import Status

__all__ = ["MotorModel"]

M = TypeVar("M", bound=MotorModelInfo, covariant=True)


# TODO: more protocols for this?
@runtime_checkable
class MotorProtocol(Protocol):  # pragma: no cover
    """Bluesky-compatible motor protocol.

    Implements the following protocols:

    - :class:`bluesky.protocols.Movable`
    - :class:`bluesky.protocols.Locatable`
    """

    def shutdown(self) -> None:
        """Shutdown the motor.

        Optional method.
        Implement this to for graceful shutdown.
        """
        ...

    def set(self, value: Union[float, int, str], *args: Any, **kwargs: Any) -> Status:
        """Set a value for the given motor.

        The meaning of ``value`` depends on the motor model implementation, i.e.

        - setting a new position for a linear motor;
        - setting a new angle for a rotary motor;
        - setting a new voltage for a piezo motor;
        - setting a pressure value for a pump;
        - ...

        Parameters
        ----------
        value : ``Union[float, int, str]]``
            The value to set.
        *args : ``Any``
            Additional positional arguments.
        **kwargs : ``Any``
            Additional keyword arguments.

        Returns
        -------
        :class:`~sunflare.engine.status.Status`
            A status object that is marked done when the motor is done moving.
        """
        ...

    def locate(self) -> Location[Union[float, int, str]]:
        """Return the current location of a Device.

        While a ``Readable`` reports many values, a ``Movable`` will have the
        concept of location. This is where the Device currently is, and where it
        was last requested to move to. This protocol formalizes how to get the
        location from a ``Movable``.

        Returns
        -------
        ``Location[Union[float, int, str]]]``
            The current location of the motor.
        """
        ...

    @property
    def name(self) -> str:
        """The name of the motor instance."""
        ...

    @property
    def parent(self) -> None:
        """Required property for Bluesky compatibility.

        It's tied to Ophyd's concept of
        parent/child relationships between devices.
        """
        ...


class MotorModel(MotorProtocol, Loggable, Generic[M]):
    """
    ``MotorModel`` abstract base class. Supports logging via :class:`~sunflare.log.Loggable`.

    The ``MotorModel`` is the base class from which all motors must inherit.
    It provides the basic information about the motor model and the properties exposable to the upper layers for user interaction.

    It does **not** provide APIs for performing actions, which are instead defined by :class:`~sunflare.engine.motor.MotorProtocol`.

    Parameters
    ----------
    name : ``str``
        Motor name.
    model_info: MotorModelInfo
        Motor model informations.
    """

    @abstractmethod
    def __init__(self, name: str, model_info: M) -> None:
        self._name = name
        self._model_info = model_info

    @property
    def name(self) -> str:
        """Motor instance unique identifier name."""
        return self._name

    @property
    def parent(self) -> None:
        """Required property for Bluesky compatibility.

        It's tied to Ophyd's concept of
        parent/child relationships between devices.
        """
        None

    @property
    def model_info(self) -> M:
        """Motor model informations."""
        return self._model_info

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
    def category(self) -> MotorModelTypes:
        """Motor type."""
        return self._model_info.category

    @property
    def step_egu(self) -> str:
        """Motor step unit."""
        return self._model_info.step_egu

    @property
    def step_size(self) -> Union[int, float]:
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

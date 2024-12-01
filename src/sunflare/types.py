# noqa: D100

from typing import TYPE_CHECKING, TypeAlias, TypeVar, Generic, TypedDict

if TYPE_CHECKING:
    from typing import Any, Generator, Iterable, Union, Sequence

T = TypeVar("T", bound=Union[int, str, float])
X = TypeVar("X", bound=Union[str, int])


class AxisLocation(TypedDict, Generic[X, T]):
    r"""Typed dictionary for axis-aware device location.

    Parameters
    ----------
    axis : Union[X, Sequence[X]]
        The axis along which the Device is moving. \
        Can be a single axis or a sequence of axes.
    setpoint : Union[T, Sequence[T]]
        Where the Device was requested to move to. \
        Can be a single setpoint or a sequence of setpoints. \
        If it's a sequence, length must match the length of "axis".
    readback : Union[T, Sequence[T]]
        Where the Device actually is at the moment. \
        Can be a single setpoint or a sequence of setpoints. \
        If it's a sequence, length must match the length of "axis".
    """

    axis: "Union[X, Sequence[X]]"
    setpoint: "Union[T, Sequence[T]]"
    readback: "Union[T, Sequence[T]]"


Workflow: TypeAlias = "Union[Generator[Any, None, None], Iterable[Any]]"

__all__ = ["Workflow", "AxisLocation"]

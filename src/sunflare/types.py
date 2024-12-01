# noqa: D100

from typing import TYPE_CHECKING, TypeAlias, TypeVar, Generic, TypedDict

if TYPE_CHECKING:
    from typing import Any, Generator, Iterable, Union, Sequence

T = TypeVar("T", bound=Union[int, str, float])
X = TypeVar("X", bound=Union[str, int])


class AxisLocation(TypedDict, Generic[T, X]):
    """Typed dictionary for axis-aware device location.

    Parameters
    ----------
    axis : Union[X, Sequence[X]]
        The axis along which the Device is moving. Can be a single axis or a sequence of axes.
    setpoint : T
        Where the Device was requested to move to.
    readback : T
        Where the Device actually is at the moment.
    """

    axis: "Union[X, Sequence[X]]"
    setpoint: T
    readback: T


Workflow: TypeAlias = "Union[Generator[Any, None, None], Iterable[Any]]"

__all__ = ["Workflow", "AxisLocation"]

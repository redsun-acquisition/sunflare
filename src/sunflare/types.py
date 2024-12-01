# noqa: D100

from typing import TYPE_CHECKING, TypeAlias, TypeVar, Generic, TypedDict

if TYPE_CHECKING:
    from typing import Any, Generator, Iterable, Union, Optional

T = TypeVar("T")


class AxisLocation(TypedDict, Generic[T]):
    """Typed dictionary for axis-aware device location.

    Parameters
    ----------
    axis : Optional[Union[str, int]]
        The axis along which the Device is moving.
    setpoint : T
        Where the Device was requested to move to.
    readback : T
        Where the Device actually is at the moment.
    """

    axis: "Optional[Union[str, int]]"
    setpoint: T
    readback: T


Workflow: TypeAlias = "Union[Generator[Any, None, None], Iterable[Any]]"

__all__ = ["Workflow", "AxisLocation"]

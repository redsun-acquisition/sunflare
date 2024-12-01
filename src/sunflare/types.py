# noqa: D100

from typing import TYPE_CHECKING, TypeAlias, TypeVar, Generic, TypedDict

if TYPE_CHECKING:
    from typing import Any, Generator, Iterable, Union, Optional

T = TypeVar("T")


class AxisLocation(TypedDict, Generic[T]):
    """Extended Location adding axis information."""

    #: The axis along which the Device is moving
    axis: "Optional[Union[str, int]]"
    #: Where the Device was requested to move to
    setpoint: T
    #: Where the Device actually is at the moment
    readback: T


Workflow: TypeAlias = "Union[Generator[Any, None, None], Iterable[Any]]"

__all__ = ["Workflow", "AxisLocation"]

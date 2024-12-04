# noqa: D100

from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar, TypedDict

if TYPE_CHECKING:
    from typing import Any, Generator, Iterable, Union, Tuple, TypeAlias

    import numpy.typing as npt

T = TypeVar("T", bound=Union[int, str, float])
X = TypeVar("X", bound=Union[str, int])


class AxisLocation(TypedDict, Generic[T]):
    """TypedDict for accessing coordinates along a specific axis.

    Parameters
    ----------
    axis: dict[str, T]
        A dictionary containing the axis name and its corresponding value.
    """

    axis: dict[str, T]


Workflow: TypeAlias = Union[Generator[Any, None, None], Iterable[Any]]

Buffer: TypeAlias = dict[str, Tuple[npt.NDArray[Any], dict[str, Any]]]

__all__ = ["Workflow", "AxisLocation"]

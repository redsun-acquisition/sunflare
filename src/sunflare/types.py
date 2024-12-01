# noqa: D100

from typing import TYPE_CHECKING, TypeAlias, TypeVar

from bluesky.protocols import Location

if TYPE_CHECKING:
    from typing import Any, Generator, Iterable, Union, Optional


T = TypeVar("T")


class AxisLocation(Location[T]):
    """Extended Location adding axis information."""

    axis: "Optional[Union[str, int]]"


Workflow: TypeAlias = "Union[Generator[Any, None, None], Iterable[Any]]"

__all__ = ["Workflow"]

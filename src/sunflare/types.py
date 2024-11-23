# noqa: D100

from typing import TYPE_CHECKING, TypeAlias

if TYPE_CHECKING:
    from typing import Any, Generator, Iterable, Union

Workflow: TypeAlias = "Union[Generator[Any, None, None], Iterable[Any]]"

__all__ = ["Workflow"]

"""The module contains types that are used throughout the SunFlare package.

- ``Workflow``
    - expected signature of a workflow published by a controller.
    - definition: ``Workflow: TypeAlias = Union[Generator[Any, None, None], Iterable[Any]]``
- ``Buffer``
    - expected signature of a data buffer captured by a detector.
    - definition: ``Buffer: TypeAlias = dict[str, Tuple[npt.NDArray[Any], dict[str, Any]]]``
"""

from __future__ import annotations

import sys
from typing import (
    Any,
    Generator,
    Iterable,
    Union,
    Tuple,
    TypeAlias,
    TypeVar,
)

if sys.version_info < (3, 11):
    from typing_extensions import TypedDict, Generic
else:
    from typing import TypedDict, Generic

import numpy.typing as npt

T = TypeVar("T", bound=Union[int, str, float])
X = TypeVar("X", bound=Union[str, int])


class AxisLocation(TypedDict, Generic[T]):
    """TypedDict for accessing coordinates along a specific axis.

    Parameters
    ----------
    axis: ``dict[str, T]``
        A dictionary containing the axis name and its corresponding value.
    """

    axis: dict[str, T]


# TODO: the Workflow type is useless since Bluesky already provides a type for
#       message generators. Use the Bluesky type instead.
Workflow: TypeAlias = Union[Generator[Any, None, None], Iterable[Any]]
Buffer: TypeAlias = dict[str, Tuple[npt.NDArray[Any], dict[str, Any]]]

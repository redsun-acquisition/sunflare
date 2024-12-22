"""The module contains types that are used throughout the SunFlare package.

- ``Workflow``
    - expected signature of a workflow published by a controller.
    - definition: ``Workflow: TypeAlias = Union[Generator[Any, None, None], Iterable[Any]]``
- ``Buffer``
    - expected signature of a data buffer captured by a detector.
    - definition: ``Buffer: TypeAlias = dict[str, Tuple[npt.NDArray[Any], dict[str, Any]]]``
"""

from __future__ import annotations

from typing import Any, Generator, Iterable, Tuple, TypeAlias, TypeVar, Union

import numpy.typing as npt
from bluesky.protocols import Location

T = TypeVar("T", bound=Union[int, str, float])
X = TypeVar("X", bound=Union[str, int])

__all__ = ["Location", "Workflow", "Buffer"]

# TODO: the Workflow type is useless since Bluesky already provides a type for
#       message generators. Use the Bluesky type instead.
Workflow: TypeAlias = Union[Generator[Any, None, None], Iterable[Any]]
Buffer: TypeAlias = dict[str, Tuple[npt.NDArray[Any], dict[str, Any]]]

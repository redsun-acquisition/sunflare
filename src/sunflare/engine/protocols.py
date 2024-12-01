# ruff: noqa

from typing import Protocol, TypeVar, Iterator

from sunflare.engine.motor import MotorModel
from sunflare.engine.light import LightModel
from sunflare.engine.detector import DetectorModel

# generic dict-like protocol types
K = TypeVar("K", bound=str)  # key type
V = TypeVar("V")  # value type

# specific device types
M = TypeVar("M", bound=MotorModel)
L = TypeVar("L", bound=LightModel)
D = TypeVar("D", bound=DetectorModel)


class DictLike(Protocol[K, V]):
    """A dictionary-like protocol."""

    def __getitem__(self, key: K) -> V: ...
    def __setitem__(self, key: K, value: V) -> None: ...
    def __delitem__(self, key: K) -> None: ...
    def __iter__(self) -> Iterator[K]: ...
    def __len__(self) -> int: ...
    def keys(self) -> Iterator[K]: ...
    def values(self) -> Iterator[V]: ...
    def items(self) -> Iterator[tuple[K, V]]: ...


class HasMotors(Protocol):
    """A protocol describing that the registry has motors."""

    @property
    def motors(self) -> DictLike[str, M]: ...


class HasLights(Protocol):
    """A protocol describing that the registry has lights."""

    @property
    def lights(self) -> DictLike[str, L]: ...


class HasDetectors(Protocol):
    """A protocol describing that the registry has detectors."""

    @property
    def detectors(self) -> DictLike[str, D]: ...

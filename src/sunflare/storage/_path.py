"""Path and filename providers for storage backends."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable


@dataclass
class PathInfo:
    """Where and how a storage backend should write data for one device.

    Parameters
    ----------
    store_uri :
        URI of the store root.  For local Zarr this is a ``file://`` URI;
        for remote storage it may be ``s3://`` or similar.
        Example: ``"file:///data/scan001.zarr"``.
    array_key :
        Key (array name) within the store for this device's data.
        Defaults to the device name.
    capacity :
        Maximum number of frames to accept.  ``0`` means unlimited.
    mimetype_hint :
        MIME type hint for the backend.  Consumers may use this to select
        the correct reader.
    extra :
        Optional backend-specific metadata (e.g. OME-Zarr axis labels,
        physical units).  Base writers ignore this field.
    """

    store_uri: str
    array_key: str
    capacity: int = 0
    mimetype_hint: str = "application/x-zarr"
    extra: dict[str, Any] = field(default_factory=dict)


@runtime_checkable
class FilenameProvider(Protocol):
    """Callable that produces a filename (without extension) for a device.

    Parameters
    ----------
    device_name :
        Name of the device requesting a filename.  Implementations may
        ignore this if the filename is device-agnostic.

    Returns
    -------
    str
        A filename string without extension.
    """

    def __call__(self, device_name: str | None = None) -> str:
        """Return a filename for the given device."""
        ...


@runtime_checkable
class PathProvider(Protocol):
    """Callable that produces :class:`PathInfo` for a device.

    Implementations are **picklable** — they carry no open file handles
    or mutable process-local state, so they can be safely forwarded to
    subprocess or remote workers.

    Parameters
    ----------
    device_name :
        Name of the device requesting path information.

    Returns
    -------
    PathInfo
        Complete path and storage metadata for the device.
    """

    def __call__(self, device_name: str | None = None) -> PathInfo:
        """Return path information for the given device."""
        ...


class StaticFilenameProvider:
    """Always returns the same filename.

    Parameters
    ----------
    filename :
        The filename string to return on every call.
    """

    def __init__(self, filename: str) -> None:
        self._filename = filename

    def __call__(self, device_name: str | None = None) -> str:
        """Return the static filename."""
        return self._filename


class UUIDFilenameProvider:
    """Returns a fresh UUID4 string on every call.

    Each call produces a new UUID, so files from different acquisitions
    are never overwritten.
    """

    def __call__(self, device_name: str | None = None) -> str:
        """Return a new UUID4 filename."""
        return str(uuid.uuid4())


class AutoIncrementFilenameProvider:
    """Returns a numerically incrementing filename on each call.

    Parameters
    ----------
    base :
        Optional base prefix for the filename.
    max_digits :
        Zero-padding width for the counter.
    start :
        Initial counter value.
    step :
        Increment per call.
    delimiter :
        Separator between *base* and counter.
    """

    def __init__(
        self,
        base: str = "",
        max_digits: int = 5,
        start: int = 0,
        step: int = 1,
        delimiter: str = "_",
    ) -> None:
        self._base = base
        self._max_digits = max_digits
        self._current = start
        self._step = step
        self._delimiter = delimiter

    def __call__(self, device_name: str | None = None) -> str:
        """Return the next incremented filename."""
        if len(str(self._current)) > self._max_digits:
            raise ValueError(f"Counter exceeded maximum of {self._max_digits} digits")
        padded = f"{self._current:0{self._max_digits}}"
        name = f"{self._base}{self._delimiter}{padded}" if self._base else padded
        self._current += self._step
        return name


class StaticPathProvider:
    """Provides :class:`PathInfo` rooted at a fixed base URI.

    Composes a :class:`FilenameProvider` (for the array key / filename)
    with a fixed ``base_uri`` (for the store location).

    Parameters
    ----------
    filename_provider :
        Callable that returns a filename for each device.
    base_uri :
        Base URI for the store root (e.g. ``"file:///data"``).
    mimetype_hint :
        MIME type hint forwarded to :class:`PathInfo`.
    capacity :
        Default frame capacity forwarded to :class:`PathInfo`.
    """

    def __init__(
        self,
        filename_provider: FilenameProvider,
        base_uri: str,
        mimetype_hint: str = "application/x-zarr",
        capacity: int = 0,
    ) -> None:
        self._filename_provider = filename_provider
        self._base_uri = base_uri.rstrip("/")
        self._mimetype_hint = mimetype_hint
        self._capacity = capacity

    def __call__(self, device_name: str | None = None) -> PathInfo:
        """Return :class:`PathInfo` for *device_name*."""
        filename = self._filename_provider(device_name)
        store_uri = f"{self._base_uri}/{filename}"
        array_key = device_name or filename
        return PathInfo(
            store_uri=store_uri,
            array_key=array_key,
            capacity=self._capacity,
            mimetype_hint=self._mimetype_hint,
        )

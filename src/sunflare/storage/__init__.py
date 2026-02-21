"""Storage infrastructure for sunflare devices.

This subpackage provides the dependency-free primitives for storage:

- :class:`Writer` — abstract base class for storage backends
- :class:`FrameSink` — device-facing handle for pushing frames
- :class:`SourceInfo` — per-device frame metadata
- :class:`PathInfo` — storage path and configuration for one device
- :class:`FilenameProvider` — protocol for filename callables
- :class:`PathProvider` — protocol for path-info callables
- :class:`StaticFilenameProvider`, :class:`UUIDFilenameProvider`,
  :class:`AutoIncrementFilenameProvider` — concrete filename strategies
- :class:`StaticPathProvider` — concrete path provider
- :class:`StorageProxy` — protocol implemented by all storage backends
- :class:`StorageDescriptor` — descriptor that manages ``device.storage``

Concrete backend classes (e.g. ``ZarrWriter``) are internal
implementation details and are not exported from this package.
The application container is responsible for selecting and instantiating
the correct backend based on the session configuration.

Wiring
------
Importing this module attaches a :class:`StorageDescriptor` instance to
:class:`~sunflare.device.Device` as the ``storage`` attribute.  This
keeps ``sunflare.device`` free of any runtime import from
``sunflare.storage`` — the dependency runs in one direction only.
"""

from __future__ import annotations

from sunflare.device._base import Device as _Device
from sunflare.storage._base import FrameSink, SourceInfo, Writer
from sunflare.storage._path import (
    AutoIncrementFilenameProvider,
    FilenameProvider,
    PathInfo,
    PathProvider,
    StaticFilenameProvider,
    StaticPathProvider,
    UUIDFilenameProvider,
)
from sunflare.storage._proxy import StorageDescriptor, StorageProxy

if not isinstance(getattr(_Device, "storage", None), StorageDescriptor):
    _Device.storage = StorageDescriptor()  # type: ignore[assignment]

__all__ = [
    # base
    "Writer",
    "SourceInfo",
    "FrameSink",
    # path
    "PathInfo",
    "FilenameProvider",
    "PathProvider",
    "StaticFilenameProvider",
    "UUIDFilenameProvider",
    "AutoIncrementFilenameProvider",
    "StaticPathProvider",
    # proxy / descriptor
    "StorageProxy",
    "StorageDescriptor",
]

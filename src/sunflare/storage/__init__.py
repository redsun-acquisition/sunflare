"""Storage infrastructure for sunflare devices.

This subpackage provides:

- :class:`Writer` — abstract base class for storage backends
- :class:`ZarrWriter` — Zarr v3 backend using ``acquire-zarr``
- :class:`SourceInfo` — per-device frame metadata
- :class:`PathInfo` — storage path and configuration for one device
- :class:`FilenameProvider` — protocol for filename callables
- :class:`PathProvider` — protocol for path-info callables
- :class:`StaticFilenameProvider`, :class:`UUIDFilenameProvider`,
  :class:`AutoIncrementFilenameProvider` — concrete filename strategies
- :class:`StaticPathProvider` — concrete path provider
- :class:`StorageProxy` — protocol implemented by all storage backends
- :class:`StorageDescriptor` — descriptor that manages ``device.storage``

Wiring
------
Importing this module attaches a :class:`StorageDescriptor` instance to
:class:`~sunflare.device.Device` as the ``storage`` attribute.  This
keeps ``sunflare.device`` free of any runtime import from
``sunflare.storage`` — the dependency runs in one direction only.
"""

from __future__ import annotations

from sunflare.storage._base import SourceInfo, Writer
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
from sunflare.storage._zarr import ZarrWriter

# ---------------------------------------------------------------------------
# Attach StorageDescriptor to Device
#
# This is done here — inside sunflare.storage — so that sunflare.device has
# no runtime import from sunflare.storage.  The descriptor is installed once
# when this module is first imported, which happens at container build time.
# ---------------------------------------------------------------------------
from sunflare.device._base import Device as _Device

if not isinstance(getattr(_Device, "storage", None), StorageDescriptor):
    _Device.storage = StorageDescriptor()  # type: ignore[assignment]

__all__ = [
    # base
    "Writer",
    "SourceInfo",
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
    # backends
    "ZarrWriter",
]

# SPDX-License-Identifier: Apache-2.0
# The design of this subpackage is heavily inspired by ophyd-async
# (https://github.com/bluesky/ophyd-async), developed by the Bluesky collaboration.
# ophyd-async is licensed under the BSD 3-Clause License.
# No source code from ophyd-async has been copied; the architectural patterns
# (shared writer, path providers, FrameSink, StorageProxy protocol) were
# studied and independently re-implemented to fit the sunflare/redsun model.

"""Storage infrastructure for sunflare devices.

This subpackage provides the dependency-free primitives for storage:

- [`Writer`][sunflare.storage.Writer] — abstract base class for storage backends
- [`FrameSink`][sunflare.storage.FrameSink] — device-facing handle for pushing frames
- [`SourceInfo`][sunflare.storage.SourceInfo] — per-device frame metadata
- [`PathInfo`][sunflare.storage.PathInfo] — storage path and configuration for one device
- [`FilenameProvider`][sunflare.storage.FilenameProvider] — protocol for filename callables
- [`PathProvider`][sunflare.storage.PathProvider] — protocol for path-info callables
- [`StaticFilenameProvider`][sunflare.storage.StaticFilenameProvider],
  [`UUIDFilenameProvider`][sunflare.storage.UUIDFilenameProvider],
  [`AutoIncrementFilenameProvider`][sunflare.storage.AutoIncrementFilenameProvider] — concrete filename strategies
- [`StaticPathProvider`][sunflare.storage.StaticPathProvider] — concrete path provider
- [`StorageProxy`][sunflare.storage.StorageProxy] — protocol implemented by all storage backends
- [`StorageDescriptor`][sunflare.storage.StorageDescriptor] — descriptor for declaring `storage` on a device

Concrete backend classes (e.g. `ZarrWriter`) are internal
implementation details and are not exported from this package.
The application container is responsible for selecting and instantiating
the correct backend based on the session configuration.

Devices that require storage declare it explicitly in their class body:

```python
from sunflare.storage import StorageDescriptor


class MyDetector(Device):
    storage = StorageDescriptor()
```
"""

from __future__ import annotations

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

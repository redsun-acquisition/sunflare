# SPDX-License-Identifier: Apache-2.0
# The design of this subpackage is heavily inspired by ophyd-async
# (https://github.com/bluesky/ophyd-async), developed by the Bluesky collaboration.
# ophyd-async is licensed under the BSD 3-Clause License.
# No source code from ophyd-async has been copied; the architectural patterns
# (shared writer, path providers, FrameSink, StorageProxy protocol) were
# studied and independently re-implemented to fit the sunflare/redsun model.

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
- :class:`StorageDescriptor` — descriptor for declaring ``storage`` on a device

Concrete backend classes (e.g. ``ZarrWriter``) are internal
implementation details and are not exported from this package.
The application container is responsible for selecting and instantiating
the correct backend based on the session configuration.

Devices that require storage declare it explicitly in their class body:

.. code-block:: python

    from sunflare.storage import StorageDescriptor


    class MyDetector(Device):
        storage = StorageDescriptor()
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

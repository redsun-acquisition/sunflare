# SPDX-License-Identifier: Apache-2.0
# The design of this module is heavily inspired by ophyd-async
# (https://github.com/bluesky/ophyd-async), developed by the Bluesky collaboration.
# ophyd-async is licensed under the BSD 3-Clause License.
# No source code from ophyd-async has been copied; the StorageProxy protocol and
# opt-in descriptor pattern were studied and independently re-implemented for sunflare.

"""StorageProxy protocol and StorageDescriptor for device-side storage access."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol, overload, runtime_checkable

if TYPE_CHECKING:
    from collections.abc import Iterator

    import numpy as np
    from bluesky.protocols import StreamAsset

    from sunflare.storage._base import FrameSink


@runtime_checkable
class StorageProxy(Protocol):
    """Protocol that devices use to interact with a storage backend.

    Both local [`Writer`][sunflare.storage.Writer] instances and future
    remote proxy objects implement this protocol, so device code is
    identical regardless of where storage lives.

    Devices access the backend via their `storage` attribute, which is
    `None` when no backend has been configured for the session.
    """

    def update_source(
        self,
        name: str,
        dtype: np.dtype[np.generic],
        shape: tuple[int, ...],
        extra: dict[str, Any] | None = None,
    ) -> None:
        """Register or update a data source on the backend."""
        ...

    def prepare(self, name: str, capacity: int = 0) -> FrameSink:
        """Prepare the backend for *name* and return a [`FrameSink`][sunflare.storage.FrameSink]."""
        ...

    def kickoff(self) -> None:
        """Open the storage backend."""
        ...

    def complete(self, name: str) -> None:
        """Signal that *name* has finished writing."""
        ...

    def get_indices_written(self, name: str | None = None) -> int:
        """Return the number of frames written for *name*."""
        ...

    def collect_stream_docs(
        self,
        name: str,
        indices_written: int,
    ) -> Iterator[StreamAsset]:
        """Yield Bluesky stream documents for *name*."""
        ...


class StorageDescriptor:
    """Descriptor that manages the `storage` slot on a device.

    Stores the [`StorageProxy`][sunflare.storage.StorageProxy] (or `None`)
    in the instance `__dict__` under the key `_storage`.

    This descriptor is public so users can reference it explicitly in
    custom device classes:

    ```python
    from sunflare.storage import StorageDescriptor


    class MyDevice(Device):
        storage = StorageDescriptor()
    ```

    [`Device`][sunflare.device.Device] already carries a pre-installed
    instance, so most users never need to add it manually.
    """

    @overload
    def __get__(self, obj: None, objtype: type) -> StorageDescriptor: ...

    @overload
    def __get__(self, obj: Any, objtype: type | None) -> StorageProxy | None: ...

    def __get__(
        self,
        obj: Any,
        objtype: type | None = None,
    ) -> StorageDescriptor | StorageProxy | None:
        if obj is None:
            return self
        result: StorageProxy | None = obj.__dict__.get("_storage", None)
        return result

    def __set__(self, obj: Any, value: StorageProxy | None) -> None:
        obj.__dict__["_storage"] = value

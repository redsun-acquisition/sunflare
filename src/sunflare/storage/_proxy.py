"""StorageProxy protocol and StorageDescriptor for device-side storage access."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol, overload, runtime_checkable

if TYPE_CHECKING:
    import numpy as np
    import numpy.typing as npt
    from collections.abc import Iterator
    from bluesky.protocols import StreamAsset
    from sunflare.storage._base import SinkGenerator


@runtime_checkable
class StorageProxy(Protocol):
    """Protocol that devices use to interact with a storage backend.

    Both local :class:`~sunflare.storage.Writer` instances and future
    remote proxy objects implement this protocol, so device code is
    identical regardless of where storage lives.

    Devices access this via their :attr:`storage` attribute, which is
    ``None`` when no storage backend has been configured for the session.
    """

    def update_source(
        self,
        name: str,
        dtype: np.dtype[np.generic],
        shape: tuple[int, ...],
        extra: dict[str, Any] | None = None,
    ) -> None:
        """Register or update a data source on the backend.

        Parameters
        ----------
        name :
            Source name (typically the device name).
        dtype :
            NumPy data type of the frames.
        shape :
            Shape of individual frames.
        extra :
            Optional backend-specific metadata.
        """
        ...

    def prepare(self, name: str, capacity: int = 0) -> SinkGenerator:
        """Prepare the backend for *name* and return a frame sink.

        Parameters
        ----------
        name :
            Source name.
        capacity :
            Maximum frames (``0`` = unlimited).

        Returns
        -------
        SinkGenerator
            A primed generator; push frames via ``sink.send(frame)``.
        """
        ...

    def kickoff(self) -> None:
        """Open the storage backend."""
        ...

    def complete(self, name: str) -> None:
        """Signal that *name* has finished writing.

        The backend is closed when all active sources have called
        ``complete()``.

        Parameters
        ----------
        name :
            Source name.
        """
        ...

    def get_indices_written(self, name: str | None = None) -> int:
        """Return the number of frames written for *name*.

        Parameters
        ----------
        name :
            Source name.  If ``None``, returns the minimum across all
            active sources.
        """
        ...

    def collect_stream_docs(
        self,
        name: str,
        indices_written: int,
    ) -> Iterator[StreamAsset]:
        """Yield Bluesky stream documents for *name*.

        Parameters
        ----------
        name :
            Source name.
        indices_written :
            Frames to report in this call.
        """
        ...


class StorageDescriptor:
    """Descriptor that manages the ``storage`` slot on a device.

    Stores the :class:`StorageProxy` (or ``None``) in the instance
    ``__dict__`` under the key ``_storage``, keeping it invisible to
    ``vars()`` / attribute enumeration while still being accessible via
    ``device.storage``.

    This descriptor is public so that users can reference it explicitly
    when building custom device classes:

    .. code-block:: python

        from sunflare.storage import StorageDescriptor

        class MyDevice(Device):
            storage = StorageDescriptor()

    :class:`~sunflare.device.Device` already carries a pre-installed
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

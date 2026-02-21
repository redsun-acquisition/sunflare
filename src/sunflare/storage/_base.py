"""Abstract base classes for storage writers."""

from __future__ import annotations

import abc
import threading as th
import uuid
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import TYPE_CHECKING, Any, TypeVar

from sunflare.log import Loggable

if TYPE_CHECKING:
    from collections.abc import Generator, Iterator
    from pathlib import Path

    import numpy as np
    import numpy.typing as npt
    from bluesky.protocols import StreamAsset
    from event_model.documents import StreamDatum, StreamResource
    from typing_extensions import Self

    SinkGenerator: TypeAlias = Generator[None, npt.NDArray[np.generic], None]

from typing import TypeAlias


@dataclass
class SourceInfo:
    """Metadata for a registered data source.

    Parameters
    ----------
    name :
        Name of the data source (e.g. the device name).
    dtype :
        NumPy data type of the source frames.
    shape :
        Shape of individual frames from the source.
    data_key :
        Bluesky data key for stream documents.
    mimetype :
        MIME type hint for the storage backend.
    frames_written :
        Running count of frames written so far.
    collection_counter :
        Frames reported in the current collection cycle.
    stream_resource_uid :
        UID of the current ``StreamResource`` document.
    extra :
        Optional extra metadata for backend-specific use (e.g. OME-Zarr
        axis labels, physical units).  Base ``Writer`` ignores this field;
        specialised subclasses may read it.
    """

    name: str
    dtype: np.dtype[np.generic]
    shape: tuple[int, ...]
    data_key: str
    mimetype: str = "application/octet-stream"
    frames_written: int = 0
    collection_counter: int = 0
    stream_resource_uid: str = field(default_factory=lambda: str(uuid.uuid4()))
    extra: dict[str, Any] = field(default_factory=dict)


_W = TypeVar("_W", bound="Writer")


class Writer(abc.ABC, Loggable):
    """Abstract base class for data writers.

    This interface loosely follows the Bluesky ``Flyable`` protocol while
    remaining generic — methods do not need to return a ``Status`` object;
    that is left to the device that owns the writer.

    A single ``Writer`` instance is shared by all devices in a session.
    Each device registers itself as a *source* via :meth:`update_source`
    and obtains a dedicated frame sink via :meth:`prepare`.

    Call order per acquisition:

    1. ``prepare(name, capacity)`` — called by each device to set up its source
    2. ``kickoff()`` — called once to open the storage backend
    3. ``complete(name)`` — called by each device when it finishes writing

    Subclasses must implement:

    - :attr:`mimetype` — MIME type string for this backend
    - :meth:`prepare` — source-specific setup; must call ``super().prepare()``
    - :meth:`kickoff` — open the backend; must call ``super().kickoff()``
    - :meth:`_write_frame` — write one frame to the backend
    - :meth:`_finalize` — close the backend when all sources are complete

    Parameters
    ----------
    name :
        Unique name for this writer instance (used for logging).
    """

    def __init__(self, name: str) -> None:
        self._name = name
        self._store_path = ""
        self._capacity = 0
        self._lock = th.Lock()
        self._is_open = False
        self._sources: dict[str, SourceInfo] = {}
        self._frame_sinks: dict[str, Generator[None, npt.NDArray[np.generic], None]] = (
            {}
        )

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def is_open(self) -> bool:
        """Return whether the writer is currently open."""
        return self._is_open

    @property
    def name(self) -> str:
        """Return the name of this writer."""
        return self._name

    @property
    @abc.abstractmethod
    def mimetype(self) -> str:
        """Return the MIME type string for this backend."""
        ...

    @property
    def sources(self) -> MappingProxyType[str, SourceInfo]:
        """Return a read-only view of the registered data sources."""
        return MappingProxyType(self._sources)

    # ------------------------------------------------------------------
    # Source management
    # ------------------------------------------------------------------

    def update_source(
        self,
        name: str,
        dtype: np.dtype[np.generic],
        shape: tuple[int, ...],
        extra: dict[str, Any] | None = None,
    ) -> None:
        """Register or update a data source.

        A *source* is a device that will push frames to this writer.
        If the source name already exists its metadata is updated;
        otherwise a new entry is created.

        Parameters
        ----------
        name :
            Source name (typically the device name).
        dtype :
            NumPy data type of the frames.
        shape :
            Shape of individual frames.
        extra :
            Optional extra metadata forwarded to :class:`SourceInfo`.
            Backend-specific writers (e.g. a future ``OMEZarrWriter``) may
            read this; the base ``Writer`` ignores it.

        Raises
        ------
        RuntimeError
            If the writer is currently open.
        """
        if self._is_open:
            raise RuntimeError("Cannot update sources while writer is open.")

        data_key = f"{name}:buffer:stream"
        self._sources[name] = SourceInfo(
            name=name,
            dtype=dtype,
            shape=shape,
            data_key=data_key,
            mimetype=self.mimetype,
            extra=extra or {},
        )
        self.logger.debug(f"Updated source '{name}' with shape {shape}")

    def clear_source(self, name: str, *, raise_if_missing: bool = False) -> None:
        """Remove a registered data source.

        Parameters
        ----------
        name :
            Source name to remove.
        raise_if_missing :
            If ``True``, raise :exc:`KeyError` when the source is not found.

        Raises
        ------
        RuntimeError
            If the writer is currently open.
        KeyError
            If ``raise_if_missing`` is ``True`` and the source is absent.
        """
        if self._is_open:
            raise RuntimeError("Cannot clear sources while writer is open.")

        try:
            del self._sources[name]
            self.logger.debug(f"Cleared source '{name}'")
        except KeyError as exc:
            self.logger.error(f"Source '{name}' not found.")
            if raise_if_missing:
                raise exc

    def get_indices_written(self, name: str | None = None) -> int:
        """Return the number of frames written for a source.

        Parameters
        ----------
        name :
            Source name.  If ``None``, returns the minimum across all
            sources (useful for synchronisation checks).

        Raises
        ------
        KeyError
            If *name* is not registered.
        """
        if name is None:
            if not self._sources:
                return 0
            return min(s.frames_written for s in self._sources.values())

        if name not in self._sources:
            raise KeyError(f"Unknown source '{name}'")
        return self._sources[name].frames_written

    def reset_collection_state(self, name: str) -> None:
        """Reset the collection counter for a new acquisition.

        Parameters
        ----------
        name :
            Source name to reset.
        """
        source = self._sources[name]
        source.collection_counter = 0
        source.stream_resource_uid = str(uuid.uuid4())

    # ------------------------------------------------------------------
    # Frame sink
    # ------------------------------------------------------------------

    def _create_frame_sink(self, name: str) -> SinkGenerator:
        """Return a primed generator that accepts frames via ``send()``."""
        if name not in self._sources:
            raise KeyError(f"Unknown source '{name}'")

        source = self._sources[name]

        def _frame_sink() -> SinkGenerator:
            try:
                while True:
                    frame = yield
                    with self._lock:
                        self._write_frame(name, frame)
                        source.frames_written += 1
            except GeneratorExit:
                pass

        return _frame_sink()

    # ------------------------------------------------------------------
    # Acquisition lifecycle
    # ------------------------------------------------------------------

    @abc.abstractmethod
    def kickoff(self) -> None:
        """Open the storage backend for a new acquisition.

        Subclasses must call ``super().kickoff()`` to set :attr:`is_open`.
        Subsequent calls while already open must be no-ops.
        """
        if not self._is_open:
            self._is_open = True

    @abc.abstractmethod
    def prepare(self, name: str, capacity: int = 0) -> SinkGenerator:
        """Prepare storage for a specific source and return its frame sink.

        Called once per device per acquisition.  Resets per-source counters
        and creates (or reuses) the frame sink generator.

        Parameters
        ----------
        name :
            Source name.
        capacity :
            Maximum frames to accept (``0`` = unlimited).

        Returns
        -------
        SinkGenerator
            A primed generator; callers push frames via ``sink.send(frame)``.

        Raises
        ------
        KeyError
            If *name* has not been registered via :meth:`update_source`.
        """
        source = self._sources[name]
        source.frames_written = 0
        source.collection_counter = 0
        source.stream_resource_uid = str(uuid.uuid4())

        if name not in self._frame_sinks:
            sink = self._create_frame_sink(name)
            next(sink)
            self._frame_sinks[name] = sink

        return self._frame_sinks[name]

    def complete(self, name: str) -> None:
        """Mark acquisition complete for *name* and close when all done.

        When the last active source calls ``complete()``, the backend is
        finalised and :attr:`is_open` is set to ``False``.

        Parameters
        ----------
        name :
            Source name.
        """
        self._frame_sinks[name].close()
        del self._frame_sinks[name]
        if not self._frame_sinks:
            self._finalize()
            self._is_open = False

    # ------------------------------------------------------------------
    # Backend hooks (subclass responsibility)
    # ------------------------------------------------------------------

    @abc.abstractmethod
    def _write_frame(self, name: str, frame: npt.NDArray[np.generic]) -> None:
        """Write one frame to the backend.

        Parameters
        ----------
        name :
            Source name (routes the write to the correct array/dataset).
        frame :
            Frame data; dtype and shape are described in the corresponding
            :class:`SourceInfo`.
        """
        ...

    @abc.abstractmethod
    def _finalize(self) -> None:
        """Close the backend after all sources have completed."""
        ...

    # ------------------------------------------------------------------
    # Stream document generation
    # ------------------------------------------------------------------

    def collect_stream_docs(
        self,
        name: str,
        indices_written: int,
    ) -> Iterator[StreamAsset]:
        """Yield ``StreamResource`` and ``StreamDatum`` documents for *name*.

        Parameters
        ----------
        name :
            Source name.
        indices_written :
            Number of frames to report in this call.

        Yields
        ------
        StreamAsset
            Tuples of ``("stream_resource", doc)`` or ``("stream_datum", doc)``.

        Raises
        ------
        KeyError
            If *name* is not registered.
        """
        if name not in self._sources:
            raise KeyError(f"Unknown source '{name}'")

        source = self._sources[name]

        if indices_written == 0:
            return

        frames_to_report = min(indices_written, source.frames_written)

        if source.collection_counter >= frames_to_report:
            return

        if source.collection_counter == 0:
            stream_resource: StreamResource = {
                "data_key": source.data_key,
                "mimetype": source.mimetype,
                "parameters": {"array_name": source.name},
                "uid": source.stream_resource_uid,
                "uri": self._store_path,
            }
            yield ("stream_resource", stream_resource)

        stream_datum: StreamDatum = {
            "descriptor": "",
            "indices": {"start": source.collection_counter, "stop": frames_to_report},
            "seq_nums": {"start": 0, "stop": 0},
            "stream_resource": source.stream_resource_uid,
            "uid": f"{source.stream_resource_uid}/{source.collection_counter}",
        }
        yield ("stream_datum", stream_datum)

        source.collection_counter = frames_to_report

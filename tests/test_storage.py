"""Smoke tests for sunflare.storage."""

from __future__ import annotations

import time
from typing import Any
from unittest.mock import MagicMock

import numpy as np
import pytest
from bluesky.protocols import Descriptor, Reading

import sunflare.storage  # noqa: F401 — triggers descriptor wiring on Device
from sunflare.device import Device
from sunflare.storage import (
    FrameSink,
    AutoIncrementFilenameProvider,
    PathInfo,
    StaticFilenameProvider,
    StaticPathProvider,
    StorageDescriptor,
    StorageProxy,
    UUIDFilenameProvider,
    Writer,
    ZarrWriter,
)
from sunflare.storage._proxy import StorageDescriptor


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class _MinimalDevice(Device):
    """Minimal concrete Device for testing the storage descriptor."""

    def __init__(self, name: str, /) -> None:
        super().__init__(name)

    def describe_configuration(self) -> dict[str, Descriptor]:
        return {}

    def read_configuration(self) -> dict[str, Reading[Any]]:
        return {}


class _ConcreteWriter(Writer):
    """Minimal Writer subclass for testing the abstract base."""

    def __init__(self, name: str) -> None:
        super().__init__(name)
        self._frames: dict[str, list[Any]] = {}
        self._finalized = False

    @property
    def mimetype(self) -> str:
        return "application/x-test"

    def prepare(self, name: str, capacity: int = 0) -> FrameSink:
        self._frames.setdefault(name, [])
        self._store_path = "file:///tmp/test.zarr"
        return super().prepare(name, capacity)

    def kickoff(self) -> None:
        super().kickoff()

    def _write_frame(self, name: str, frame: Any) -> None:
        self._frames[name].append(frame)

    def _finalize(self) -> None:
        self._finalized = True


# ---------------------------------------------------------------------------
# StorageDescriptor
# ---------------------------------------------------------------------------


class TestStorageDescriptor:
    def test_descriptor_installed_on_device(self) -> None:
        """Importing sunflare.storage must attach StorageDescriptor to Device."""
        assert isinstance(Device.__dict__.get("storage"), StorageDescriptor)

    def test_default_is_none(self) -> None:
        device = _MinimalDevice("dev")
        assert device.storage is None

    def test_set_and_get(self) -> None:
        device = _MinimalDevice("dev")
        mock_proxy = MagicMock(spec=StorageProxy)
        device.storage = mock_proxy
        assert device.storage is mock_proxy

    def test_set_none_resets(self) -> None:
        device = _MinimalDevice("dev")
        device.storage = MagicMock(spec=StorageProxy)
        device.storage = None
        assert device.storage is None

    def test_independent_per_instance(self) -> None:
        """Each device instance must have its own storage slot."""
        dev_a = _MinimalDevice("a")
        dev_b = _MinimalDevice("b")
        mock = MagicMock(spec=StorageProxy)
        dev_a.storage = mock
        assert dev_b.storage is None

    def test_class_access_returns_descriptor(self) -> None:
        assert isinstance(Device.storage, StorageDescriptor)


# ---------------------------------------------------------------------------
# PathInfo
# ---------------------------------------------------------------------------


class TestPathInfo:
    def test_defaults(self) -> None:
        pi = PathInfo(store_uri="file:///data/scan.zarr", array_key="camera")
        assert pi.capacity == 0
        assert pi.mimetype_hint == "application/x-zarr"
        assert pi.extra == {}

    def test_custom_values(self) -> None:
        pi = PathInfo(
            store_uri="s3://bucket/scan.zarr",
            array_key="det",
            capacity=100,
            mimetype_hint="application/x-zarr",
            extra={"units": "nm"},
        )
        assert pi.store_uri == "s3://bucket/scan.zarr"
        assert pi.capacity == 100
        assert pi.extra == {"units": "nm"}


# ---------------------------------------------------------------------------
# FilenameProviders
# ---------------------------------------------------------------------------


class TestStaticFilenameProvider:
    def test_always_same(self) -> None:
        p = StaticFilenameProvider("scan001")
        assert p() == "scan001"
        assert p("camera") == "scan001"
        assert p() == "scan001"


class TestUUIDFilenameProvider:
    def test_returns_string(self) -> None:
        p = UUIDFilenameProvider()
        name = p()
        assert isinstance(name, str)
        assert len(name) == 36  # UUID4 canonical form

    def test_unique_per_call(self) -> None:
        p = UUIDFilenameProvider()
        assert p() != p()


class TestAutoIncrementFilenameProvider:
    def test_increments(self) -> None:
        p = AutoIncrementFilenameProvider(base="scan", max_digits=3, start=0)
        assert p() == "scan_000"
        assert p() == "scan_001"
        assert p() == "scan_002"

    def test_no_base(self) -> None:
        p = AutoIncrementFilenameProvider(max_digits=2, start=5)
        assert p() == "05"
        assert p() == "06"

    def test_overflow_raises(self) -> None:
        p = AutoIncrementFilenameProvider(max_digits=1, start=10)
        with pytest.raises(ValueError, match="exceeded maximum"):
            p()


# ---------------------------------------------------------------------------
# StaticPathProvider
# ---------------------------------------------------------------------------


class TestStaticPathProvider:
    def test_basic(self) -> None:
        fp = StaticFilenameProvider("scan001")
        pp = StaticPathProvider(fp, base_uri="file:///data")
        info = pp("camera")
        assert info.store_uri == "file:///data/scan001"
        assert info.array_key == "camera"

    def test_trailing_slash_stripped(self) -> None:
        fp = StaticFilenameProvider("scan")
        pp = StaticPathProvider(fp, base_uri="file:///data/")
        info = pp("det")
        assert info.store_uri == "file:///data/scan"

    def test_none_device_name(self) -> None:
        fp = StaticFilenameProvider("scan")
        pp = StaticPathProvider(fp, base_uri="file:///data")
        info = pp(None)
        # array_key falls back to filename when device_name is None
        assert info.array_key == "scan"

    def test_capacity_forwarded(self) -> None:
        fp = StaticFilenameProvider("s")
        pp = StaticPathProvider(fp, base_uri="file:///d", capacity=50)
        assert pp("x").capacity == 50


# ---------------------------------------------------------------------------
# Writer (via _ConcreteWriter)
# ---------------------------------------------------------------------------


class TestWriter:
    def _make_writer(self) -> _ConcreteWriter:
        return _ConcreteWriter("test_writer")

    def test_initial_state(self) -> None:
        w = self._make_writer()
        assert not w.is_open
        assert w.name == "test_writer"
        assert len(w.sources) == 0

    def test_update_source(self) -> None:
        w = self._make_writer()
        w.update_source("cam", np.dtype("uint8"), (512, 512))
        assert "cam" in w.sources
        assert w.sources["cam"].shape == (512, 512)
        assert w.sources["cam"].mimetype == "application/x-test"

    def test_update_source_while_open_raises(self) -> None:
        w = self._make_writer()
        w.update_source("cam", np.dtype("uint8"), (64, 64))
        w.prepare("cam")
        w.kickoff()
        with pytest.raises(RuntimeError, match="open"):
            w.update_source("cam2", np.dtype("uint8"), (64, 64))

    def test_prepare_returns_sink(self) -> None:
        w = self._make_writer()
        w.update_source("cam", np.dtype("uint8"), (4, 4))
        sink = w.prepare("cam")
        assert isinstance(sink, FrameSink)
        assert hasattr(sink, "write")
        assert hasattr(sink, "close")

    def test_prepare_unknown_source_raises(self) -> None:
        w = self._make_writer()
        with pytest.raises(KeyError):
            w.prepare("unknown")

    def test_kickoff_sets_open(self) -> None:
        w = self._make_writer()
        w.update_source("cam", np.dtype("uint8"), (4, 4))
        w.prepare("cam")
        w.kickoff()
        assert w.is_open

    def test_frame_written_via_sink(self) -> None:
        w = self._make_writer()
        w.update_source("cam", np.dtype("uint8"), (2, 2))
        sink = w.prepare("cam")
        w.kickoff()
        frame = np.zeros((2, 2), dtype="uint8")
        sink.write(frame)
        assert w.get_indices_written("cam") == 1
        assert w._frames["cam"][0] is frame

    def test_complete_finalizes_when_last_source_done(self) -> None:
        w = self._make_writer()
        w.update_source("cam", np.dtype("uint8"), (2, 2))
        w.prepare("cam")
        w.kickoff()
        w.complete("cam")
        assert not w.is_open
        assert w._finalized

    def test_two_sources_complete_sequence(self) -> None:
        w = self._make_writer()
        for src in ("cam_a", "cam_b"):
            w.update_source(src, np.dtype("uint8"), (2, 2))
            w.prepare(src)
        w.kickoff()
        # first complete should not finalize
        w.complete("cam_a")
        assert w.is_open
        # second complete should finalize
        w.complete("cam_b")
        assert not w.is_open
        assert w._finalized

    def test_clear_source(self) -> None:
        w = self._make_writer()
        w.update_source("cam", np.dtype("uint8"), (2, 2))
        w.clear_source("cam")
        assert "cam" not in w.sources

    def test_clear_missing_source_silent(self) -> None:
        w = self._make_writer()
        w.clear_source("nonexistent")  # should not raise

    def test_clear_missing_source_raises_if_requested(self) -> None:
        w = self._make_writer()
        with pytest.raises(KeyError):
            w.clear_source("nonexistent", raise_if_missing=True)

    def test_get_indices_written_min_across_sources(self) -> None:
        w = self._make_writer()
        for src in ("a", "b"):
            w.update_source(src, np.dtype("uint8"), (2, 2))
            w.prepare(src)
        w.kickoff()
        frame = np.zeros((2, 2), dtype="uint8")
        w._sinks["a"].write(frame) if hasattr(w, "_sinks") else None
        w._sources["a"].frames_written = 1
        # b has 0 frames — min should be 0
        assert w.get_indices_written() == 0

    def test_collect_stream_docs_emits_resource_then_datum(self) -> None:
        w = self._make_writer()
        w.update_source("cam", np.dtype("uint8"), (2, 2))
        w.prepare("cam")
        w.kickoff()
        # Simulate frames written
        w._sources["cam"].frames_written = 3
        docs = list(w.collect_stream_docs("cam", 3))
        kinds = [d[0] for d in docs]
        assert "stream_resource" in kinds
        assert "stream_datum" in kinds

    def test_collect_stream_docs_no_duplicate_resource(self) -> None:
        w = self._make_writer()
        w.update_source("cam", np.dtype("uint8"), (2, 2))
        w.prepare("cam")
        w.kickoff()
        w._sources["cam"].frames_written = 2
        # First call — should include stream_resource
        docs1 = list(w.collect_stream_docs("cam", 2))
        assert any(d[0] == "stream_resource" for d in docs1)
        # Update frames and call again — must NOT emit stream_resource again
        w._sources["cam"].frames_written = 4
        docs2 = list(w.collect_stream_docs("cam", 4))
        assert not any(d[0] == "stream_resource" for d in docs2)


# ---------------------------------------------------------------------------
# StorageProxy structural check
# ---------------------------------------------------------------------------


class TestStorageProxyProtocol:
    def test_writer_satisfies_proxy(self) -> None:
        """Writer must structurally satisfy StorageProxy."""
        assert issubclass(_ConcreteWriter, StorageProxy)  # type: ignore[arg-type]

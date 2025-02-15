"""Wrapper for the :class:`~bluesky.run_engine.RunEngine` class to allow execution without blocking the main thread.

The original implementation of the ``RunEngine`` blocks the
execution of the main thread when the ``__call__`` method is used.
This wrapper uses a ``ThreadPoolExecutor`` to run the execution
in a separate thread, allowing the main thread to continue executing other tasks.

.. note::

    The ``context_manager`` attribute is forced to be an empty list to
    avoid the use of the built-in ``SignalHandler`` context manager.
    The rationale is that the original implementation is meant
    for interactive usage (e.g., Jupyter notebooks, scripts) and not for
    applications relying on an event loop.

    When invoking ``RunEngine.__call__`` not in the main thread,
    this will cause an exception as in Python
    signal handlers (e.g. ``SIGINT``) can not
    be handled in threads other than the main thread.
"""

from __future__ import annotations

import asyncio
import sys
from concurrent.futures import Future, ThreadPoolExecutor
from typing import Any, Callable, Optional, Union

import zmq
from bluesky.run_engine import (
    RunEngine as BlueskyRunEngine,
)
from bluesky.run_engine import RunEngineResult
from event_model import (
    Datum,
    DatumPage,
    Event,
    EventDescriptor,
    EventPage,
    Resource,
    RunStart,
    RunStop,
    StreamDatum,
    StreamResource,
)

from sunflare.virtual import encode

__all__ = ["RunEngine", "RunEngineResult"]

DocumentType = Union[
    RunStart,
    RunStop,
    EventDescriptor,
    Event,
    EventPage,
    Datum,
    DatumPage,
    Resource,
    StreamResource,
    StreamDatum,
]

REResultType = Union[RunEngineResult, tuple[str, ...]]
FuncSocket = Union[Callable[[str, dict[str, Any]], None], zmq.Socket[bytes]]


class RunEngine(BlueskyRunEngine):
    __doc__ = BlueskyRunEngine.__doc__

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        # force the context_managers to be empty,
        # otherwise the RunEngine will try to use the
        # SignalHandler context manager
        kwargs["context_managers"] = []
        self.socket: Optional[zmq.Socket[bytes]] = kwargs.pop("socket", None)
        self._executor = ThreadPoolExecutor(max_workers=1)
        self._result: REResultType
        super().__init__(*args, **kwargs)

        # override pause message to be an empty string
        self.pause_msg = ""

        # Python 3.9 explicitly requires the event loop to be set
        # when running in a separate thread
        if sys.version_info < (3, 10):
            self._run_in_executor = self.__run_in_executor_explicit
        else:
            self._run_in_executor = self.__run_in_executor

    def emit_sync(self, name: str, doc: dict[str, Any]) -> None:
        if self.socket is not None:
            self.socket.send_multipart([name.encode(), encode(doc)])
        super().emit_sync(name, doc)

    def __run_in_executor_explicit(self, *args: Any, **kwargs: Any) -> REResultType:
        asyncio.set_event_loop(self.loop)
        return super().__call__(*args, **kwargs)  # type: ignore[no-any-return]

    def __run_in_executor(self, *args: Any, **kwargs: Any) -> REResultType:
        return super().__call__(*args, **kwargs)  # type: ignore[no-any-return]

    def __call__(self, *args: Any, **metadata_kw: Any) -> Future[REResultType]:
        self._fut = self._executor.submit(
            lambda: self._run_in_executor(*args, **metadata_kw)
        )
        self._fut.add_done_callback(self._set_result)
        return self._fut

    def _set_result(self, fut: Future[REResultType]) -> None:
        self._result = fut.result()

    @property
    def result(self) -> Union[REResultType]:
        return self._result

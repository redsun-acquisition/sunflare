"""Wrapper for the :class:`~bluesky.run_engine.RunEngine` class to allow execution without blocking the main thread."""

from __future__ import annotations

import asyncio
import sys
from concurrent.futures import Future, ThreadPoolExecutor
from itertools import count
from typing import Any, Callable, Optional, Union

import zmq
from bluesky.run_engine import (
    RunEngine as BlueskyRunEngine,
)
from bluesky.run_engine import RunEngineResult
from bluesky.utils import DuringTask
from event_model import (
    Datum,
    DatumPage,
    DocumentNames,
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

_prefix_counter = count()


class RunEngine(BlueskyRunEngine):
    """Subclass of ``bluesky.run_engine.RunEngine`` to allow execution in a separate thread.

    Additional features:

    - ``socket``: A ZMQ socket to send messages to a remote endpoint;
    - ``socket_prefix``: A prefix to be used in the ZMQ topic when sending messages.

    When launching a plan, the ``RunEngine``, the ``__call__`` method returns a ``Future`` object.
    This allows to set a callback on the future to retrieve the result of the execution.
    Alternatively, the result can be accessed directly from the ``result`` attribute
    when the future is done.

    Suppressed features:

    - ``context_managers``: The context managers are forced to be an empty list to
      avoid the use of the built-in ``SignalHandler`` context manager.

    The rationale is that the original implementation is meant for
    interactive usage (e.g., Jupyter notebooks, scripts) and not
    for applications relying on an event loop.

    - ``pause_msg``: Overridden to be an empty string.
    - ``during_task``: Overridden to ``DuringTask``, so the ``RunEngine``
      does not interact with any possible event loop in the main thread.

    For the original class initializer signature, refer to the :class:`~bluesky.run_engine.RunEngine` documentation.

    Parameters
    ----------
    socket_prefix : ``str``, keyword-only, optional
        Prefix to be used in the ZMQ topic when sending messages.
        Default is ``RE{N}``, where ``{N}`` is a counter that increments for each instance.
    socket : ``zmq.Socket[bytes]``, keyword-only, optional
        ZMQ socket to send messages to a remote endpoint.
        Default is ``None`` (no messages are sent).
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        # force the context_managers to be empty,
        # otherwise the RunEngine will try to use the
        # SignalHandler context manager
        kwargs["context_managers"] = []
        kwargs["during_task"] = DuringTask()
        self.socket_prefix: str = kwargs.pop(
            "socket_prefix", f"RE{next(_prefix_counter)}"
        )
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

    def emit_sync(self, name: DocumentNames, doc: dict[str, Any]) -> None:
        """Emit a document synchronously.

        Reimplemented to send documents also through a ZMQ socket.

        .. warning::

            This method is not meant to be used directly.
            The ``RunEngine`` will emit documents automatically
            during the execution of a plan. Any
            subscriber will receive the documents.

        """
        if self.socket is not None:
            topic = f"{self.socket_prefix}:{str(DocumentNames[name])}"
            self.socket.send_multipart([topic.encode(), encode(doc)])
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

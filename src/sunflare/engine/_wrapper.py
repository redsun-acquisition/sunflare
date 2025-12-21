"""Wrapper for the :class:`~bluesky.run_engine.RunEngine` class to allow execution without blocking the main thread."""

from __future__ import annotations

from concurrent.futures import Future, ThreadPoolExecutor
from typing import TYPE_CHECKING, Any

from bluesky.run_engine import (
    RunEngine as BlueskyRunEngine,
)
from bluesky.run_engine import RunEngineResult
from bluesky.utils import DuringTask, RunEngineInterrupted
from event_model.documents import Document

if TYPE_CHECKING:
    from typing import Iterable

    from bluesky.utils import Msg, Subscribers

__all__ = ["RunEngine", "RunEngineResult", "RunEngineInterrupted", "Document"]

REResultType = RunEngineResult | tuple[str, ...] | Exception


class RunEngine(BlueskyRunEngine):
    """Subclass of ``bluesky.run_engine.RunEngine`` to allow execution in a separate thread.

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
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        # force the context_managers to be empty,
        # otherwise the RunEngine will try to use the
        # SignalHandler context manager
        kwargs["context_managers"] = []
        kwargs["during_task"] = DuringTask()
        self._executor = ThreadPoolExecutor(max_workers=1)
        self._result: REResultType
        super().__init__(*args, **kwargs)

        # override pause message to be an empty string
        self.pause_msg = ""

    def __call__(  # type: ignore[override]
        self,
        plan: Iterable[Msg],
        subs: Subscribers | None = None,
        /,
        **metadata_kw: Any,
    ) -> Future[RunEngineResult | tuple[str, ...]]:
        self._fut = self._executor.submit(
            super().__call__,
            plan,
            subs,
            **metadata_kw,
        )
        self._fut.add_done_callback(self._set_result)
        return self._fut

    def resume(self) -> Future[RunEngineResult | tuple[str, ...]]:
        """Resume the paused plan in a separate thread.

        If the plan has been paused, the initial
        future returned by ``__call__`` will be set as completed.

        With this method, the plan is resumed in a separate thread,
        and a new future is returned.

        Returns
        -------
        ``Future[RunEngineResult | tuple[str, ...]]``
            Future object representing the result of the resumed plan.
        """
        self._fut = self._executor.submit(super().resume)
        self._fut.add_done_callback(self._set_result)
        return self._fut

    def _set_result(self, fut: Future[RunEngineResult | tuple[str, ...]]) -> None:
        try:
            self._result = fut.result()
        except Exception as exc:
            self._result = exc

    @property
    def result(self) -> REResultType:
        return self._result

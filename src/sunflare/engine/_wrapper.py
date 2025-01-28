"""Wrapper for the RunEngine class to allow execution without blocking the main thread."""

from concurrent.futures import Future, ThreadPoolExecutor
from typing import Any, Union

from bluesky.run_engine import RunEngine as BlueskyRunEngine
from bluesky.run_engine import RunEngineResult

__all__ = ["RunEngine", "RunEngineResult"]


class RunEngine(BlueskyRunEngine):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        # force the context_managers to be empty,
        # otherwise the RunEngine will try to use the
        # SignalHandler context manager
        kwargs["context_managers"] = []
        self._executor = ThreadPoolExecutor(max_workers=1)
        self._result: Union[RunEngineResult, tuple[str, ...]]
        super().__init__(*args, **kwargs)  # type: ignore[no-untyped-call]

    def __call__(self, *args: Any, **metadata_kw: Any) -> Future[Any]:
        self._fut = self._executor.submit(super().__call__, *args, **metadata_kw)
        self._fut.add_done_callback(self._set_result)
        return self._fut

    def _set_result(self, fut: Future[Any]) -> None:
        self._result = fut.result()

    @property
    def result(self) -> Union[RunEngineResult, tuple[str, ...]]:
        return self._result

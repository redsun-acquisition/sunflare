import asyncio
import sys
import threading
from typing import Optional

from sunflare.log import Loggable


class LoopManager(Loggable):
    """Helper class to launch the async subscribers loop."""

    _loop: Optional[asyncio.AbstractEventLoop]
    _thread: threading.Thread

    def __init__(self) -> None:
        self._loop = None

    def __call__(self) -> asyncio.AbstractEventLoop:
        """Return the async subscribers event loop is running.

        If no loop is running, it will be created and started
        in a background thread.

        Returns
        -------
        asyncio.AbstractEventLoop
            The async subscribers event loop.
        """
        if self._loop is None:
            self.debug("No loop found, creating a new one")
            if sys.platform == "win32":
                self.debug(
                    "Setting WindowsSelectorEventLoopPolicy (required for ZMQ on Windows)"
                )
                asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
                self._loop = asyncio.new_event_loop()
            else:
                self._loop = asyncio.new_event_loop()
            self._thread = threading.Thread(target=self._loop.run_forever, daemon=True)
            self._thread.name = "async-subscribers-loop"
            self._thread.start()
            self.debug("Loop started in thread %s", self._thread.name)
        return self._loop

    def stop(self) -> None:
        """Stop the async subscribers event loop."""
        if self._loop is not None:
            self._loop.call_soon_threadsafe(self._loop.stop)
            self._thread.join()
            self.debug(f"{self._thread.name} stopped")


_loop_manager = LoopManager()

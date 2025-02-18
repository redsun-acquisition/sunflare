import asyncio
import sys
import threading

import zmq
import zmq.asyncio

from sunflare.log import Loggable


class SubscriberLoop(Loggable):
    """Background thread to run the async subscribers event loop.

    Spawns a daemon thread to run an asyncio event loop.
    At initialization, it will create a shadow
    ZMQ context compatible with asyncio.

    Parameters
    ----------
    ctx : ``zmq.Context``
        The synchronous context to shadow.
    """

    _ctx: zmq.asyncio.Context
    _loop: asyncio.AbstractEventLoop
    _thread: threading.Thread

    def __init__(self, ctx: zmq.Context[zmq.Socket[bytes]]) -> None:
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

        async def _inner_init(ctx: zmq.Context[zmq.Socket[bytes]]) -> None:
            self._ctx = zmq.asyncio.Context(ctx)

        fut = asyncio.run_coroutine_threadsafe(_inner_init(ctx), self._loop)

        # wait for initialization
        while not fut.done():
            ...

    async def _stop_ctx(self) -> None:
        """Stop the shadow context."""
        self._ctx.term()

    def stop(self) -> None:
        """Stop the async subscribers event loop."""
        asyncio.run_coroutine_threadsafe(self._stop_ctx(), self._loop)
        self._loop.call_soon_threadsafe(self._loop.stop)
        self._thread.join()
        self.debug(f"{self._thread.name} stopped")

    @property
    def loop(self) -> asyncio.AbstractEventLoop:
        """Get the event loop."""
        return self._loop

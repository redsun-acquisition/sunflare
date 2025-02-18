import logging
import threading
from abc import abstractmethod
from concurrent.futures import Future
from typing import Awaitable, Iterable, Optional, Protocol, TypeVar, Union

import zmq
import zmq.asyncio
from typing_extensions import TypeIs

from ._bus import VirtualBus

T = TypeVar("T")


def _isawaitable(ret: Union[T, Awaitable[T]]) -> TypeIs[Awaitable[T]]:
    return hasattr(ret, "__await__")


async def maybe_await(ret: Union[T, Awaitable[T]]) -> T:
    """Await (possibly) for the return value.

    Helper function to support both synchronous and asynchronous
    return values from a method.
    """
    if _isawaitable(ret):
        return await ret
    return ret


class Publisher:
    """Publisher mixin class.

    Creates a publisher socket for the virtual bus,
    which can be used to send messages to subscribers
    over the virtual bus.

    Parameters
    ----------
    virtual_bus : :class:`~sunflare.virtual.VirtualBus`
        Virtual bus.

    Attributes
    ----------
    pub_socket : ``zmq.Socket[bytes]``
        Publisher socket.
    """

    pub_socket: zmq.Socket[bytes]

    def __init__(
        self,
        virtual_bus: VirtualBus,
    ) -> None:
        self.pub_socket = virtual_bus.connect_publisher()


class Consumer(Protocol):
    """Helper protocol for subscribers."""

    @abstractmethod
    def consume(self, content: list[bytes]) -> Union[None, Awaitable[None]]:
        """Consume the incoming message.

        Provided by the user to perform operations
        on incoming messages.

        ``consume`` can be synchronous, e.g.:

        .. code-block:: python

            def consume(self, content: list[bytes]) -> None:
                pass

        ... or asynchronous, e.g.:

        .. code-block:: python

            async def consume(self, content: list[bytes]) -> None:
                pass

        Parameters
        ----------
        content : ``Iterable[bytes]``
            Incoming message.
        """


class SyncSubscriber(Consumer):
    """Synchronous subscriber mixin class.

    The synchronous subscriber deploys a background thread
    which will poll the virtual bus for incoming messages.

    Parameters
    ----------
    virtual_bus : :class:`~sunflare.virtual.VirtualBus`
        Virtual bus.
    topics : ``str | Iterable[str]``
        Subscriber topics.

    Attributes
    ----------
    sub_socket : ``zmq.Socket[bytes]``
        Subscriber socket.
    sub_poller : ``zmq.Poller``
        Poller for the subscriber socket.
    sub_thread : ``threading.Thread``
        Subscriber thread.
    sub_topics : ``str | Iterable[str]``
        Subscriber topics.
    """

    sub_socket: zmq.Socket[bytes]
    sub_poller: zmq.Poller
    sub_thread: threading.Thread
    sub_topics: Optional[Union[str, Iterable[str]]]

    def __init__(
        self,
        virtual_bus: VirtualBus,
        topics: Optional[Union[str, Iterable[str]]] = None,
    ) -> None:
        self._logger = logging.getLogger("redsun")
        self.sub_socket, self.sub_poller = virtual_bus.connect_subscriber(topics)
        self.sub_topics = topics
        self.sub_thread = threading.Thread(target=self._spin, daemon=True)
        self.sub_thread.start()

    def _spin(self) -> None:
        """Spin the subscriber.

        The subscriber thread will poll the subscriber socket for incoming messages.
        When the virtual bus is shut down, the subscriber will stop polling.
        """
        self._logger.debug("Starting subscriber")
        try:
            while True:
                try:
                    socks = dict(self.sub_poller.poll())
                    if self.sub_socket in socks:
                        self.consume(self.sub_socket.recv_multipart())
                except zmq.error.ContextTerminated:
                    self._logger.debug("Context terminated")
                    break
        finally:
            self._logger.debug("Shutting down subscriber")
            self.sub_poller.unregister(self.sub_socket)
            self.sub_socket.close()

    @abstractmethod
    def consume(self, content: list[bytes]) -> None:
        """Consume the incoming message.

        The user must implement this method to process incoming messages.

        Parameters
        ----------
        content : ``list[bytes]``
            Incoming message.
        """
        ...


class AsyncSubscriber(Consumer):
    """Mixin class for asynchronous subscribing.

    .. warning::

        Currently not implemented!

    Just like its synchronous counterpart,
    the asynchronous subscriber will poll
    the virtual bus for incoming messages
    to registered topics.

    Instead of a background thread,
    a shared background event loop
    is used, where multiple async.
    subscribers can coexist.

    Parameters
    ----------
    virtual_bus : :class:`~sunflare.virtual.VirtualBus`
        Virtual bus.
    topics : ``str | Iterable[str]``
        Subscriber topics.

    Attributes
    ----------
    sub_socket : ``zmq.asyncio.Socket``
        Subscriber socket.
    sub_poller : ``zmq.asyncio.Poller``
        Poller for the subscriber socket.
    sub_future : ``concurrent.futures.Future[None]``
        Future object of the subscriber task.
    sub_topics : ``str | Iterable[str]``
        Subscriber topics.
    """

    sub_socket: zmq.asyncio.Socket
    sub_poller: zmq.asyncio.Poller
    sub_future: Future[None]
    sub_topics: Optional[Union[str, Iterable[str]]]

    def __init__(
        self, virtual_bus: VirtualBus, topics: Optional[Union[str, Iterable[str]]]
    ) -> None:
        raise NotImplementedError("Async subscriber not implemented yet.")

    async def _spin(self) -> None:
        """Spin the subscriber.

        The subscriber thread will poll the subscriber socket for incoming messages.
        When the virtual bus is shut down, the subscriber will stop polling.
        """
        try:
            while True:
                try:
                    socks = dict(await self.sub_poller.poll())
                    if self.sub_socket in socks:
                        await maybe_await(
                            self.consume(await self.sub_socket.recv_multipart())
                        )
                except zmq.error.ContextTerminated:
                    break
        finally:
            self.sub_poller.unregister(self.sub_socket)
            self.sub_socket.close()

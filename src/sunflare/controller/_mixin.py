import threading
from abc import abstractmethod
from typing import Iterable, Optional, Union

import zmq

from sunflare.virtual import VirtualBus


class SyncPublisher:
    """Synchronous publisher protocol class.

    A protocol class for controllers that need to publish data synchronously.

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


class SyncSubscriber:
    """Synchronous subscriber mixin class.

    The synchronous subscriber deploys a background thread
    which will poll the virtual bus for incoming messages.
    When a new message is received and the subscriber
    is registered to the topic the message carries,
    the message is put in a queue to be consumed
    by the controller (possibly in another thread).

    When the virtual bus is shut down, the
    subscriber will:

    - put a ``None`` in the queue (which signals the consumer to finish);
    - unregister the subscriber from the poller;
    - close the subscriber socket.

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
    msg_queue : ``deque[Iterable[bytes]]``
        Incoming message queue.
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
        self.sub_socket, self.sub_poller = virtual_bus.connect_subscriber(topics)
        self.sub_topics = topics
        self.sub_thread = threading.Thread(target=self._spin, daemon=True)
        self.sub_thread.start()

    def _spin(self) -> None:
        """Spin the subscriber.

        The subscriber thread will poll the subscriber socket for incoming messages.
        When the virtual bus is shut down, the subscriber will stop polling.
        """
        try:
            while True:
                try:
                    socks = dict(self.sub_poller.poll())
                    if self.sub_socket in socks:
                        self.consume(self.sub_socket.recv_multipart())
                except zmq.error.ContextTerminated:
                    break
        finally:
            self.sub_poller.unregister(self.sub_socket)
            self.sub_socket.close()

    @abstractmethod
    def consume(self, content: list[bytes]) -> None:
        """Consume the incoming message.

        Provided by the user to perform operations
        on incoming messages.

        Parameters
        ----------
        content : ``Iterable[bytes]``
            Incoming message content.
        """
        ...


class SyncPubSub(SyncPublisher, SyncSubscriber):
    """Mixin class for synchronous simultaneous publishing and subscribing.

    See :class:`~sunflare.virtual.SyncPublisher` and :class:`~sunflare.virtual.SyncSubscriber` for reference.
    """

    def __init__(
        self, virtual_bus: VirtualBus, topics: Optional[Union[str, list[str]]] = None
    ) -> None:
        SyncPublisher.__init__(self, virtual_bus)
        SyncSubscriber.__init__(self, virtual_bus, topics)

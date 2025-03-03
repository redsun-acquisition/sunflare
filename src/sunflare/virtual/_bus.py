from __future__ import annotations

import logging
import threading
from abc import abstractmethod
from types import MappingProxyType
from typing import (
    Callable,
    Final,
    Iterable,
    Optional,
    TypeVar,
    Union,
    cast,
    overload,
)
from weakref import WeakSet

import msgspec
import numpy as np
import zmq
import zmq.asyncio
import zmq.devices
from psygnal import Signal, SignalInstance

from sunflare.log import Loggable

__all__ = [
    "Signal",
    "VirtualBus",
    "slot",
    "encode",
    "decode",
    "Publisher",
    "Subscriber",
]


F = TypeVar("F", bound=Callable[..., object])
T = TypeVar("T")

_INPROC_XPUB = "inproc://virtual_xpub"
_INPROC_XSUB = "inproc://virtual_xsub"


def _msgpack_enc_hook(obj: object) -> object:
    if isinstance(obj, np.ndarray):
        # TODO: this can be done more efficiently
        return (obj.tobytes(), str(obj.dtype), obj.shape)
    raise NotImplementedError(
        f"Object of type {type(obj)} is not a supported type for encoding"
    )


def _msgpack_dec_hook(expected_type: type, obj: object) -> object:
    if expected_type is np.ndarray:
        # TODO: this can be done more efficiently
        data, dtype, shape = cast(tuple[bytes, str, tuple[int, ...]], obj)
        return np.frombuffer(data, dtype=dtype).reshape(shape)
    return obj


_encoder = msgspec.msgpack.Encoder(enc_hook=_msgpack_enc_hook)
_decoder = msgspec.msgpack.Decoder(dec_hook=_msgpack_dec_hook)


def encode(obj: T) -> bytes:
    """Encode an object in msgpack format.

    Parameters
    ----------
    obj : ``T``
        The object to encode.

    Returns
    -------
    ``bytes``
        The encoded object.
    """
    return _encoder.encode(obj)


def decode(data: bytes) -> object:
    """Decode a serialized message to an object.

    .. note::

        For correct type checking,
        the decoded object should
        be casted by the caller of
        this function using
        ``typing.cast``.

    Parameters
    ----------
    data : ``bytes``
        The encoded data.

    Returns
    -------
    ``object``
        The decoded object.
    """
    return _decoder.decode(data)


@overload
def slot(func: F) -> F: ...


@overload
def slot(*, private: bool) -> Callable[[F], F]: ...


def slot(
    func: Optional[F] = None, *, private: bool = False
) -> Union[F, Callable[[F], F]]:
    """Decorate a function (or class method) as a slot.

    Parameters
    ----------
    func : ``F``, optional
        The function to decorate. If not provided, the decorator must be applied with arguments.
    private : ``bool``, optional
        Mark the slot as private. Default is ``False``.

    Returns
    -------
    ``F | Callable[[F], F]``
        Either the decorated function or a callable decorator.
    """

    def decorator(actual_func: F) -> F:
        setattr(actual_func, "__isslot__", True)
        setattr(actual_func, "__isprivate__", private)
        return actual_func

    if func is None:
        return decorator  # Return the decorator function
    else:
        return decorator(func)  # Directly apply the decorator


class ContextFactory:
    ctx: Optional[zmq.Context[zmq.Socket[bytes]]] = None

    def __call__(self) -> zmq.Context[zmq.Socket[bytes]]:
        if self.ctx is None:
            self.ctx = zmq.Context()
        return self.ctx


class VirtualBus(Loggable):
    """``VirtualBus``: signal router for data exchange.

    Supports logging via :class:`~sunflare.log.Loggable`.

    The ``VirtualBus`` is a mechanism to exchange
    data between different parts of the system. Communication
    can happen between plugins on the same layer as
    well as between different layers of the system.

    It can be used to emit notifications and carry information
    to other plugins.

    The bus offers two communication mechanisms:

    - `psygnal.Signal` for control signaling;
    - ZMQ sockets for data exchange.
    """

    FWD_MAP: Final[dict[str, dict[int, str]]] = {
        "inproc": {zmq.SUB: _INPROC_XPUB, zmq.PUB: _INPROC_XSUB},
    }

    def __init__(self) -> None:
        self._map: dict[int, str]
        self._map = self.FWD_MAP["inproc"]
        self._cache: dict[str, dict[str, SignalInstance]] = {}
        self._pub_sockets: WeakSet[zmq.Socket[bytes]] = WeakSet()
        self._factory = ContextFactory()
        self._context = self._factory()
        self._forwarder = zmq.devices.ThreadDevice(zmq.FORWARDER, zmq.XSUB, zmq.XPUB)
        self._forwarder.context_factory = self._factory
        self._forwarder.setsockopt_in(zmq.LINGER, 0)
        self._forwarder.setsockopt_out(zmq.LINGER, 0)

        # the two binding points are intentionally
        # swapped here; the sockets will receive
        # the correct connection string
        self._forwarder.bind_in(self._map[zmq.PUB])
        self._forwarder.bind_out(self._map[zmq.SUB])
        self._forwarder.start()

    def shutdown(self) -> None:
        """Shutdown the virtual bus.

        Closes the ZMQ context and terminates the streamer queue.
        """
        self.debug("Closing publisher sockets.")
        for socket in self._pub_sockets:
            socket.close()
        self._context.term()
        self._forwarder.join()

    def register_signals(
        self, owner: object, only: Optional[Iterable[str]] = None
    ) -> None:
        """
        Register the signals of an object in the virtual bus.

        Parameters
        ----------
        owner : ``object``
            The instance whose class's signals are to be cached.
        only : ``Iterable[str]``, optional
            A list of signal names to cache. If not provided, all
            signals in the class will be cached automatically by inspecting
            the class attributes.

        Notes
        -----
        This method inspects the attributes of the owner's class to find
        ``psygnal.Signal`` descriptors. For each such descriptor, it retrieves
        the ``SignalInstance`` from the owner using the descriptor protocol and
        stores it in the registry.
        """
        owner_class = type(owner)  # Get the class of the object
        class_name = owner_class.__name__  # Name of the class

        if only is None:
            # Automatically detect all attributes of the class that are psygnal.Signal descriptors
            only = [
                name
                for name in dir(owner_class)
                if isinstance(getattr(owner_class, name, None), Signal)
            ]

        # Initialize the registry for this class if not already present
        if class_name not in self._cache:
            self._cache[class_name] = {}

        # Iterate over the specified signal names and cache their instances
        for name in only:
            signal_descriptor = getattr(owner_class, name, None)
            if isinstance(signal_descriptor, Signal):
                # Retrieve the SignalInstance using the descriptor protocol
                signal_instance = getattr(owner, name)
                self._cache[class_name][name] = signal_instance

    def __getitem__(self, class_name: str) -> MappingProxyType[str, SignalInstance]:
        """
        Access the registry for a specific class.

        Parameters
        ----------
        class_name: str
            The name of the class whose signals are to be accessed.

        Returns
        -------
        MappingProxyType[str, SignalInstance]
            A read-only dictionary mapping signal names to their `SignalInstance` objects.
            If the class is not found in the registry, an empty dictionary is returned.
        """
        try:
            return MappingProxyType(self._cache[class_name])
        except KeyError:
            self.error(f"Class {class_name} not found in the registry.")
            return MappingProxyType({})

    def __contains__(self, class_name: str) -> bool:
        """
        Check if a class is in the registry.

        Parameters
        ----------
        class_name : str
            The name of the class to check.

        Returns
        -------
        bool
            True if the class is in the registry, False otherwise.
        """
        return class_name in self._cache

    @overload
    def connect_subscriber(
        self, topic: str
    ) -> tuple[zmq.Socket[bytes], zmq.Poller]: ...

    @overload
    def connect_subscriber(
        self, topic: Iterable[str]
    ) -> tuple[zmq.Socket[bytes], zmq.Poller]: ...

    def connect_subscriber(
        self,
        topic: Union[str, Iterable[str]] = "",
    ) -> tuple[zmq.Socket[bytes], zmq.Poller]:
        """
        Connect a subscriber to the virtual bus.

        A subscriber can be attached to different
        topics (or receive all messages if no topic)
        via the ``topic`` parameter.

        A subtopic of a given topic
        can be specified as "<main_topic>/<sub_topic>/...".

        Usage:

        .. code-block:: python

            # registering to all topics
            socket, poller = bus.connect_subscriber()
            # or more explicitly
            socket, poller = bus.connect_subscriber("")

            # registering to a specific topic
            socket, poller = bus.connect_subscriber("topic")

            # you can also use a list, where the first
            # entry is the main topic and the rest are subtopics

            # "topic/subtopic"
            socket, poller = bus.connect_subscriber("topic/subtopic")
            socket, poller = bus.connect_subscriber(["topic", "subtopic"])

            # "topic/subtopic/subsubtopic"
            socket, poller = bus.connect_subscriber("topic/subtopic/subsubtopic")
            socket, poller = bus.connect_subscriber(
                ["topic", "subtopic", "subsubtopic"]
            )


        Parameters
        ----------
        topic : ``str | Iterable[str]``, optional
            The topic(s) to subscribe to.
            If not provided, socket
            is subscribed to all topics.
        is_async : ``bool``, optional
            Whether to return an asyncio-compatible socket.
            Default is ``False``.

        Returns
        -------
        ``tuple[zmq.SyncSocket, zmq.Poller]``
            A tuple containing the subscriber socket and its poller.

        """
        socket = self._context.socket(zmq.SUB)
        socket.setsockopt(zmq.LINGER, 0)
        poller = zmq.Poller()
        socket.connect(self._map[zmq.SUB])
        poller.register(socket, zmq.POLLIN)
        if isinstance(topic, str):
            socket.subscribe(topic)
        else:
            final_topic = "/".join(topic)
            socket.subscribe(final_topic)
        return socket, poller

    def connect_publisher(self) -> zmq.Socket[bytes]:
        """Connect a publisher to the virtual bus.

        Parameters
        ----------
        asyncio : ``bool``, keyword-only, optional
            Whether to return an asyncio-compatible socket.
            Default is ``False``.

        Returns
        -------
        ``zmq.SyncSocket | zmq.asyncio.Socket``
            The publisher socket.
        """
        socket: zmq.Socket[bytes] = self._context.socket(zmq.PUB)
        socket.connect(self._map[zmq.PUB])
        socket.setsockopt(zmq.LINGER, 0)
        self._pub_sockets.add(socket)
        return socket


class Publisher:
    """Publisher mixin class.

    Creates a publisher socket for the virtual bus,
    which can be used to send messages to subscribers
    over the virtual bus.

    Provides a built-in reference to the application logger.

    Parameters
    ----------
    virtual_bus : :class:`~sunflare.virtual.VirtualBus`
        Virtual bus.

    Attributes
    ----------
    pub_socket : ``zmq.Socket[bytes]``
        Publisher socket.
    logger : ``logging.Logger``
        Reference to application logger.
    """

    pub_socket: zmq.Socket[bytes]

    def __init__(
        self,
        virtual_bus: VirtualBus,
    ) -> None:
        self.logger = logging.getLogger("redsun")
        self.pub_socket = virtual_bus.connect_publisher()


class Subscriber:
    """Subscriber mixin class.

    The synchronous subscriber deploys a background thread
    which will poll the virtual bus for incoming messages.

    Provides a built-in reference to the application logger.

    Parameters
    ----------
    virtual_bus : :class:`~sunflare.virtual.VirtualBus`
        Virtual bus.
    topics : ``str | Iterable[str]``, optional
        Subscriber topics.
        Default is ``""`` (receive all messages).

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
    logger: ``logging.Logger``
        Reference to application logger.
    """

    sub_socket: zmq.Socket[bytes]
    sub_poller: zmq.Poller
    sub_thread: threading.Thread
    sub_topics: Optional[Union[str, Iterable[str]]]

    def __init__(
        self,
        virtual_bus: VirtualBus,
        topics: Union[str, Iterable[str]] = "",
    ) -> None:
        self.logger = logging.getLogger("redsun")
        self.sub_socket, self.sub_poller = virtual_bus.connect_subscriber(topics)
        self.logger.debug(f"Registered to topics {topics}")
        self.sub_topics = topics
        self.sub_thread = threading.Thread(target=self._spin, daemon=True)
        self.sub_thread.start()

    def _spin(self) -> None:
        """Spin the subscriber.

        The subscriber thread will poll the subscriber socket for incoming messages.
        When the virtual bus is shut down, the subscriber will stop polling.
        """
        self.logger.debug("Starting subscriber")
        try:
            while True:
                try:
                    socks = dict(self.sub_poller.poll())
                    if self.sub_socket in socks:
                        self.consume(self.sub_socket.recv_multipart())
                except zmq.error.ContextTerminated:
                    break
        finally:
            self.logger.debug("Context terminated")
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

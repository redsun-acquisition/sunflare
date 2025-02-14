r"""
Sunflare virtual module.

This module implements the communication mechanism between the controller layer and the view layer.

It achieves this by using the `psygnal <https://psygnal.readthedocs.io/en/stable/>`_ library.

The module exposes the following:

- the ``psygnal.Signal`` class;
- the ``VirtualBus`` class;
- the ``slot`` decorator.

``psygnal.Signal`` is the main communication mechanism between controllers and the view layer.

It provides a syntax similar to the Qt signal/slot mechanism, i.e.

.. code-block:: python

    class MyController:
        sigMySignal = Signal()


    def a_slot():
        print("My signal was emitted!")


    ctrl = MyController()
    ctrl.sigMySignal.connect(my_slot)

- The ``VirtualBus`` class is a signal router for data exchange between the backend and frontend. Plugins can expose signals to other plugins or different Redsun modules, as well as connect to built-in signals or signals provided from other system components.

- The ``slot`` decorator is used to mark a function as a slot. In practice, it provides no benefit at runtime; it's used to facilitate code readability.

.. code-block:: python

    # slot will mark the function as a slot
    @slot
    def my_slot():
        print("My slot was called!")
"""

from __future__ import annotations

from types import MappingProxyType
from typing import (
    TYPE_CHECKING,
    Callable,
    ClassVar,
    Iterable,
    Optional,
    TypeVar,
    Union,
    cast,
    overload,
)

import msgspec
import numpy as np
import zmq
import zmq.devices
from psygnal import Signal, SignalInstance

from sunflare.log import Loggable

if TYPE_CHECKING:
    from sunflare.engine import DocumentType

__all__ = ["Signal", "VirtualBus", "slot", "encode", "decode"]


F = TypeVar("F", bound=Callable[..., object])

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


def encode(obj: DocumentType) -> bytes:
    """Encode a document in msgpack format.

    Parameters
    ----------
    obj : ``DocumentType``
        The document to encode.

    Returns
    -------
    ``bytes``
        The encoded object.
    """
    return _encoder.encode(obj)


def decode(data: bytes) -> DocumentType:
    """Decode a serialized message to a document.

    Parameters
    ----------
    data : ``bytes``
        The encoded data.

    Returns
    -------
    ``DocumentType``
        The decoded document.
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


class VirtualBus(Loggable):
    """``VirtualBus``: signal router for data exchange.

    Supports logging via :class:`~sunflare.log.Loggable`.

    The ``VirtualBus`` is a mechanism to exchange
    data between different parts of the system. Communication
    can happen between plugins on the same layer as
    well as between different layers of the system.

    It can be used to emit notifications, as well as carry information
    to other plugins and/or different Redsun modules.

    ``VirtualBus``' signals are implemented using the ``psygnal`` library;
    they can be dynamically registered as class attributes,
    and accessed as a read-only dictionary.
    """

    _INPROC_MAP: ClassVar[dict[int, str]] = {
        # a subscriber publishes to the XPUB socket;
        # a publisher subscribes to the XSUB socket
        zmq.SUB: _INPROC_XPUB,
        zmq.PUB: _INPROC_XSUB,
    }

    _PUB_SOCKETS: ClassVar[set[zmq.SyncSocket]] = set()

    def __init__(self) -> None:
        self._cache: dict[str, dict[str, SignalInstance]] = {}

        self._context = zmq.Context.instance()
        self._forwarder = zmq.devices.ThreadDevice(zmq.FORWARDER, zmq.XSUB, zmq.XPUB)
        self._forwarder.daemon = True
        self._forwarder.setsockopt_in(zmq.LINGER, 0)
        self._forwarder.setsockopt_out(zmq.LINGER, 0)
        self._forwarder.bind_in(_INPROC_XSUB)
        self._forwarder.bind_out(_INPROC_XPUB)
        self._forwarder.start()

    def shutdown(self) -> None:
        """Shutdown the virtual bus.

        Closes the ZMQ context and terminates the streamer queue.
        """
        self.debug("Closing publisher sockets.")
        for socket in self._PUB_SOCKETS:
            socket.close()
        try:
            self._context.term()
        except zmq.error.ZMQError:
            self.debug("ZMQ context already terminated.")
        finally:
            if not self._forwarder.done:
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
    def connect(self, socket_type: int) -> zmq.SyncSocket: ...

    @overload
    def connect(self, socket_type: int, *, topic: None) -> zmq.SyncSocket: ...

    @overload
    def connect(
        self, socket_type: int, *, topic: str
    ) -> tuple[zmq.SyncSocket, zmq.Poller]: ...

    @overload
    def connect(
        self, socket_type: int, *, topic: Iterable[str]
    ) -> tuple[zmq.SyncSocket, zmq.Poller]: ...

    def connect(
        self,
        socket_type: int,
        *,
        topic: Optional[Union[str, Iterable[str]]] = None,
    ) -> Optional[Union[zmq.SyncSocket, tuple[zmq.SyncSocket, zmq.Poller]]]:
        """Return a new socket connected to the virtual bus context.

        Class instances may use this method to
        create a new socket which will be automatically
        connected to the virtual bus.

        Parameters
        ----------
        socket_type : ``int | zmq.SocketType``
            The type of the socket to create.
            Accepted values are:

            - ``1`` / ``zmq.PUB``: Publisher socket.
            - ``2`` / ``zmq.SUB``: Subscriber socket.
        topic: ``str | Iterable[str] ``, optional (subscribers only)
            Topic(s) to subscribe to.
            If not provided, the subscriber is in charge
            of specifying the topic.

        Returns
        -------
        socket : ``zmq.SyncSocket | None``
            A new socket for the virtual bus.
            If the socket type is invalid,
            logs the error returns ``None``.
        socket, poller : ``tuple[zmq.SyncSocket, zmq.Poller] | None``
            A new socket and a poller for the virtual bus
            (only for ``zmq.SUB`` sockets).
            If the socket type is invalid,
            returns ``None``.

        """
        if socket_type not in [zmq.PUB, zmq.SUB]:
            self.error(
                f"Invalid socket type: {zmq.SocketType(socket_type)}. Aborting connection."
            )
            return None
        socket: zmq.SyncSocket = self._context.socket(socket_type)
        socket.connect(self._INPROC_MAP[socket_type])

        if socket_type == zmq.SUB:
            poller = zmq.Poller()
            poller.register(socket, zmq.POLLIN)
            if isinstance(topic, str):
                socket.subscribe(topic)
            elif isinstance(topic, Iterable):
                for t in topic:
                    socket.subscribe(t)
            return socket, poller
        else:
            self._PUB_SOCKETS.add(socket)
            return socket

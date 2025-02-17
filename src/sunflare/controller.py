"""Redsun uses controllers to manage the interaction between the user interface and the hardware.

They have access to the ``VirtualBus`` to enable interaction with other controllers and/or
widgets by exchanging data via either the built-in signals or custom signals that can be defined by the user.

They can keep a reference of hardware devices for exclusive control by selecting the appropriate model from the
``models`` map.

Functionally wise, they can:

- publish plans to provide information on their capabilities;
- allocate a reference to the ``RunEngine`` to execute said plans;
- simply process the data acquired by the ``RunEngine``, accessed from the `VirtualBus` signals.

Each controller is associated with a ``ControllerInfo`` object,
which contains a series of user-defined properties that
describe the controller and provides further customization options.
"""

import sys
import threading
from abc import abstractmethod
from collections import deque

if sys.version_info >= (3, 11):
    from typing import Protocol
else:
    from typing_extensions import Protocol

from typing import Iterable, Mapping, Optional, Union, runtime_checkable

import zmq

from sunflare.config import ControllerInfo
from sunflare.model import ModelProtocol
from sunflare.virtual import VirtualBus


@runtime_checkable
class ControllerProtocol(Protocol):
    """Controller protocol class.

    Parameters
    ----------
    ctrl_info : :class:`~sunflare.config.ControllerInfo`
        Controller information.
    models : Mapping[str, :class:`~sunflare.model.ModelProtocol`]
        Models currently loaded in the active Redsun session.
    virtual_bus : :class:`~sunflare.virtual.VirtualBus`
        Virtual bus.
    """

    info: ControllerInfo
    virtual_bus: VirtualBus

    @abstractmethod
    def __init__(
        self,
        info: ControllerInfo,
        models: Mapping[str, ModelProtocol],
        virtual_bus: VirtualBus,
    ) -> None: ...

    @abstractmethod
    def registration_phase(self) -> None:
        r"""Register the controller signals listed in this method to expose them to the virtual buses.

        At application start-up, controllers can't know what signals are available from other controllers. \
        This method is called after all controllers are initialized to allow them to register their signals. \
        Controllers may be able to register further signals even after this phase (but not before the `connection_phase` ended). \
        
        Only signals defined in your controller can be registered.
        
        An implementation example:

        .. code-block:: python

            def registration_phase(self) -> None:
                # you can register all signals...
                self.virtual_bus.register_signals(self)
                
                # ... or only a selection of them
                self.virtual_bus.register_signals(self, only=["signal"])
        """
        ...

    @abstractmethod
    def connection_phase(self) -> None:
        """Connect to other controllers or widgets.

        At application start-up, controllers can't know what signals are available from other parts of Redsun.
        This method is invoked after the controller's construction and after `registration_phase` as well, allowing to
        connect to all available registered signals in both virtual buses.
        Controllers may be able to connect to other signals even after this phase (provided those signals
        were registered before).

        An implementation example:

        .. code-block:: python

            def connection_phase(self) -> None:
                # you can connect signals from another controller to your local slots...
                self.virtual_bus["OtherController"]["signal"].connect(self._my_slot)

                # ... or to other signals ...
                self.virtual_bus["OtherController"]["signal"].connect(self.sigMySignal)

                # ... or connect to widgets
                self.virtual_bus["OtherWidget"]["sigWidget"].connect(self._my_slot)
        """
        ...


class HasShutdown(Protocol):
    """Shutdown protocol class.

    Provides the ``shutdown`` method.
    """

    @abstractmethod
    def shutdown(self) -> None:
        """Shutdown the controller. Performs cleanup operations.

        If the controller holds any kind of resources,
        this method should invoke any equivalent shutdown method for each resource.
        """
        ...


class SyncPublisher:
    """SyncPublisher protocol class.

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
        """Pre-initialization method.

        Initializes the publisher socket.
        """
        self.pub_socket = virtual_bus.connect_publisher()


class SyncSubscriber:
    """SyncSubscriber protocol class.

    A protocol class for controllers that need to subscribe to data synchronously.

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
    msg_queue: deque[Iterable[bytes]]

    def __init__(
        self,
        virtual_bus: VirtualBus,
        topics: Optional[Union[str, Iterable[str]]] = None,
    ) -> None:
        self.sub_socket, self.sub_poller = virtual_bus.connect_subscriber(topics)
        self.sub_topics = topics
        self.msg_queue = deque()
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
                        self.msg_queue.append(self.sub_socket.recv_multipart())
                except zmq.error.ContextTerminated:
                    break
        finally:
            self.sub_poller.unregister(self.sub_socket)
            self.sub_socket.close()


class SyncPubSub(SyncPublisher, SyncSubscriber):
    """Mixin class for synchronous simultaneous publishing and subscribing.

    See :class:`~sunflare.virtual.SyncPublisher` and :class:`~sunflare.virtual.SyncSubscriber` for reference.
    """

    def __init__(self, virtual_bus: VirtualBus) -> None:
        SyncSubscriber.__init__(self, virtual_bus)
        SyncPublisher.__init__(self, virtual_bus)

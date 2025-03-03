from abc import abstractmethod

from typing_extensions import Protocol, runtime_checkable


class HasShutdown(Protocol):  # pragma: no cover
    """Protocol marking your class as capable of shutting down.

    .. tip::

        This protocol is optional and only available for
        ``Controllers``. ``Widgets`` and ``Models`` will not
        be affected by this protocol.

    """

    @abstractmethod
    def shutdown(self) -> None:
        """Shutdown an object. Performs cleanup operations.

        If the object holds any kind of resources,
        this method should invoke any equivalent shutdown method for each resource.
        """
        ...


@runtime_checkable
class HasRegistration(Protocol):  # pragma: no cover
    """Protocol marking your class as capable of emitting signals.

    .. tip::

        This protocol is optional and only available for
        ``Controllers`` and ``Widgets``. ``Models``
        will not be affected by this protocol.

    """

    @abstractmethod
    def registration_phase(self) -> None:
        r"""Register the signals listed in this method to expose them to the virtual bus.

        At application start-up, controllers can't know what signals are available from other controllers. \
        This method is called after all controllers are initialized to allow them to register their signals. \
        Controllers may be able to register further signals even after this phase (but not before the `connection_phase` ended). \
        
        Only signals defined in your object can be registered.
        
        An implementation example:

        .. code-block:: python

            def registration_phase(self) -> None:
                # you can register all signals...
                self.virtual_bus.register_signals(self)
                
                # ... or only a selection of them
                self.virtual_bus.register_signals(self, only=["signal"])
        """
        ...


@runtime_checkable
class HasConnection(Protocol):  # pragma: no cover
    """Protocol marking your class as requesting connection to other signals.

    .. tip::

        This protocol is optional and only usable with
        ``Controllers`` and ``Widgets``. ``Models``
        will not be affected by this protocol.

    """

    @abstractmethod
    def connection_phase(self) -> None:
        """Connect to other objects via the virtual bus.

        At application start-up, objects within Redsun can't know what signals are available from other parts of the session.
        This method is invoked after the object's construction and after `registration_phase` as well, allowing to
        connect to all available registered signals in the virtual bus.
        Objects may be able to connect to other signals even after this phase (provided those signals
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

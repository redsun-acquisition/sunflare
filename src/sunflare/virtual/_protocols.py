from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from dependency_injector.containers import DynamicContainer


@runtime_checkable
class HasShutdown(Protocol):  # pragma: no cover
    """Protocol marking your class as capable of shutting down.

    !!! tip
        This protocol is optional and only available for
        ``Presenters``. ``Widgets`` and ``Devices`` will not
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
class IsProvider(Protocol):  # pragma: no cover
    """Protocol marking a class as a provider of dependencies.

    !!! tip
        This protocol is optional and only available for
        ``Presenters``. ``Widgets`` and ``Devices`` will not
        be affected by this protocol.
    """

    @abstractmethod
    def register_providers(self, container: DynamicContainer) -> None:
        """Register providers in the dependency injection container.

        This method is invoked after the presenter is built,
        allowing to register providers in the DI container before any view is built.

        !!! tip
            This protocol is optional and only available for ``Presenters``.
            ``Views`` and ``Devices`` will not be affected by this protocol.
        """
        ...


@runtime_checkable
class IsInjectable(Protocol):  # pragma: no cover
    """Protocol marking a class as injectable with dependencies from the container.

    !!! tip
        This protocol is optional and only available for ``Views``.
        ``Presenters`` and ``Devices`` will not be affected by this protocol.
    """

    @abstractmethod
    def inject_dependencies(self, container: DynamicContainer) -> None:
        """Inject dependencies from the container.

        This method is invoked after the view is built object is built,
        allowing to inject dependencies from the container
        in order to customize the view after its construction.
        """
        ...


@runtime_checkable
class VirtualAware(Protocol):  # pragma: no cover
    """Protocol marking a class as aware of the virtual bus and able to connect to it.

    !!! tip
        This protocol is optional and only usable with ``Presenters`` and ``Views``.
        ``Devices`` will not be affected by this protocol.

    !!! note
        In the future, this may be extended to support ``Devices`` as well.
    """

    @abstractmethod
    def connect_to_virtual(self) -> None:
        """Connect to other objects via the virtual bus.

        At application start-up, objects within Redsun can't know what signals are available from other parts of the session.
        This method is invoked after the object's construction and after `registration_phase` as well, allowing to
        connect to all available registered signals in the virtual bus.
        Objects may be able to connect to other signals even after this phase (provided those signals
        were registered before).

        An implementation example:

        ```python
        def connect_to_virtual(self) -> None:
            # you can connect signals from another controller to your local slots...
            self.virtual_bus["OtherController"]["signal"].connect(self._my_slot)

            # ... or to other signals ...
            self.virtual_bus["OtherController"]["signal"].connect(self.sigMySignal)

            # ... or connect to a view component
            self.virtual_bus["OtherWidget"]["sigWidget"].connect(self._my_slot)
        ```
        """
        ...

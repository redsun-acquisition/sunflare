"""
RedSun controller toolkit.

This toolkit section provides RedSun developers with the necessary base classes to implement their own controllers.
"""

from abc import abstractmethod
from typing import TYPE_CHECKING, Protocol, TypeVar, Generic

from sunflare.config import ControllerInfo

if TYPE_CHECKING:
    from typing import Iterable

    from sunflare.config import ControllerInfo, AcquisitionEngineTypes, ControllerTypes
    from sunflare.virtualbus import VirtualBus, Signal
    from sunflare.types import Workflow

# device registry type
R = TypeVar("R")


class ControllerProtocol(Generic[R], Protocol):
    """Base controller protocol."""

    _registry: R
    _virtual_bus: "VirtualBus"
    _module_bus: "VirtualBus"
    _ctrl_info: "ControllerInfo"

    def shutdown(self) -> None:
        """Shutdown the controller. Performs cleanup operations.

        If the controller handles any kind of resources (i.e. devices, connections, etc.),
        this method should invoke any equivalent shutdown method for each resource.
        """
        ...

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
                self._module_bus.register_signals(self)
                
                # ... or only a selection of them
                self._module_bus.register_signals(self, only=["sigMySignal", "sigMyOtherSignal"])
                
                # you can also register signals to the module bus
                self._module_bus.register_signals(self, only=["sigMySignal", "sigMyOtherSignal"])
        """
        ...

    @abstractmethod
    def connection_phase(self) -> None:
        """Connect to other controllers' signals.

        At application start-up, controllers can't know what signals are available from other controllers.
        This method is invoked after the controller's construction and after `registration_phase` as well, allowing to
        connect to all available registered signals in both virtual buses.
        Controllers may be able to connect to other controllers' signals even after this phase,
        or to signals from the view layer (provided they have been registered as well).

        An implementation example:

        .. code-block:: python

            def connection_phase(self) -> None:
                # you can connect signals from another controller to your local slots...
                self._virtual_bus["OtherController"]["sigOtherControllerSignal"].connect(self._my_slot)

                # ... or to other signals ...
                self._virtual_bus["OtherController"]["sigOtherControllerSignal"].connect(self.sigMySignal)

                # ... or connect to widgets
                self._virtual_bus["OtherWidget"]["sigOtherWidgetSignal"].connect(self._my_slot)

                # you can also connect to the module bus
                self._module_bus["OtherController"]["sigOtherControllerSignal"].connect(self._my_slot)
                self._module_bus["OtherWidget"]["sigOtherWidgetSignal"].connect(self._my_slot)
        """
        ...

    @property
    @abstractmethod
    def category(self) -> "set[ControllerTypes]":
        """Controller category."""
        ...

    @property
    @abstractmethod
    def controller_name(self) -> str:
        """Controller name. Represents the class which builds the controller instance."""
        ...

    @property
    @abstractmethod
    def supported_engines(self) -> "list[AcquisitionEngineTypes]":
        """List of supported engines."""
        return self._ctrl_info.supported_engines

    @property
    @abstractmethod
    def registry(self) -> R:
        """Device registry."""
        return self._registry


class Computator(Protocol):
    """Infers that this class is a computational controller."""

    ...


class Publisher(Protocol):
    """Infers that this class is a publisher."""

    sigNewPlan: Signal

    @property
    @abstractmethod
    def workflows(self) -> "Iterable[Workflow]":
        """Iterable of available plans."""
        ...


class Monitorer(Protocol):
    """Infers that this class is a monitorer."""

    ...

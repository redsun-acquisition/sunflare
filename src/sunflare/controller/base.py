"""
RedSun controller toolkit.

This toolkit section provides RedSun developers with the necessary base classes to implement their own controllers.
"""

from abc import ABC, abstractmethod

from typing import Iterable, Protocol

from sunflare.config import ControllerInfo, ControllerTypes
from sunflare.virtualbus import VirtualBus, Signal
from sunflare.types import Workflow
from sunflare.engine import DeviceRegistry


class BaseController(ABC):
    """Abstract base class for all controllers."""

    def __init__(
        self,
        ctrl_info: ControllerInfo,
        registry: DeviceRegistry,
        virtual_bus: VirtualBus,
        module_bus: VirtualBus,
    ) -> None:
        self._registry = registry
        self._ctrl_info = ctrl_info
        self._virtual_bus = virtual_bus
        self._module_bus = module_bus

    @abstractmethod
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
        """Connect to other controllers or widgets.

        At application start-up, controllers can't know what signals are available from other parts of RedSun.
        This method is invoked after the controller's construction and after `registration_phase` as well, allowing to
        connect to all available registered signals in both virtual buses.
        Controllers may be able to connect to other signals even after this phase (provided those signals
        were registered before).

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
    def category(self) -> set[ControllerTypes]:
        """Controller category."""
        return self._ctrl_info.category

    @property
    def controller_name(self) -> str:  # noqa: D102
        """Controller class name."""
        return self._ctrl_info.controller_name

    @property
    def registry(self) -> DeviceRegistry:
        """Device registry."""
        return self._registry


class Renderer(Protocol):
    """Infers that this class is a rendering controller."""

    ...


class Publisher(Protocol):
    """Infers that this class is a publisher."""

    sigNewPlan: Signal

    @property
    @abstractmethod
    def workflows(self) -> Iterable[Workflow]:
        """Iterable of available plans."""
        ...


class Monitorer(Protocol):
    """Infers that this class is a monitorer."""

    ...

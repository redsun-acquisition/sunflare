"""RedSun uses controllers to manage the interaction between the user interface and the hardware.

Controllers can either render information (i.e. process some data and send it to the upper layer for visualization),
notify of changes in the hardware state or publish Bluesky plans for the run engine to execute.

Each controller is associated with a ``ControllerInfo`` object, which contains a series of user-defined properties that
describe the controller and provides further customization options.

Controllers can access specific hardware devices through the ``DeviceRegistry`` object, which is a singleton instance
that holds all the devices registered in the application.
"""

from abc import ABCMeta, abstractmethod
from typing import Any

from bluesky.utils import MsgGenerator

from sunflare.config import ControllerInfo, ControllerTypes
from sunflare.engine import DeviceRegistry
from sunflare.log import Loggable
from sunflare.virtualbus import Signal, VirtualBus


class BaseController(Loggable, metaclass=ABCMeta):
    """Abstract base class for all controllers.

    Parameters
    ----------
    ctrl_info : :class:`~sunflare.config.ControllerInfo`
        Controller information.
    registry : :class:`~sunflare.engine.registry.DeviceRegistry`
        Device registry.
    virtual_bus : :class:`~sunflare.virtualbus.VirtualBus`
        Virtual bus.
    module_bus : :class:`~sunflare.virtualbus.VirtualBus`
        Module bus.

    Attributes
    ----------
    sigNewPlan : Signal(object)
        - Signal that can emit plans built within the controller.
    """

    sigNewPlan: Signal = Signal(object)

    __slots__ = ("_ctrl_info", "_registry", "_virtual_bus", "_module_bus")

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
        self._plans: list[MsgGenerator[Any]] = []

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
                self._virtual_bus["OtherController"]["sigOtherControllerSignal"].connect(
                    self._my_slot
                )

                # ... or to other signals ...
                self._virtual_bus["OtherController"]["sigOtherControllerSignal"].connect(
                    self.sigMySignal
                )

                # ... or connect to widgets
                self._virtual_bus["OtherWidget"]["sigOtherWidgetSignal"].connect(
                    self._my_slot
                )

                # you can also connect to the module bus
                self._module_bus["OtherController"]["sigOtherControllerSignal"].connect(
                    self._my_slot
                )
                self._module_bus["OtherWidget"]["sigOtherWidgetSignal"].connect(
                    self._my_slot
                )
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

    @property
    def plans(self) -> list[MsgGenerator[Any]]:
        """Set of available plans."""
        return self._plans

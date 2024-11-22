"""
RedSun controller toolkit.

This toolkit section provides RedSun developers with the necessary base classes to implement their own controllers.

Two controller types are defined: `DeviceController` and `ComputationalController`.
"""

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING

from sunflare.config import ControllerInfo
from sunflare.log import Loggable

if TYPE_CHECKING:
    from typing import Any

    from sunflare.config import ControllerInfo, AcquisitionEngineTypes
    from sunflare.engine import EngineHandler
    from sunflare.virtualbus import VirtualBus


class BaseController(Loggable, metaclass=ABCMeta):
    """Base controller class. Supports logging via `Loggable`.

    Parameters
    ----------
    ctrl_info : ControllerInfo
        Controller information dataclass.
    handler : EngineHandler
        Engine API.
    virtual_bus : VirtualBus
        Intra-module virtual bus.
    module_bus : VirtualBus
        Inter-module virtual bus.
    """

    @abstractmethod
    def __init__(
        self,
        ctrl_info: "ControllerInfo",
        handler: "EngineHandler",
        virtual_bus: "VirtualBus",
        module_bus: "VirtualBus",
    ) -> None:
        self._handler = handler
        self._virtual_bus = virtual_bus
        self._module_bus = module_bus
        self._ctrlInfo = ctrl_info

    def shutdown(self) -> None:
        """Shutdown the controller. Performs cleanup operations."""
        ...

    @abstractmethod
    def registration_phase(self) -> None:
        """Register the controller signals listed in this method to expose them to the virtual buses.

        At application start-up, controllers can't know what signals are available from other controllers.
        This method is called after all controllers are initialized to allow them to register their signals.
        Controllers may be able to register further signals or connect to other controllers' signals even after this phase.

        An implementation example:

        >>> def registration_phase(self) -> None:
        >>>     # virtual bus signal
        >>>     self._virtual_bus.sigMySignal = Signal(str, int, **kwargs)
        >>>
        >>>     # module bus signal
        >>>     self._module_bus.sigOtherMySignal = Signal(int, tuple, **kwargs)
        >>>
        >>>     # using "register_signal" method
        >>>     self._virtual_bus.register_signal("sigMySecondOtherSignal", str, **kwargs)
        """
        ...

    @abstractmethod
    def connection_phase(self) -> None:
        """Connect to other controllers' signals.

        At application start-up, controllers can't know what signals are available from other controllers.
        This method is invoked after the controller's construction and after `registration_phase` as well, allowing to
        connect to all available registered signals in both virtual buses.
        Controllers may be able to connect to other controllers' signals even after this phase.

        An implementation example:

        >>> def connection_phase(self) -> None:
        >>>     # connect to virtual bus signal
        >>>     self._virtual_bus.sigExternalControllerSignal.connect(self._my_slot)
        >>>
        >>>     # connect to module bus signal
        >>>     self._module_bus.sigOtherExternalControllerSignal.connect(self._my_other_slot)
        """
        ...

    @property
    def category(self) -> str:
        """Controller category."""
        return self._ctrlInfo.category

    @property
    def controllerName(self) -> str:
        """Controller name. Represents the class which builds the controller instance."""
        return self._ctrlInfo.controllerName

    @property
    def supportedEngines(self) -> "list[AcquisitionEngineTypes]":
        """List of supported engines."""
        return self._ctrlInfo.supportedEngines

    @property
    def controllerParams(self) -> "dict[str, Any]":
        """Controller custom parameters dictionary."""
        return self._ctrlInfo.controllerParams


class DeviceController(BaseController):
    """Device controller base class.

    Parameters
    ----------
    ctrl_info : ControllerInfo
        Controller information dataclass.
    handler : EngineHandler
        Engine API.
    virtual_bus : VirtualBus
        Intra-module virtual bus.
    module_bus : VirtualBus
        Inter-module virtual bus.
    """

    @abstractmethod
    def __init__(
        self,
        ctrl_info: "ControllerInfo",
        handler: "EngineHandler",
        virtual_bus: "VirtualBus",
        module_bus: "VirtualBus",
    ) -> None:
        super().__init__(ctrl_info, handler, virtual_bus, module_bus)


class ComputationalController(BaseController):
    """Computational controller base class.

    Parameters
    ----------
    ctrl_info : ControllerInfo
        Controller information dataclass.
    handler : EngineHandler
        Engine API.
    virtual_bus : VirtualBus
        Intra-module virtual bus.
    module_bus : VirtualBus
        Inter-module virtual bus.
    """

    @abstractmethod
    def __init__(
        self,
        ctrl_info: "ControllerInfo",
        handler: "EngineHandler",
        virtual_bus: "VirtualBus",
        module_bus: "VirtualBus",
    ) -> None:
        super().__init__(ctrl_info, handler, virtual_bus, module_bus)

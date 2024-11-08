"""
RedSun controller toolkit.

This toolkit section provides RedSun developers with the necessary base classes to implement their own controllers.

Two controller types are defined: `DeviceController` and `ComputationalController`.
"""

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING

from sunflare.config import ControllerInfo
from sunflare.engine import EngineHandler
from sunflare.log import Loggable
from sunflare.utils import create_evented_dataclass
from sunflare.virtualbus import VirtualBus

if TYPE_CHECKING:
    from typing import Any

    from sunflare.config import ControllerInfo
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
        FullModelInfo = create_evented_dataclass(
            ctrl_info.controllerName + "Info", type(ctrl_info)
        )
        self._modelInfo = FullModelInfo(**ctrl_info.controllerParams)

    def shutdown(self) -> None:
        """Shutdown the controller. Performs cleanup operations."""
        ...

    @property
    def category(self) -> str:
        """Controller category."""
        return self._modelInfo.category  # type: ignore[no-any-return]

    @property
    def controllerName(self) -> str:
        """Controller name. Represents the class which builds the controller instance."""
        return self._modelInfo.controllerName  # type: ignore[no-any-return]

    @property
    def supportedEngines(self) -> "list[str]":
        """List of supported engines."""
        return self._modelInfo.supportedEngines  # type: ignore[no-any-return]

    @property
    def controllerParams(self) -> "dict[str, Any]":
        """Controller custom parameters dictionary."""
        return self._modelInfo.controllerParams  # type: ignore[no-any-return]


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
        ctrl_info: ControllerInfo,
        handler: EngineHandler,
        virtual_bus: VirtualBus,
        module_bus: VirtualBus,
    ) -> None:
        super().__init__(ctrl_info, handler, virtual_bus, module_bus)

    # TODO: add APIs...


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
        ctrl_info: ControllerInfo,
        handler: EngineHandler,
        virtual_bus: VirtualBus,
        module_bus: VirtualBus,
    ) -> None:
        super().__init__(ctrl_info, handler, virtual_bus, module_bus)

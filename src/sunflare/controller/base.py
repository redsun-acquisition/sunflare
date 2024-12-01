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

from __future__ import annotations

from abc import abstractmethod
from typing import (
    TYPE_CHECKING,
    Callable,
    Generic,
    Iterable,
    Mapping,
    NamedTuple,
    Optional,
    TypeVar,
)

from typing_extensions import Protocol, runtime_checkable

from sunflare.config import ControllerInfoProtocol

if TYPE_CHECKING:
    from sunflare.model import ModelProtocol
    from sunflare.virtual import VirtualBus


@runtime_checkable
class ControllerProtocol(Protocol):  # pragma: no cover
    """Controller protocol class.

    Provides the interface for a class
    that Redsun can recognize as a controller.

    Parameters
    ----------
    ctrl_info : :class:`~sunflare.config.ControllerInfo`
        Controller information.
    models : Mapping[str, :class:`~sunflare.model.ModelProtocol`]
        Models currently loaded in the active Redsun session.
    virtual_bus : :class:`~sunflare.virtual.VirtualBus`
        Virtual bus.
    """

    @abstractmethod
    def __init__(
        self,
        ctrl_info: ControllerInfoProtocol,
        models: Mapping[str, ModelProtocol],
        virtual_bus: VirtualBus,
    ) -> None: ...


CI = TypeVar("CI", bound=ControllerInfoProtocol)


class Connection(NamedTuple):
    """Connection tuple.

    Provides a type-hinted helper
    for describing a connection between
    a virtual bus signal and a local slot.

    Usable with :class:`~sunflare.controller.Receiver`
    and :class:`~sunflare.controller.SenderReceiver`
    to set the `connection_map` parameter.

    Parameters
    ----------
    signal : ``str``
        Signal name.
    slot : ``Callable``
        Slot to connect to.
    """

    signal: str
    slot: Callable[..., None]


class Controller(ControllerProtocol, Generic[CI]):
    """A boilerplate base class for quick development.

    Users may subclass from this controller and provide their custom
    :class:`~sunflare.config.ControllerInfo` implementation.

    Example usage:

    .. code-block:: python

        from sunflare.controller import Controller
        from sunflare.config import ControllerInfo
        from attrs import define


        @define
        class MyControllerInfo(ControllerInfo):
            str_param: str
            bool_param: bool
            # any other parameters...


        class MyController(Controller[MyControllerInfo]):
            def __init__(
                self,
                ctrl_info: MyControllerInfo,
                models: Mapping[str, ModelProtocol],
                virtual_bus: VirtualBus,
            ) -> None:
                super().__init__(ctrl_info, models, virtual_bus)
                # any other initialization code...

    Parameters
    ----------
    ctrl_info : ``CI``
        Instance of :class:`~sunflare.config.ControllerInfo` subclass.
    models : ``Mapping[str, ModelProtocol]``
        Reference to the models used in the controller.
    virtual_bus : :class:`~sunflare.virtual.VirtualBus`
        Reference to the virtual bus.
    """

    def __init__(
        self,
        ctrl_info: CI,
        models: Mapping[str, ModelProtocol],
        virtual_bus: VirtualBus,
    ) -> None:
        self.ctrl_info = ctrl_info
        self.models = models
        self.virtual_bus = virtual_bus


class Sender(Controller[CI]):
    """A controller capable of emitting signals to the virtual bus.

    Provides an additional `signals` parameter to the constructor
    to optionally register a group of the controller's defined
    signals.

    Users may subclass from this controller and provide their custom
    :class:`~sunflare.config.ControllerInfo` implementation.

    Example usage:

    .. code-block:: python

        from sunflare.controller import SignalerController
        from sunflare.config import ControllerInfo
        from attrs import define


        @define
        class MyControllerInfo(ControllerInfo):
            str_param: str
            bool_param: bool
            # any other parameters...


        class MyController(SignalerController[MyControllerInfo]):
            sigRegisteredSignal = Signal(str)
            sigUnregisteredSignal = Signal(int)

            def __init__(
                self,
                ctrl_info: MyControllerInfo,
                models: Mapping[str, ModelProtocol],
                virtual_bus: VirtualBus,
            ) -> None:
                signals = ["sigRegisteredSignal"]
                super().__init__(ctrl_info, models, virtual_bus, signals)
                # any other initialization code...


    See :class:`~sunflare.controller.Controller` for parent information.

    .. note::

        Users should carefully document the data transmitted by the signals
        to ensure other endpoints can easily connect to them.

    Parameters
    ----------
    ctrl_info : ``CI``
        Instance of a :class:`~sunflare.config.ControllerInfo` subclass.
    models : ``Mapping[str, ModelProtocol]``
        Reference to the models used in the controller.
    virtual_bus : :class:`~sunflare.virtual.VirtualBus`
        Reference to the virtual bus.
    signals : ``Iterable[str]``, keyword-only, optional
        Iterable of signals to register.
        Default is ``None`` (no signals registered).

    Attributes
    ----------
    signals : ``Iterable[str]``, optional
        Iterable of registered signals.
    """

    def __init__(
        self,
        ctrl_info: CI,
        models: Mapping[str, ModelProtocol],
        virtual_bus: VirtualBus,
        *,
        signals: Optional[Iterable[str]] = None,
    ) -> None:
        self.signals = signals
        super().__init__(ctrl_info, models, virtual_bus)

    def registration_phase(self) -> None:
        """Register the signals defined in ``self.signals``.

        This method is called from Redsun during
        application initialization.
        """
        self.virtual_bus.register_signals(self, self.signals)


class Receiver(Controller[CI]):
    """A controller capable of connecting signals exposed in the virtual bus to local slots.

    Provides an additional `connection_map` parameter to the constructor
    to optionally connect a group of the controller's defined signals to local slots.

    Users may subclass from this controller and provide their custom
    :class:`~sunflare.config.ControllerInfo` implementation.

    Example usage:

    .. code-block:: python

        from sunflare.controller import ReceiverController
        from sunflare.config import ControllerInfo
        from attrs import define

        @define
        class MyControllerInfo(ControllerInfo):
            str_param: str
            bool_param: bool
            # any other parameters...

        class MyController(ReceiverController[MyControllerInfo]):
            def __init__(
                self,
                ctrl_info: MyControllerInfo,
                models: Mapping[str, ModelProtocol],
                virtual_bus: VirtualBus,
            ) -> None:
                connection_map = {
                    "WidgetEmitter": [
                        Connection("sigWidgetSignal1", self.widget_slot),
                        Connection("sigWidgetSignal2", self.other_widget_slot)
                    ],
                    "ControllerEmitter": [
                        Connection("sigControllerSignal", self.controller_slot),
                    ],
                }
                super().__init__(ctrl_info, models, virtual_bus, connection_map)
                # any other initialization code...

            def widget_slot(self, *args, **kwargs) -> None:
                # your logic here...

            def other_widget_slot(self, *args, **kwargs) -> None:
                # your logic here...

            def controller_slot(self, *args, **kwargs) -> None:
                # your logic here...

        .. note::

            The controller slots should respect the signals' signatures
            in order to correctly receive the emitted signals.
            Make sure to review any provided documentation
            about the nature of the signals being connected.

    See :class:`~sunflare.controller.Controller` for parent information.

    Parameters
    ----------
    ctrl_info : ``CI``
        Instance of a :class:`~sunflare.config.ControllerInfo` subclass.
    models : ``Mapping[str, ModelProtocol]``
        Reference to the models used in the controller.
    virtual_bus : :class:`~sunflare.virtual.VirtualBus`
        Reference to the virtual bus.
    connection_map : ``Mapping[str, list[Connection]]``, optional
        Mapping of emitters to a list of connections.
        Default is ``None`` (no connections).

    Attributes
    ----------
    connection_map : ``Mapping[str, list[Connection]]``, keyword-only, optional
        Mapping of emitters to a list of connections.
    """

    def __init__(
        self,
        ctrl_info: CI,
        models: Mapping[str, ModelProtocol],
        virtual_bus: VirtualBus,
        *,
        connection_map: Optional[Mapping[str, list[Connection]]] = None,
    ) -> None:
        self.connection_map = connection_map
        super().__init__(ctrl_info, models, virtual_bus)

    def connection_phase(self) -> None:
        """Connect the signals defined in ``self.connection_map``.

        This method is called from Redsun during
        application initialization.
        """
        if self.connection_map is not None:
            for emitter, connections in self.connection_map.items():
                for connection in connections:
                    self.virtual_bus[emitter][connection.signal].connect(
                        connection.slot
                    )


class SenderReceiver(Controller[CI]):
    """Combines the functionality of :class:`~sunflare.controller.Sender` and :class:`~sunflare.controller.Receiver`.

    Users may subclass from this controller and provide their custom
    :class:`~sunflare.config.ControllerInfo` implementation.

    Example usage:

    .. code-block:: python

        from sunflare.controller import SenderReceiverController
        from sunflare.config import ControllerInfo
        from attrs import define

        @define
        class MyControllerInfo(ControllerInfo):
            str_param: str
            bool_param: bool
            # any other parameters...

        class MyController(SenderReceiverController[MyControllerInfo]):
            sigRegisteredSignal = Signal(str)
            sigUnregisteredSignal = Signal(int)

            def __init__(
                self,
                ctrl_info: MyControllerInfo,
                models: Mapping[str, ModelProtocol],
                virtual_bus: VirtualBus,
            ) -> None:
                signals = ["sigRegisteredSignal"]
                connection_map = {
                    "WidgetEmitter": [
                        Connection("sigWidgetSignal1", self.widget_slot),
                        # you can recover the slot with "getattr(self, <slot_name>)" too
                        Connection("sigWidgetSignal2", getattr(self, "other_widget_slot"))
                    ],
                    "ControllerEmitter": [
                        Connection("sigControllerSignal", self.controller_slot),
                    ],
                }
                super().__init__(ctrl_info, models, virtual_bus, signals, connection_map)
                # any other initialization code...

            def widget_slot(self, *args, **kwargs) -> None:
                # your logic here...

            def other_widget_slot(self, *args, **kwargs) -> None:
                # your logic here...

            def controller_slot(self, *args, **kwargs) -> None:
                # your logic here...

        .. note::

            The controller slots should respect the signals' signatures
            in order to correctly receive the emitted signals.
            Make sure to review any provided documentation
            about the nature of the signals being connected.

    Parameters
    ----------
    ctrl_info : ``CI``
        Instance of a :class:`~sunflare.config.ControllerInfo` subclass.
    models : ``Mapping[str, ModelProtocol]``
        Reference to the models used in the controller.
    virtual_bus : :class:`~sunflare.virtual.VirtualBus`
        Reference to the virtual bus.
    signals : ``Iterable[str]``, optional
        Iterable of signals to register.
        Default is ``None`` (no signals registered).
    connection_map : ``Mapping[str, list[Connection]]``, optional
        Mapping of emitters to a list of connections.
        Default is ``None`` (no connections).

    Attributes
    ----------
    signals : ``Iterable[str]``, optional
        Iterable of registered signals.
    connection_map : ``Mapping[str, list[Connection]]``, optional
        Mapping of emitters to a list of connections.
    """

    def __init__(
        self,
        ctrl_info: CI,
        models: Mapping[str, ModelProtocol],
        virtual_bus: VirtualBus,
        *,
        signals: Optional[Iterable[str]] = None,
        connection_map: Optional[Mapping[str, list[Connection]]] = None,
    ) -> None:
        self.signals = signals
        self.connection_map = connection_map
        super().__init__(ctrl_info, models, virtual_bus)

    def registration_phase(self) -> None:
        """Register the signals defined in ``self.signals``.

        This method is called from Redsun during
        application initialization.
        """
        self.virtual_bus.register_signals(self, self.signals)

    def connection_phase(self) -> None:
        """Connect the signals defined in ``self.connection_map``.

        This method is called from Redsun during
        application initialization.
        """
        if self.connection_map is not None:
            for emitter, connections in self.connection_map.items():
                for connection in connections:
                    self.virtual_bus[emitter][connection.signal].connect(
                        connection.slot
                    )

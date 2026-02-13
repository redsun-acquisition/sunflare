from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Callable, NamedTuple, Protocol, runtime_checkable

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence
    from typing import Any

    from sunflare.device import PDevice
    from sunflare.virtual import VirtualBus


@runtime_checkable
class PPresenter(Protocol):  # pragma: no cover
    """Presenter protocol class.

    Provides the interface for a class
    that Redsun can recognize as a presenter by
    implementing the defined attributes.

    Attributes
    ----------
    devices : Mapping[str, PDevice]
        Reference to the devices used in the presenter.
    virtual_bus : VirtualBus
        Reference to the virtual bus.
    """

    virtual_bus: VirtualBus
    devices: Mapping[str, PDevice]


class Connection(NamedTuple):
    """Connection tuple.

    Provides a type-hinted helper
    for describing a connection between
    a virtual bus signal and a local slot.

    Usable with [`sunflare.presenter.Receiver`]()
    and [`sunflare.presenter.SenderReceiver`]()
    to set the `connection_map` parameter.

    Attributes
    ----------
    signal : ``str``
        Signal name.
    slot : ``Callable[..., None]``
        Slot to connect to.
    """

    signal: str
    slot: Callable[..., None]


class Presenter(PPresenter, ABC):
    """Presenter base class.

    Classes that do not directly inherit from it
    will need to match the `__init__` signature
    to ensure that at runtime Redsun registers
    them as virtual subclasses.

    Parameters
    ----------
    devices : ``Mapping[str, PDevice]``
        Reference to the devices used in the presenter.
    virtual_bus : `sunflare.virtual.VirtualBus`
        Reference to the virtual bus.
    kwargs : ``Any``, optional
        Additional keyword arguments for presenter subclasses.
        These are parsed from the session configuration file.
    """

    @abstractmethod
    def __init__(
        self, devices: Mapping[str, PDevice], virtual_bus: VirtualBus, /, **kwargs: Any
    ) -> None:
        self.devices = devices
        self.virtual_bus = virtual_bus


class Sender(Presenter):
    """A presenter capable of emitting signals to the virtual bus.

    Provides an additional `signals` parameter to the constructor
    to optionally register a group of the presenter's defined
    signals.

    Example usage:

    ```python
    from sunflare.presenter import Sender
    from sunflare.virtual import Signal


    class MyPresenter(Sender):
        sigRegisteredSignal = Signal(str)
        sigUnregisteredSignal = Signal(int)

        def __init__(
            self,
            devices: Mapping[str, PDevice],
            virtual_bus: VirtualBus,
        ) -> None:
            signals = ["sigRegisteredSignal"]
            super().__init__(devices, virtual_bus, signals=signals)
            # any other initialization code...
    ```

    See [`sunflare.presenter.Presenter`]() for parent information.

    !!! note
        Users should carefully document the data transmitted by the signals
        to ensure other endpoints can easily connect to them.

    Parameters
    ----------
    devices : ``Mapping[str, PDevice]``
        Reference to the devices used in the presenter.
    virtual_bus : `sunflare.virtual.VirtualBus`
        Reference to the virtual bus.
    signals : ``Sequence[str]``, keyword-only, optional
        Sequence of signals to register.
        Default is ``None`` (no signals registered).

    Attributes
    ----------
    signals : ``Sequence[str]``, optional
        Sequence of registered signals.
    """

    def __init__(
        self,
        devices: Mapping[str, PDevice],
        virtual_bus: VirtualBus,
        *,
        signals: Sequence[str] | None = None,
    ) -> None:
        self.signals = signals
        super().__init__(devices, virtual_bus)

    def registration_phase(self) -> None:
        """Register the signals defined in ``self.signals``.

        This method is called from Redsun during
        application initialization.
        """
        self.virtual_bus.register_signals(self, self.signals)


class Receiver(Presenter):
    """A presenter capable of connecting signals exposed in the virtual bus to local slots.

    Provides an additional `connection_map` parameter to the constructor
    to optionally connect a group of the presenter's defined signals to local slots.

    Example usage:

    ```python
    from sunflare.presenter import Receiver


    class MyPresenter(Receiver):
        def __init__(
            self,
            devices: Mapping[str, PDevice],
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
            super().__init__(devices, virtual_bus, connection_map=connection_map)
            # any other initialization code...

        def widget_slot(self, *args, **kwargs) -> None:
            # your logic here...

        def other_widget_slot(self, *args, **kwargs) -> None:
            # your logic here...

        def controller_slot(self, *args, **kwargs) -> None:
            # your logic here...
    ```

    !!! note
        The presenter slots should respect the signals' signatures
        in order to correctly receive the emitted signals.
        Make sure to review any provided documentation
        about the nature of the signals being connected.

    See [`sunflare.presenter.Presenter`]() for parent information.

    Parameters
    ----------
    devices : ``Mapping[str, PDevice]``
        Reference to the devices used in the presenter.
    virtual_bus : `sunflare.virtual.VirtualBus`
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
        devices: Mapping[str, PDevice],
        virtual_bus: VirtualBus,
        *,
        connection_map: Mapping[str, list[Connection]] | None = None,
    ) -> None:
        self.connection_map = connection_map
        super().__init__(devices, virtual_bus)

    def connect_to_virtual(self) -> None:
        """Connect the signals defined in ``self.connection_map``.

        This method is called from Redsun during
        application initialization.
        """
        if self.connection_map is not None:
            for emitter, connections in self.connection_map.items():
                for connection in connections:
                    self.virtual_bus.signals[emitter][connection.signal].connect(
                        connection.slot
                    )


class SenderReceiver(Presenter):
    """Combines the functionality of [`sunflare.presenter.Sender`]() and [`sunflare.presenter.Receiver`]().

    Example usage:

    ```python
    from sunflare.presenter import SenderReceiver
    from sunflare.virtual import Signal


    class MyPresenter(SenderReceiver):
        sigRegisteredSignal = Signal(str)
        sigUnregisteredSignal = Signal(int)

        def __init__(
            self,
            devices: Mapping[str, PDevice],
            virtual_bus: VirtualBus,
        ) -> None:
            signals = ["sigRegisteredSignal"]
            connection_map = {
                "WidgetEmitter": [
                    Connection("sigWidgetSignal1", self.widget_slot),
                    Connection("sigWidgetSignal2", getattr(self, "other_widget_slot"))
                ],
                "ControllerEmitter": [
                    Connection("sigControllerSignal", self.controller_slot),
                ],
            }
            super().__init__(devices, virtual_bus, signals=signals, connection_map=connection_map)
            # any other initialization code...

        def widget_slot(self, *args, **kwargs) -> None:
            # your logic here...

        def other_widget_slot(self, *args, **kwargs) -> None:
            # your logic here...

        def controller_slot(self, *args, **kwargs) -> None:
            # your logic here...
    ```

    !!! note
        The presenter slots should respect the signals' signatures
        in order to correctly receive the emitted signals.
        Make sure to review any provided documentation
        about the nature of the signals being connected.

    Parameters
    ----------
    devices : ``Mapping[str, PDevice]``
        Reference to the devices used in the presenter.
    virtual_bus : `sunflare.virtual.VirtualBus`
        Reference to the virtual bus.
    signals : ``Sequence[str]``, optional
        Sequence of signals to register.
        Default is ``None`` (no signals registered).
    connection_map : ``Mapping[str, list[Connection]]``, optional
        Mapping of emitters to a list of connections.
        Default is ``None`` (no connections).

    Attributes
    ----------
    signals : ``Sequence[str]``, optional
        Sequence of registered signals.
    connection_map : ``Mapping[str, list[Connection]]``, optional
        Mapping of emitters to a list of connections.
    """

    def __init__(
        self,
        devices: Mapping[str, PDevice],
        virtual_bus: VirtualBus,
        *,
        signals: Sequence[str] | None = None,
        connection_map: Mapping[str, list[Connection]] | None = None,
    ) -> None:
        self.signals = signals
        self.connection_map = connection_map
        super().__init__(devices, virtual_bus)
        self.virtual_bus.register_signals(self, self.signals)

    def connect_to_virtual(self) -> None:
        """Connect the signals defined in ``self.connection_map``.

        This method is called from Redsun during
        application initialization.
        """
        if self.connection_map is not None:
            for emitter, connections in self.connection_map.items():
                for connection in connections:
                    self.virtual_bus.signals[emitter][connection.signal].connect(
                        connection.slot
                    )

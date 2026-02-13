from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Callable,
    NamedTuple,
)

from typing_extensions import Protocol, runtime_checkable

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

    from sunflare.model import PModel
    from sunflare.virtual import VirtualBus


@runtime_checkable
class PPresenter(Protocol):  # pragma: no cover
    """Presenter protocol class.

    Provides the interface for a class
    that Redsun can recognize as a presenter by
    implementing the defined attributes.

    Attributes
    ----------
    models : Mapping[str, PModel]
        Reference to the models used in the presenter.
    virtual_bus : VirtualBus
        Reference to the virtual bus.
    """

    virtual_bus: VirtualBus
    models: Mapping[str, PModel]


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


class Presenter(PPresenter):
    """A boilerplate base class for quick presenter development.

    Users may subclass from this presenter and provide their
    initialization logic directly.

    Example usage:

    ```python
    from sunflare.presenter import Presenter


    class MyPresenter(Presenter):
        def __init__(
            self,
            models: Mapping[str, PModel],
            virtual_bus: VirtualBus,
            custom_param: str,
        ) -> None:
            super().__init__(models, virtual_bus)
            self.custom_param = custom_param
            # any other initialization code...
    ```

    Parameters
    ----------
    models : ``Mapping[str, PModel]``
        Reference to the models used in the presenter.
    virtual_bus : `sunflare.virtual.VirtualBus`
        Reference to the virtual bus.
    """

    def __init__(
        self,
        models: Mapping[str, PModel],
        virtual_bus: VirtualBus,
    ) -> None:
        self.models = models
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
            models: Mapping[str, PModel],
            virtual_bus: VirtualBus,
        ) -> None:
            signals = ["sigRegisteredSignal"]
            super().__init__(models, virtual_bus, signals=signals)
            # any other initialization code...
    ```

    See [`sunflare.presenter.Presenter`]() for parent information.

    !!! note
        Users should carefully document the data transmitted by the signals
        to ensure other endpoints can easily connect to them.

    Parameters
    ----------
    models : ``Mapping[str, PModel]``
        Reference to the models used in the presenter.
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
        models: Mapping[str, PModel],
        virtual_bus: VirtualBus,
        *,
        signals: Sequence[str] | None = None,
    ) -> None:
        self.signals = signals
        super().__init__(models, virtual_bus)

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
            models: Mapping[str, PModel],
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
            super().__init__(models, virtual_bus, connection_map=connection_map)
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
    models : ``Mapping[str, PModel]``
        Reference to the models used in the presenter.
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
        models: Mapping[str, PModel],
        virtual_bus: VirtualBus,
        *,
        connection_map: Mapping[str, list[Connection]] | None = None,
    ) -> None:
        self.connection_map = connection_map
        super().__init__(models, virtual_bus)

    def connection_phase(self) -> None:
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
            models: Mapping[str, PModel],
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
            super().__init__(models, virtual_bus, signals=signals, connection_map=connection_map)
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
    models : ``Mapping[str, PModel]``
        Reference to the models used in the presenter.
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
        models: Mapping[str, PModel],
        virtual_bus: VirtualBus,
        *,
        signals: Sequence[str] | None = None,
        connection_map: Mapping[str, list[Connection]] | None = None,
    ) -> None:
        self.signals = signals
        self.connection_map = connection_map
        super().__init__(models, virtual_bus)

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
                    self.virtual_bus.signals[emitter][connection.signal].connect(
                        connection.slot
                    )

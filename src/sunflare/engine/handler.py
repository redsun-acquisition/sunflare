"""``handler`` module."""

from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, Any, Callable, Literal, Optional, Protocol, Union

from bluesky.utils import MsgGenerator

from sunflare.config import MotorModelInfo, DetectorModelInfo
from sunflare.engine.detector import DetectorProtocol
from sunflare.engine.motor import MotorProtocol
from sunflare.virtualbus import VirtualBus

if TYPE_CHECKING:
    # TODO: create a protocol for the engine?
    from bluesky.run_engine import RunEngine


EventName = Literal["all", "start", "descriptor", "event", "stop"]
Motor = MotorProtocol[MotorModelInfo]
Detector = DetectorProtocol[DetectorModelInfo]


class EngineHandler(Protocol):
    """``EngineHandler`` protocol class.

    The ``EngineHandler`` wraps the acquisition engine and provides a common interface for all engines.
    It communicates with the rest of the application via the virtual buses.

    Controllers receive a reference to the ``EngineHandler`` object in their constructor.

    Parameters
    ----------
    virtual_bus : :class:`~sunflare.virtualbus.VirtualBus`
        Module-local virtual bus.
    module_bus : :class:`~sunflare.virtualbus.VirtualBus`
        Inter-module virtual bus.
    """

    _plans: dict[str, MsgGenerator[Any]]
    _virtual_bus: VirtualBus
    _module_bus: VirtualBus
    _engine: RunEngine

    @abstractmethod
    def __init__(
        self,
        virtual_bus: VirtualBus,
        module_bus: VirtualBus,
    ) -> None: ...

    @abstractmethod
    def shutdown(self) -> None:
        """Perform a clean shutdown of the engine."""
        ...

    @abstractmethod
    def register_plan(self, name: str, plan: MsgGenerator[Any]) -> None:
        """
        Register a new workflow in the handler.

        Parameters
        ----------
        name : ``str``
            Plan unique identifier.
        plan : ``MsgGenerator[Any]``
            Plan to be registered.
        """
        ...

    @abstractmethod
    def load_device(self, name: str, device: Union[Motor, Detector]) -> None:
        """Load a device into the handler and make it available to the rest of the application.

        Parameters
        ----------
        name : ``str``
            Device unique identifier.
        device : Union[Motor, Detector]
            Device to be loaded.
        """
        ...

    @abstractmethod
    def subscribe(
        self,
        func: Callable[
            [EventName, dict[str, Any]],
            None,
        ],
        name: Optional[EventName] = "all",
    ) -> int:
        """Subscribe a callback function to the engine notifications.

        The callback has signature ``func(name, document)``:

        - ``name`` is the type of document the callback should receive;
            - ``"all"``: all documents;
            - ``"start"``: start documents;
            - ``"descriptor"``: descriptor documents;
            - ``"event"``: event documents;
            - ``"stop"``: stop documents.
        - ``document`` is the document received from the engine (a dictionary).

        Parameters
        ----------
        func: Callable[[EventName, dict[str, Any]], None]
            Function to be called when the event occurs.
        name: Optional[EventName]
            Event type. Defaults to ``"all"``.

        Returns
        -------
        token: int
            Subscription token. It can be used to unsubscribe the callback.

        Notes
        -----
        See also :meth:`~bluesky.run_engine.RunEngine.unsubscribe`.
        """
        ...

    @abstractmethod
    def unsubscribe(self, token: int) -> None:
        """Unregister a callback function its integer ID.

        Parameters
        ----------
        token: int
            Subscription token.

        Notes
        -----
        See also :meth:`~bluesky.run_engine.RunEngine.unsubscribe`.
        """
        ...

    @property
    def plans(
        self,
    ) -> dict[str, MsgGenerator[Any]]:
        """Plans dictionary."""
        ...

    @property
    def detectors(self) -> dict[str, Detector]:
        """Detectors dictionary."""
        ...

    @property
    def motors(self) -> dict[str, Motor]:
        """Motors dictionary."""
        ...

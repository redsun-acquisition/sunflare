"""``handler`` module."""

from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, Any, Callable, Literal, Optional, Protocol

if TYPE_CHECKING:
    from functools import partial

    from bluesky.run_engine import RunEngine
    from bluesky.utils import DuringTask, MsgGenerator

    from sunflare.config import RedSunSessionInfo
    from sunflare.model import ModelProtocol
    from sunflare.virtual import VirtualBus


EventName = Literal["all", "start", "descriptor", "event", "stop"]


class EngineHandler(Protocol):
    """``EngineHandler`` protocol class.

    The ``EngineHandler`` wraps the acquisition engine and provides a common interface for all engines.
    It communicates with the rest of the application via the virtual buses.

    Controllers receive a reference to the ``EngineHandler`` object in their constructor.

    Parameters
    ----------
    config : :class:`~sunflare.config.RedSunSessionInfo`
        Configuration options for the RedSun instance.
    virtual_bus : :class:`~sunflare.virtual.VirtualBus`
        Module-local virtual bus.
    module_bus : :class:`~sunflare.virtual.VirtualBus`
        Inter-module virtual bus.
    during_task : :class:`~bluesky.utils.DuringTask`
        DuringTask object. This object manages the blocking event
        used by the run engine to safely execute the plan.
    """

    _plans: dict[str, dict[str, partial[MsgGenerator[Any]]]]
    _virtual_bus: VirtualBus
    _module_bus: VirtualBus
    _engine: RunEngine

    @abstractmethod
    def __init__(
        self,
        config: RedSunSessionInfo,
        virtual_bus: VirtualBus,
        module_bus: VirtualBus,
        during_task: DuringTask,
    ) -> None: ...

    @abstractmethod
    def shutdown(self) -> None:
        """Perform a clean shutdown of the engine."""
        ...

    @abstractmethod
    def register_plan(self, name: str, plan: partial[MsgGenerator[Any]]) -> None:
        """
        Register a new plan dynamically.

        This method can be used to register a plan from an external source that is not a controller.
        If a key of value ``name`` is already present in the plans dictionary, the plan will be
        appended to the list of plans associated to the key.

        Parameters
        ----------
        name : ``str``
            Key to be used to assign the plan.
        plan : ``MsgGenerator[Any]``
            Plan to be registered.
        """
        ...

    @abstractmethod
    def load_model(self, name: str, model: ModelProtocol) -> None:
        """Load a model into the handler and make it available to the rest of the application.

        This method can be used to dynamically load a model. The request
        for adding a model should be initiated by the plugin manager.

        Parameters
        ----------
        name : ``str``
            Model identifier.
        model : ``ModelProtocol``
            Model to be loaded.
        """
        ...

    @abstractmethod
    def subscribe(
        self,
        func: Callable[[EventName, dict[str, Any]], None],
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
    ) -> dict[str, dict[str, partial[MsgGenerator[Any]]]]:
        """Dictionaries of plans.

        The key of the main dictionary represents the name of the controller.
        The values are dictionaries where:
        - the key is the name of the plan;
        - the value is the plan itself, built as a partial function.
        """
        ...

    @property
    def models(self) -> dict[str, ModelProtocol]:
        """Models dictionary."""
        ...

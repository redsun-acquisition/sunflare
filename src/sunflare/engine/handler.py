"""`EngineHandler` abstract base class."""

from __future__ import annotations

from abc import abstractmethod
from typing import Protocol, Any, Generator, Iterable, Union, TYPE_CHECKING

from sunflare.virtualbus import VirtualBus
from sunflare.types import Workflow

if TYPE_CHECKING:
    # TODO: create a protocol for the engine
    from bluesky.run_engine import RunEngine


class EngineHandler(Protocol):
    """`EngineHandler` protocol class.

    The `EngineHandler` wraps the acquisition engine and provides a common interface for all engines.
    It communicates with the rest of the application via the virtual buses.

    The handler needs to be specialized depending on what engine is being used.

    Parameters
    ----------
    virtual_bus : VirtualBus
        Module-local virtual bus.
    module_bus : VirtualBus
        Inter-module virtual bus.
    """

    _workflows: dict[str, Workflow]
    _virtual_bus: VirtualBus
    _module_bus: VirtualBus

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
    def register_workflows(self, name: str, workflow: Workflow) -> None:
        """
        Register a new workflow in the handler.

        Parameters
        ----------
        name : str
            Workflow unique identifier.
        workflow : Union[Generator, Iterable]
            Workflow to be registered.
        """
        ...

    @property
    @abstractmethod
    def engine(self) -> RunEngine:
        """Returns the engine instance.

        The return type is determined by the specific engine implementation.
        """
        ...

    @property
    def workflows(
        self,
    ) -> dict[str, Union[Generator[Any, None, None], Iterable[Any]]]:
        """Workflows dictionary."""
        ...

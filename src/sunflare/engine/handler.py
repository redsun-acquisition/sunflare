"""`EngineHandler` abstract base class."""

import sys

from abc import abstractmethod
from typing import TYPE_CHECKING, TypeVar, Generic, Protocol

if TYPE_CHECKING:
    from typing import Any, Generator, Iterable, Union

    if sys.version_info < (3, 11):
        from typing_extensions import Self
    else:
        from typing import Self

    from sunflare.config import RedSunInstanceInfo
    from sunflare.virtualbus import VirtualBus
    from sunflare.types import Workflow

E = TypeVar("E", covariant=True)


class EngineHandler(Generic[E], Protocol):
    """`EngineHandler` protocol class.

    The `EngineHandler` class is a singleton that stores all the devices currently
    deployed within a RedSun hardware module. It provides access to the rest of the controller layer
    to information for each device, allowing for execution of atomic operations such as moving
    a motor or setting a light intensity.

    At startup, the `EngineHandler` is populated with the devices defined in the configuration file. These
    can be then accessed as read-only dictionaries, indexing the device by unique identifiers.

    Each engine has its own dedicated `EngineHandler` instance, with common methods that are specialized
    for the specific engine type by using inheritance.

    `EngineHandler` classes hold dictionaries that are used to group up devices by type and provide
    a key-value access to specific devices the user wants to interact with. The types of devices
    the registry can provide depend on the engine capabilities to support that type of device.

    Parameters
    ----------
    config_options: RedSunInstanceInfo
        RedSun instance configuration dataclass.
    virtual_bus : VirtualBus
        Module-local virtual bus.
    module_bus : VirtualBus
        Inter-module virtual bus.
    """

    _workflows: "dict[str, Workflow]"
    _config_options: "RedSunInstanceInfo"
    _virtual_bus: "VirtualBus"
    _module_bus: "VirtualBus"

    @abstractmethod
    def __init__(
        self,
        config_options: "RedSunInstanceInfo",
        virtual_bus: "VirtualBus",
        module_bus: "VirtualBus",
    ) -> None: ...

    @abstractmethod
    def register_device(self, name: str, device: "Any") -> None:
        """
        Add a new device to the registry.

        Child classes must implement this method to add a new device to the registry.

        Parameters
        ----------
        name : str
            Device unique identifier.
        device : Any
            - Device instance
            - The device instance must be coherent with the selected acquisition engine.
            - This means that devices to be added to the registry must inherit from the correct device model class for the selected engine.
        """
        ...

    @abstractmethod
    def shutdown(self) -> None:
        """Perform a clean shutdown of the engine and all its devices."""
        ...

    @abstractmethod
    def register_workflows(self, name: str, workflow: "Workflow") -> None:
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

    @classmethod
    @abstractmethod
    def instance(cls) -> Self:
        """Return the engine handler instance."""
        ...

    @property
    @abstractmethod
    def engine(self) -> E:
        """Returns the engine instance.

        The return type is determined by the specific engine implementation.
        """
        ...

    @property
    def workflows(
        self,
    ) -> "dict[str, Union[Generator[Any, None, None], Iterable[Any]]]":
        """Workflows dictionary."""
        ...

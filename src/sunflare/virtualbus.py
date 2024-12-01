"""
The `VirtualBus` is a mechanism to exchange data between different parts of the system.

The module contains two main classes: `Signal` and `VirtualBus`.

The `Signal` class is a small wrapper around `psygnal.SignalInstance` that provides additional properties to access the signal data types and description.

The `VirtualBus` class is a factory of singleton objects charged of exchanging information between different controllers via `Signals`.

`VirtualBuses` can be inter-module or intra-module, and they can be used to emit notifications, as well as carry information to other plugins and/or different RedSun modules.
"""

from __future__ import annotations

from abc import ABCMeta
from types import MappingProxyType
from typing import final, TYPE_CHECKING, Iterable, ClassVar

from psygnal import SignalInstance, Signal

from sunflare.log import Loggable

if TYPE_CHECKING:
    import sys

    from typing import Optional

    if sys.version_info < (3, 11):
        from typing_extensions import Self
    else:
        from typing import Self

__all__ = ["Signal", "VirtualBus", "ModuleVirtualBus"]

from typing import Callable, TypeVar


F = TypeVar("F", bound=Callable[..., object])


def slot(func: F) -> F:
    """Decorate a function as a slot.

    psygnal does not need this decorator; it is only used for documentation purposes.

    Parameters
    ----------
    func : F
        The function to decorate.

    Returns
    -------
    F
        The same function with the `__isslot__` attribute set to True.
    """
    setattr(func, "__isslot__", True)
    return func


class VirtualBus(Loggable, metaclass=ABCMeta):
    """VirtualBus base class. Supports logging via `Loggable`.

    The VirtualBus is a mechanism to exchange data between different parts of the system.

    They can be used to emit notifications, as well as carry information to other plugins and/or different RedSun modules.

    VirtualBus' signals are implemented using the `psygnal` library; they can be dynamically registered as class attributes, and accessed as a read-only dictionary.
    """

    def __init__(self) -> None:
        # pre-register signals added as attributes in the class definition
        self._cache: dict[str, dict[str, SignalInstance]] = {}

    def register_signals(
        self, owner: object, only: Optional[Iterable[str]] = None
    ) -> None:
        """
        Register the signals of an object in the virtual bus.

        Parameters
        ----------
        owner : object
            The instance whose class's signals are to be cached.
        only : iterable of str, optional
            A list of signal names to cache. If not provided, all
            signals in the class will be cached automatically by inspecting
            the class attributes.

        Notes
        -----
        This method inspects the attributes of the owner's class to find
        `psygnal.Signal` descriptors. For each such descriptor, it retrieves
        the `SignalInstance` from the owner using the descriptor protocol and
        stores it in the registry.
        """
        owner_class = type(owner)  # Get the class of the object
        class_name = owner_class.__name__  # Name of the class

        if only is None:
            # Automatically detect all attributes of the class that are psygnal Signal descriptors
            only = [
                name
                for name in dir(owner_class)
                if isinstance(getattr(owner_class, name, None), Signal)
            ]

        # Initialize the registry for this class if not already present
        if class_name not in self._cache:
            self._cache[class_name] = {}

        # Iterate over the specified signal names and cache their instances
        for name in only:
            signal_descriptor = getattr(owner_class, name, None)
            if isinstance(signal_descriptor, Signal):
                # Retrieve the SignalInstance using the descriptor protocol
                signal_instance = getattr(owner, name)
                self._cache[class_name][name] = signal_instance

    def __getitem__(self, class_name: str) -> MappingProxyType[str, SignalInstance]:
        """
        Access the registry for a specific class.

        Parameters
        ----------
        class_name: str
            The name of the class whose signals are to be accessed.

        Returns
        -------
        MappingProxyType[str, SignalInstance]
            A read-only dictionary mapping signal names to their `SignalInstance` objects.

        Raises
        ------
        KeyError
            If the class name is not found in the registry.
        """
        if class_name not in self._cache:
            raise KeyError(f"Class '{class_name}' is not registered.")
        return MappingProxyType(self._cache[class_name])

    def __contains__(self, class_name: str) -> bool:
        """
        Check if a class is in the registry.

        Parameters
        ----------
        class_name : str
            The name of the class to check.

        Returns
        -------
        bool
            True if the class is in the registry, False otherwise.
        """
        return class_name in self._cache


# TODO: should this become a ZMQ server
# where external applications can connect to?
@final
class ModuleVirtualBus(VirtualBus):
    r"""
    Inter-module virtual bus.

    Communication between modules passes via this virtual bus. \
    There can be only one instance of this class within a RedSun application.
    """

    __instance: ClassVar[Optional[ModuleVirtualBus]] = None

    def __new__(cls) -> Self:  # noqa: D102
        if cls.__instance is None:
            cls.__instance = super(ModuleVirtualBus, cls).__new__(cls)

        return cls.__instance

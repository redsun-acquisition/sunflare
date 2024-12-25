r"""
SunFlare virtual module.

This module implements the communication mechanism between the controller layer and the view layer.

It achieves this by using the `psygnal <https://psygnal.readthedocs.io/en/stable/>`_ library.

The module exposes the following:

- the ``psygnal.Signal`` class;
- the ``VirtualBus`` class;
- the ``ModuleVirtualBus`` class;
- the ``slot`` decorator.

``psygnal.Signal`` is the main communication mechanism between controllers and the view layer.

It provides a syntax similar to the Qt signal/slot mechanism, i.e.

.. code-block:: python

    class MyController:
        sigMySignal = Signal()


    def a_slot():
        print("My signal was emitted!")


    ctrl = MyController()
    ctrl.sigMySignal.connect(my_slot)

- The ``VirtualBus`` class is the base class for building virtual communication buses. It must be re-implemented by users that wish to create new modules for RedSun.
- The ``ModuleVirtualBus`` class is a pre-defined bus that acts as the main communication mechanism between modules. Different modules can share information by emitting signals on this bus and connecting to them.
- The ``slot`` decorator is used to mark a function as a slot. In practice, it provides no benefit at runtime; it's used to facilitate code readability.

.. code-block:: python

    # slot will mark the function as a slot
    @slot
    def my_slot():
        print("My slot was called!")
"""

from __future__ import annotations

from abc import ABCMeta
from types import MappingProxyType
from typing import Callable, Iterable, Optional, TypeVar, Union, final, overload

from psygnal import Signal, SignalInstance

from sunflare.log import Loggable

__all__ = ["Signal", "VirtualBus", "ModuleVirtualBus", "slot"]


F = TypeVar("F", bound=Callable[..., object])


@overload
def slot(func: F) -> F: ...


@overload
def slot(*, private: bool) -> Callable[[F], F]: ...


def slot(
    func: Optional[F] = None, *, private: bool = False
) -> Union[F, Callable[[F], F]]:
    """Decorate a function as a slot.

    Parameters
    ----------
    func : ``F``, optional
        The function to decorate. If not provided, the decorator must be applied with arguments.
    private : ``bool``, optional
        Mark the slot as private. Default is ``False``.

    Returns
    -------
    ``Union[F, Callable[[F], F]]``
        Either the decorated function or a callable decorator.
    """

    def decorator(actual_func: F) -> F:
        setattr(actual_func, "__isslot__", True)
        setattr(actual_func, "__isprivate__", private)
        return actual_func

    if func is None:
        return decorator  # Return the decorator function
    else:
        return decorator(func)  # Directly apply the decorator


class VirtualBus(Loggable, metaclass=ABCMeta):
    """``VirtualBus`` abstract base class. Supports logging via :class:`~sunflare.log.Loggable`.

    The ``VirtualBus`` is a mechanism to exchange data between different parts of the system.

    It can be used to emit notifications, as well as carry information to other plugins and/or different RedSun modules.

    ``VirtualBus``' signals are implemented using the ``psygnal`` library; they can be dynamically registered as class attributes, and accessed as a read-only dictionary.
    """

    def __init__(self) -> None:
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
        ``psygnal.Signal`` descriptors. For each such descriptor, it retrieves
        the ``SignalInstance`` from the owner using the descriptor protocol and
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
            If the class is not found in the registry, an empty dictionary is returned.
        """
        try:
            return MappingProxyType(self._cache[class_name])
        except KeyError:
            self.error(f"Class {class_name} not found in the registry.")
            return MappingProxyType({})

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

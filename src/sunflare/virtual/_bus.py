from __future__ import annotations

from types import MappingProxyType
from typing import (
    Iterable,
)

from psygnal import Signal, SignalInstance

from sunflare.log import Loggable

__all__ = [
    "Signal",
    "VirtualBus",
]


class VirtualBus(Loggable):
    """``VirtualBus``: signal router for data exchange.

    Supports logging via :class:`~sunflare.log.Loggable`.

    The ``VirtualBus`` is a mechanism to exchange
    data between different parts of the system. Communication
    can happen between plugins on the same layer as
    well as between different layers of the system.

    It can be used to emit notifications and carry information
    to other plugins.
    """

    def __init__(self) -> None:
        self._cache: dict[str, dict[str, SignalInstance]] = {}

    def register_signals(
        self, owner: object, only: Iterable[str] | None = None
    ) -> None:
        """
        Register the signals of an object in the virtual bus.

        Parameters
        ----------
        owner : ``object``
            The instance whose class's signals are to be cached.
        only : ``Iterable[str]``, optional
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
            # Automatically detect all attributes of the class that are psygnal.Signal descriptors
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
            self.logger.error(f"Class {class_name} not found in the registry.")
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

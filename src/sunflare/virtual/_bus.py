from __future__ import annotations

import inspect
from collections.abc import Callable
from typing import (
    Iterable,
    TypeAlias,
    TypeVar,
)

from event_model import DocumentRouter
from event_model.documents import Document
from psygnal import Signal, SignalInstance

from sunflare.log import Loggable

__all__ = [
    "Signal",
    "VirtualBus",
]

K = TypeVar("K")
V = TypeVar("V")

CallbackType: TypeAlias = Callable[[str, Document], None] | DocumentRouter
SignalCache: TypeAlias = dict[str, SignalInstance]


class VirtualBus(Loggable):
    """``VirtualBus``: router object for data exchange.

    The ``VirtualBus`` is a mechanism to exchange
    data between different parts of the system. Communication
    can happen between plugins on the same layer as
    well as between different layers of the system.

    It can be used to emit notifications and carry information
    to other plugins, or to register document callbacks
    that process documents generated during data acquisition.
    """

    def __init__(self) -> None:
        self._signals: dict[str, SignalCache] = {}
        self._callbacks: dict[str, CallbackType] = {}

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
        if class_name not in self._signals:
            self._signals[class_name] = SignalCache()

        # Iterate over the specified signal names and cache their instances
        for name in only:
            signal_descriptor = getattr(owner_class, name, None)
            if isinstance(signal_descriptor, Signal):
                # Retrieve the SignalInstance using the descriptor protocol
                signal_instance = getattr(owner, name)
                self._signals[class_name][name] = signal_instance

    def register_callbacks(self, callback: CallbackType) -> None:
        """Register a document callback in the virtual bus.

        Allows other components of the system access to
        specific document routers through the `callbacks` property.

        Parameters
        ----------
        callback : ``CallbackType``
            The document callback to register.

        Raises
        ------
        TypeError
            If the provided callback is not callable or does not
            accept the correct parameters.
        """
        if isinstance(callback, DocumentRouter):
            self._callbacks[callback.__class__.__name__] = callback
        else:
            if not callable(callback):
                raise TypeError(f"{callback} is not callable.")
            # validate that the callback accepts only two parameters
            try:
                inspect.signature(callback).bind(None, None)
            except TypeError as e:
                raise TypeError(
                    "The callback function must accept exactly two parameters: "
                    "'name' (str) and 'document' (Document)."
                ) from e

            # determine the key based on the type of callback
            if inspect.ismethod(callback):
                # bound method: if it's __call__, use the class name; otherwise use the method name
                if callback.__name__ == "__call__":
                    key = callback.__self__.__class__.__name__
                else:
                    key = callback.__name__
            elif inspect.isfunction(callback):
                # regular function: use the function name
                key = callback.__name__
            elif hasattr(callback, "__call__"):
                # callable object (instance with __call__ method): use the class name
                key = callback.__class__.__name__
            else:
                # fallback (should not reach here due to earlier callable check)
                key = callback.__name__

            self._callbacks[key] = callback

    @property
    def callbacks(self) -> dict[str, CallbackType]:
        """The currently registered document callbacks in the virtual bus."""
        return self._callbacks

    @property
    def signals(self) -> dict[str, SignalCache]:
        """The currently registered signals in the virtual bus."""
        return self._signals

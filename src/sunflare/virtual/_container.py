from __future__ import annotations

import inspect
from collections.abc import Callable
from typing import (
    Iterable,
    TypeAlias,
    TypeVar,
)

from dependency_injector.containers import DynamicContainer
from event_model import DocumentRouter
from event_model.documents import Document
from psygnal import Signal, SignalInstance

from sunflare.log import Loggable

K = TypeVar("K")
V = TypeVar("V")

CallbackType: TypeAlias = Callable[[str, Document], None] | DocumentRouter
"""Type alias for document callback functions."""

SignalCache: TypeAlias = dict[str, SignalInstance]
"""Cache type for signals of a specific class."""

__all__ = ["Signal", "VirtualContainer", "CallbackType", "SignalCache"]


class VirtualContainer(DynamicContainer, Loggable):
    """Data exchange and dependency injection layer.

    ``VirtualContainer`` is a :class:`dependency_injector.containers.DynamicContainer`
    that also acts as a runtime signal bus.  It replaces the former
    ``VirtualBus`` while keeping the same public API for signal and
    callback registration/lookup so that existing components need only
    update their type annotations.

    Communication can happen between plugins on the same layer as well as
    between different layers of the system.  Signals can be emitted to
    carry information to other plugins, and document callbacks can be
    registered to process documents generated during data acquisition.

    Notes
    -----
    ``DynamicContainer`` is implemented in Cython and carries its own
    metaclass.  ``VirtualContainer`` must **not** redeclare ``__init__``
    in a way that conflicts with that metaclass — the Loggable mixin is
    safe because it only adds a ``log`` property via ``__init_subclass__``.
    """

    def __init__(self) -> None:
        super().__init__()
        self._signals: dict[str, SignalCache] = {}
        self._callbacks: dict[str, CallbackType] = {}

    # ------------------------------------------------------------------
    # Signal registry – identical public API to the old VirtualBus
    # ------------------------------------------------------------------

    def register_signals(
        self, owner: object, only: Iterable[str] | None = None
    ) -> None:
        """Register the signals of an object in the virtual container.

        Parameters
        ----------
        owner : object
            The instance whose class's signals are to be cached.
        only : Iterable[str], optional
            A list of signal names to cache. If not provided, all
            signals in the class will be cached automatically by inspecting
            the class attributes.

        Notes
        -----
        This method inspects the attributes of the owner's class to find
        :class:`psygnal.Signal` descriptors. For each such descriptor, it
        retrieves the :class:`psygnal.SignalInstance` from the owner using
        the descriptor protocol and stores it in the registry.
        """
        owner_class = type(owner)
        class_name = owner_class.__name__

        if only is None:
            only = [
                name
                for name in dir(owner_class)
                if isinstance(getattr(owner_class, name, None), Signal)
            ]

        if class_name not in self._signals:
            self._signals[class_name] = SignalCache()

        for name in only:
            signal_descriptor = getattr(owner_class, name, None)
            if isinstance(signal_descriptor, Signal):
                signal_instance = getattr(owner, name)
                self._signals[class_name][name] = signal_instance

    def register_callbacks(self, callback: CallbackType) -> None:
        """Register a document callback in the virtual container.

        Allows other components of the system access to specific document
        routers through the ``callbacks`` property.

        Parameters
        ----------
        callback : CallbackType
            The document callback to register.

        Raises
        ------
        TypeError
            If the provided callback is not callable or does not accept the
            correct parameters.
        """
        if isinstance(callback, DocumentRouter):
            self._callbacks[callback.__class__.__name__] = callback
        else:
            if not callable(callback):
                raise TypeError(f"{callback} is not callable.")
            try:
                inspect.signature(callback).bind(None, None)
            except TypeError as e:
                raise TypeError(
                    "The callback function must accept exactly two parameters: "
                    "'name' (str) and 'document' (Document)."
                ) from e

            if inspect.ismethod(callback):
                if callback.__name__ == "__call__":
                    key = callback.__self__.__class__.__name__
                else:
                    key = callback.__name__
            elif inspect.isfunction(callback):
                key = callback.__name__
            elif hasattr(callback, "__call__"):
                key = callback.__class__.__name__
            else:
                key = callback.__name__

            self._callbacks[key] = callback

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def callbacks(self) -> dict[str, CallbackType]:
        """The currently registered document callbacks."""
        return self._callbacks

    @property
    def signals(self) -> dict[str, SignalCache]:
        """The currently registered signals."""
        return self._signals

from __future__ import annotations

import inspect
from collections.abc import Callable
from typing import (
    TYPE_CHECKING,
    Iterable,
    TypeAlias,
    TypeVar,
)

import dependency_injector.containers as dic
import dependency_injector.providers as dip
from event_model import DocumentRouter
from event_model.documents import Document
from psygnal import Signal, SignalInstance

from sunflare.log import Loggable

K = TypeVar("K")
V = TypeVar("V")

CallbackType: TypeAlias = Callable[[str, Document], None] | DocumentRouter
"""Type alias for document callback functions."""

__all__ = ["Signal", "VirtualContainer"]

SignalCache: TypeAlias = dict[str, SignalInstance]

if TYPE_CHECKING:
    from bluesky.protocols import HasName


class VirtualContainer(dic.DynamicContainer, Loggable):
    """Data exchange and dependency injection layer.

    `VirtualContainer` is a [`DynamicContainer`][dependency_injector.containers.DynamicContainer]
    that also acts as a runtime signal bus and data sharing layer for an application.
    """

    _signals = dip.Factory(dict[str, SignalCache])
    _callbacks = dip.Factory(dict[str, CallbackType])

    def register_signals(
        self, owner: HasName, name: str | None = None, only: Iterable[str] | None = None
    ) -> None:
        """Register the signals of an object in the virtual container.

        Parameters
        ----------
        owner : HasName
            The instance whose class's signals are to be cached.
            Must provide a `name` attribute.
        name : str | None
            An optional name to use as the key for caching the signals.
            If not provided, the `name` of `owner` will be used.
        only : Iterable[str], optional
            A list of signal names to cache. If not provided, all
            signals in the class will be cached automatically by inspecting
            the class attributes.

        Notes
        -----
        This method inspects the attributes of the owner's class to find
        [`psygnal.Signal`][psygnal.Signal] descriptors. For each such descriptor, it
        retrieves the [`psygnal.SignalInstance`][psygnal.SignalInstance] from the owner using
        the descriptor protocol and stores it in the registry.
        """
        owner_class = type(owner)
        if name is not None:
            cache_entry = name
        else:
            cache_entry = owner.name

        if only is None:
            only = [
                name
                for name in dir(owner_class)
                if isinstance(getattr(owner_class, name, None), Signal)
            ]

        for name in only:
            signal_descriptor = getattr(owner_class, name, None)
            if isinstance(signal_descriptor, Signal):
                signal_instance = getattr(owner, name)
                self._signals.add_kwargs(**{cache_entry: {name: signal_instance}})

    def register_callbacks(self, name: str, callback: CallbackType) -> None:
        """Register a document callback in the virtual container.

        Allows other components of the system access to specific document
        routers through the ``callbacks`` property.

        Parameters
        ----------
        name: str
            Name to register the callback under.
        callback : CallbackType
            The document callback to register.

        Raises
        ------
        TypeError
            If the provided callback is not callable or does not accept the
            correct parameters.
        """
        if not callable(callback):
            raise TypeError(f"{callback} is not callable.")
        try:
            inspect.signature(callback).bind(None, None)
        except TypeError as e:
            raise TypeError(
                "The callback function must accept exactly two parameters: "
                "'name' (str) and 'document' (Document)."
            ) from e

        self._callbacks.add_kwargs(**{name: callback})

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def callbacks(self) -> dict[str, CallbackType]:
        """The currently registered document callbacks."""
        return self._callbacks()

    @property
    def signals(self) -> dict[str, SignalCache]:
        """The currently registered signals."""
        return self._signals()

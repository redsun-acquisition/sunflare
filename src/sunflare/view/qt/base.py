"""Base widget module.

This module contains the basic functionalities a widget of any framework should provide in order to build up
a Qt GUI that is consistent throught all the RedSun stack.
"""

from __future__ import annotations

from abc import abstractmethod, ABCMeta
from typing import Protocol, TYPE_CHECKING

from qtpy.QtWidgets import QWidget
from qtpy.QtCore import QMetaObject

if TYPE_CHECKING:
    from sunflare.virtualbus import VirtualBus

    from typing import Any

__all__ = ["BaseWidget"]


class _QMeta(QMetaObject, ABCMeta):
    pass


class WidgetProtocol(Protocol):
    """Minimmal protocol a widget should implement."""

    _virtual_bus: VirtualBus
    _module_bus: VirtualBus

    @abstractmethod
    def registration_phase(self) -> None:
        r"""Register the widget signals listed in this method to expose them to the virtual buses.

        At application start-up, widgets can't know what signals are available from other controllers or widgets. \
        This method is called after all widgets are initialized to allow them to register their signals. \
        Widgets may be able to register further signals even after this phase (but not before the `connection_phase` ended). \
        
        Only signals defined in your widgets can be registered.
        
        An implementation example:

        .. code-block:: python

            def registration_phase(self) -> None:
                # you can register all signals...
                self._module_bus.register_signals(self)
                
                # ... or only a selection of them
                self._module_bus.register_signals(self, only=["sigMySignal", "sigMyOtherSignal"])
                
                # you can also register signals to the module bus
                self._module_bus.register_signals(self, only=["sigMySignal", "sigMyOtherSignal"])
        """
        ...

    @abstractmethod
    def connection_phase(self) -> None: ...

    @property
    @abstractmethod
    def virtual_bus(self) -> VirtualBus:
        """Returns the inter-module bus."""
        ...

    @property
    @abstractmethod
    def module_bus(self) -> VirtualBus:
        """Returns the intra-module bus."""
        ...


class BaseWidget(QWidget, WidgetProtocol, metaclass=_QMeta):
    """Base widget class. Requires user implementation.

    Parameters
    ----------
    virtual_bus : VirtualBus
        The inter-module bus.
    module_bus : VirtualBus
        The intra-module bus.
    *args : Any
        Additional arguments to pass to the QWidget constructor.
    **kwargs : Any
        Additional keyword arguments to pass to the QWidget constructor.
    """

    @abstractmethod
    def __init__(
        self,
        virtual_bus: VirtualBus,
        module_bus: VirtualBus,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self._virtual_bus = virtual_bus
        self._module_bus = module_bus

    @property
    def virtual_bus(self) -> VirtualBus:
        """Returns the inter-module bus."""
        return self._virtual_bus

    @property
    def module_bus(self) -> VirtualBus:
        """Returns the intra-module bus."""
        return self._module_bus

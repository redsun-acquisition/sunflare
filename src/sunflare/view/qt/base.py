"""Base widget module.

This module contains the basic functionalities a widget of any framework should provide in order to build up
a Qt GUI that is consistent throught all the RedSun stack.
"""

from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, Protocol, runtime_checkable

from qtpy.QtWidgets import QWidget

if TYPE_CHECKING:
    from typing import Any

    from sunflare.config import RedSunSessionInfo
    from sunflare.virtual import VirtualBus

__all__ = ["BaseWidget", "WidgetProtocol"]


@runtime_checkable
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
    def connection_phase(self) -> None:
        """Connect to other controllers or widgets.

        At application start-up, widgets can't know what signals are available from other parts of RedSun.
        This method is invoked after the controller's construction and after `registration_phase` as well, allowing to
        connect to all available registered signals in both virtual buses.
        Controllers may be able to connect to other signals even after this phase (provided those signals
        were registered before).

        An implementation example:

        .. code-block:: python

            def connection_phase(self) -> None:
                # you can connect signals from another controller to your local slots...
                self._virtual_bus["OtherController"]["sigOtherControllerSignal"].connect(
                    self._my_slot
                )

                # ... or to other signals ...
                self._virtual_bus["OtherController"]["sigOtherControllerSignal"].connect(
                    self.sigMySignal
                )

                # ... or connect to widgets
                self._virtual_bus["OtherWidget"]["sigOtherWidgetSignal"].connect(
                    self._my_slot
                )

                # you can also connect to the module bus
                self._module_bus["OtherController"]["sigOtherControllerSignal"].connect(
                    self._my_slot
                )
                self._module_bus["OtherWidget"]["sigOtherWidgetSignal"].connect(
                    self._my_slot
                )
        """
        ...


class BaseWidget(QWidget):
    """Base widget class for Qt-based widgets.

    Parameters
    ----------
    config : RedSunSessionInfo
        The RedSun instance configuration.
    virtual_bus : VirtualBus
        The inter-module bus.
    module_bus : VirtualBus
        The intra-module bus.
    *args : Any
        Additional arguments to pass to the QWidget constructor.
    **kwargs : Any
        Additional keyword arguments to pass to the QWidget constructor.
    """

    def __init__(
        self,
        config: RedSunSessionInfo,
        virtual_bus: VirtualBus,
        module_bus: VirtualBus,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self._config = config
        self._virtual_bus = virtual_bus
        self._module_bus = module_bus

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
    def connection_phase(self) -> None:
        """Connect to other controllers or widgets.

        At application start-up, widgets can't know what signals are available from other parts of RedSun.
        This method is invoked after the controller's construction and after `registration_phase` as well, allowing to
        connect to all available registered signals in both virtual buses.
        Controllers may be able to connect to other signals even after this phase (provided those signals
        were registered before).

        An implementation example:

        .. code-block:: python

            def connection_phase(self) -> None:
                # you can connect signals from another controller to your local slots...
                self._virtual_bus["OtherController"]["sigOtherControllerSignal"].connect(
                    self._my_slot
                )

                # ... or to other signals ...
                self._virtual_bus["OtherController"]["sigOtherControllerSignal"].connect(
                    self.sigMySignal
                )

                # ... or connect to widgets
                self._virtual_bus["OtherWidget"]["sigOtherWidgetSignal"].connect(
                    self._my_slot
                )

                # you can also connect to the module bus
                self._module_bus["OtherController"]["sigOtherControllerSignal"].connect(
                    self._my_slot
                )
                self._module_bus["OtherWidget"]["sigOtherWidgetSignal"].connect(
                    self._my_slot
                )
        """
        ...

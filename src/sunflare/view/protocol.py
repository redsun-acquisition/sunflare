from __future__ import annotations

import sys

if sys.version_info >= (3, 11):
    from typing import Protocol
else:
    from typing_extensions import Protocol

from abc import abstractmethod
from typing import TYPE_CHECKING, runtime_checkable

if TYPE_CHECKING:
    from typing import Any

    from sunflare.config import RedSunSessionInfo
    from sunflare.virtual import VirtualBus


@runtime_checkable
class WidgetProtocol(Protocol):
    """Minimmal protocol a widget should implement.

    All widgets, regardless of the chosen front-end,
    must implement the methods defined in this protocol.

    Parameters
    ----------
    config : RedSunSessionInfo
        The RedSun instance configuration.
    virtual_bus : VirtualBus
        Main virtual bus for the RedSun instance.
    """

    _config: RedSunSessionInfo
    _virtual_bus: VirtualBus

    @abstractmethod
    def __init__(
        self,
        config: RedSunSessionInfo,
        virtual_bus: VirtualBus,
        *args: Any,
        **kwargs: Any,
    ) -> None: ...

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
                self._virtual_bus.register_signals(self)
                
                # ... or only a selection of them
                self._virtual_bus.register_signals(self, only=["sigMySignal", "sigMyOtherSignal"])
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
        """
        ...

"""RedSun uses controllers to manage the interaction between the user interface and the hardware.

They have access to the `VirtualBus` to enable interaction with other controllers and/or
widgets by exchanging data via either the built-in signals or custom signals that can be defined by the user.

They can keep a reference of hardware devices for exclusive control by selecting the appropriate model from the
`models` dictionary.

Functionally wise, they can:

- publish plans to provide information on their capabilities;
- allocate a reference to the ``RunEngine`` to execute said plans;
- simply process the data acquired by the ``RunEngine``, accessed from the `VirtualBus` signals.

Each controller is associated with a ``ControllerInfo`` object,
which contains a series of user-defined properties that
describe the controller and provides further customization options.
"""

import sys
from abc import abstractmethod
from functools import partial

if sys.version_info >= (3, 11):
    from typing import Protocol
else:
    from typing_extensions import Protocol

from typing import Any, Mapping, runtime_checkable

from bluesky.utils import MsgGenerator

from sunflare.config import ControllerInfo
from sunflare.model import ModelProtocol
from sunflare.virtual import VirtualBus


@runtime_checkable
class ControllerProtocol(Protocol):
    """Controller protocol class.

    Parameters
    ----------
    ctrl_info : :class:`~sunflare.config.ControllerInfo`
        Controller information.
    models : Mapping[str, :class:`~sunflare.model.ModelProtocol`]
        Models currently loaded in the active RedSun session.
    virtual_bus : :class:`~sunflare.virtual.VirtualBus`
        Virtual bus.
    """

    _ctrl_info: ControllerInfo
    _virtual_bus: VirtualBus

    @abstractmethod
    def __init__(
        self,
        ctrl_info: ControllerInfo,
        models: Mapping[str, ModelProtocol],
        virtual_bus: VirtualBus,
    ) -> None: ...

    @abstractmethod
    def shutdown(self) -> None:
        """Shutdown the controller. Performs cleanup operations.

        If the controller holds any kind of resources,
        this method should invoke any equivalent shutdown method for each resource.
        If no resources are held, this method can be left empty.
        """
        ...

    @abstractmethod
    def registration_phase(self) -> None:
        r"""Register the controller signals listed in this method to expose them to the virtual buses.

        At application start-up, controllers can't know what signals are available from other controllers. \
        This method is called after all controllers are initialized to allow them to register their signals. \
        Controllers may be able to register further signals even after this phase (but not before the `connection_phase` ended). \
        
        Only signals defined in your controller can be registered.
        
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

        At application start-up, controllers can't know what signals are available from other parts of RedSun.
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

    @property
    @abstractmethod
    def controller_info(self) -> ControllerInfo:
        """Controller information container."""
        ...

    @property
    @abstractmethod
    def plans(self) -> list[partial[MsgGenerator[Any]]]:
        """List of available plans."""
        ...

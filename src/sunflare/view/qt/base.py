# noqa: D100

from abc import abstractmethod, ABCMeta
from typing import Protocol, TYPE_CHECKING

from qtpy.QtWidgets import QWidget
from qtpy.QtCore import QMetaObject

if TYPE_CHECKING:
    from sunflare.virtualbus import VirtualBus

    from typing import Any


class _QMeta(QMetaObject, ABCMeta):
    pass


class WidgetProtocol(Protocol):
    """:meta-private:"""  # noqa: D400

    _virtual_bus: "VirtualBus"
    _module_bus: "VirtualBus"

    @property
    @abstractmethod
    def virtual_bus(self) -> "VirtualBus":
        """Returns the inter-module bus."""
        ...

    @property
    @abstractmethod
    def module_bus(self) -> "VirtualBus":
        """Returns the intra-module bus."""
        ...


class BaseWidget(QWidget, WidgetProtocol, metaclass=_QMeta):
    """Base widget class. Rerquires implementation from the user.

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
        virtual_bus: "VirtualBus",
        module_bus: "VirtualBus",
        *args: "Any",
        **kwargs: "Any",
    ) -> None:
        super().__init__(*args, **kwargs)
        self._virtual_bus = virtual_bus
        self._module_bus = module_bus

    @property
    def virtual_bus(self) -> "VirtualBus":
        """Returns the inter-module bus."""
        return self._virtual_bus

    @property
    def module_bus(self) -> "VirtualBus":
        """Returns the intra-module bus."""
        return self._module_bus

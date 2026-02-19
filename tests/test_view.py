from sunflare.virtual import VirtualBus
from sunflare.view import View, ViewPosition
from sunflare.view.qt import QtView
from qtpy import QtWidgets as QtW


def test_base_view(bus: VirtualBus) -> None:
    """Test basic Presenter functionality."""

    class TestView(View):
        def __init__(
            self,
            virtual_bus: VirtualBus,
        ) -> None:
            super().__init__(virtual_bus)

        @property
        def view_position(self) -> ViewPosition:
            return ViewPosition.CENTER

    controller = TestView(bus)

    assert controller.virtual_bus == bus
    assert controller.view_position == ViewPosition.CENTER


def test_base_qt_view(bus: VirtualBus) -> None:
    """Test basic Presenter functionality."""

    class TestQtView(QtView):
        def __init__(
            self,
            virtual_bus: VirtualBus,
        ) -> None:
            super().__init__(virtual_bus)

        @property
        def view_position(self) -> ViewPosition:
            return ViewPosition.CENTER

    app = QtW.QApplication([])

    assert app is not None, "A QApplication instance is required to run this test."

    controller = TestQtView(bus)

    assert controller.virtual_bus == bus
    assert controller.view_position == ViewPosition.CENTER

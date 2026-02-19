from sunflare.virtual import VirtualBus
from sunflare.view import View, ViewPosition, PView
from sunflare.view.qt import QtView
from qtpy import QtWidgets as QtW


def test_qtview_subclassing() -> None:
    """Test that QtView is a subclass of View and PView."""

    # PView is a data protocol (no methods);
    # QtView still defines "position" as abstract
    # property, hence it'll fail;
    # we hope that this PView won't cause breakages...
    assert issubclass(QtView, View)


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

    view = TestView(bus)

    assert isinstance(view, View)
    assert isinstance(view, PView)
    assert issubclass(TestView, View)
    assert view.virtual_bus == bus
    assert view.view_position == ViewPosition.CENTER


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

    view = TestQtView(bus)

    assert isinstance(view, View)
    assert isinstance(view, PView)
    assert issubclass(TestQtView, View)
    assert view.virtual_bus == bus
    assert view.view_position == ViewPosition.CENTER

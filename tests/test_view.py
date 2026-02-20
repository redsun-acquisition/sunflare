from sunflare.virtual import VirtualContainer
from sunflare.view import View, ViewPosition, PView
from sunflare.view.qt import QtView
from qtpy import QtWidgets as QtW


def test_qtview_subclassing() -> None:
    """Test that QtView is a subclass of View and PView."""
    assert issubclass(QtView, View)


def test_base_view(bus: VirtualContainer) -> None:
    """Test basic View functionality."""

    class TestView(View):
        def __init__(
            self,
            name: str,
            virtual_container: VirtualContainer,
        ) -> None:
            super().__init__(name, virtual_container)

        @property
        def view_position(self) -> ViewPosition:
            return ViewPosition.CENTER

    view = TestView("my_view", bus)

    assert isinstance(view, View)
    assert isinstance(view, PView)
    assert issubclass(TestView, View)
    assert view.name == "my_view"
    assert view.virtual_container == bus
    assert view.view_position == ViewPosition.CENTER


def test_base_qt_view(bus: VirtualContainer) -> None:
    """Test basic QtView functionality."""

    class TestQtView(QtView):
        def __init__(
            self,
            name: str,
            virtual_container: VirtualContainer,
        ) -> None:
            super().__init__(name, virtual_container)

        @property
        def view_position(self) -> ViewPosition:
            return ViewPosition.CENTER

    app = QtW.QApplication.instance() or QtW.QApplication([])

    assert app is not None, "A QApplication instance is required to run this test."

    view = TestQtView("qt_view", bus)

    assert isinstance(view, View)
    assert isinstance(view, PView)
    assert issubclass(TestQtView, View)
    assert view.name == "qt_view"
    assert view.virtual_container == bus
    assert view.view_position == ViewPosition.CENTER

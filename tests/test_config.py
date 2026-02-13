import pytest
from sunflare.config import FrontendTypes, WidgetPositionTypes


def test_frontend_types() -> None:
    """Test FrontendTypes enum."""
    assert FrontendTypes.PYQT == "pyqt"
    assert FrontendTypes.PYSIDE == "pyside"

    # Test string conversion
    assert FrontendTypes("pyqt") == FrontendTypes.PYQT
    assert FrontendTypes("pyside") == FrontendTypes.PYSIDE


def test_widget_position_types() -> None:
    """Test WidgetPositionTypes enum."""
    assert WidgetPositionTypes.CENTER == "center"
    assert WidgetPositionTypes.LEFT == "left"
    assert WidgetPositionTypes.RIGHT == "right"
    assert WidgetPositionTypes.TOP == "top"
    assert WidgetPositionTypes.BOTTOM == "bottom"

    # Test string conversion
    assert WidgetPositionTypes("center") == WidgetPositionTypes.CENTER
    assert WidgetPositionTypes("left") == WidgetPositionTypes.LEFT
    assert WidgetPositionTypes("right") == WidgetPositionTypes.RIGHT
    assert WidgetPositionTypes("top") == WidgetPositionTypes.TOP
    assert WidgetPositionTypes("bottom") == WidgetPositionTypes.BOTTOM

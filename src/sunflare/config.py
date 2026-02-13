from __future__ import annotations

from enum import Enum, unique

__all__ = [
    "FrontendTypes",
    "WidgetPositionTypes",
]


@unique
class FrontendTypes(str, Enum):
    """Supported frontend types.

    Frontends are the supported GUI frameworks that are used to interact with the user.

    Attributes
    ----------
    PYQT: str
        PyQt6 frontend.
    PYSIDE: str
        PySide6 frontend.
    """

    PYQT = "pyqt"
    PYSIDE = "pyside"


@unique
class WidgetPositionTypes(str, Enum):
    """Supported widget position types.

    This enum is used to to define the
    position of a widget in the main view of the GUI.

    !!! warning

        This enumerator refers to the usage of `QtWidget.DockWidget`;
        it may be changed in the future to support other GUI frameworks.

    Attributes
    ----------
    LEFT: str
        Left widget position.
    RIGHT: str
        Right widget position.
    TOP: str
        Top widget position.
    BOTTOM: str
        Bottom widget position.
    """

    CENTER = "center"
    LEFT = "left"
    RIGHT = "right"
    TOP = "top"
    BOTTOM = "bottom"

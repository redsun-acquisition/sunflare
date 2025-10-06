from __future__ import annotations

import logging
from enum import Enum, unique
from functools import cached_property
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    Mapping,
    Protocol,
    Sized,
    TypeVar,
    runtime_checkable,
)

import numpy as np
import yaml
from attrs import AttrsInstance, asdict, define, field, setters, validators

if TYPE_CHECKING:
    from bluesky.protocols import Descriptor, Reading
    from event_model.documents import Dtype

T = TypeVar("T")


@unique
class FrontendTypes(str, Enum):
    """Supported frontend types.

    Frontends are the supported GUI frameworks that are used to interact with the user.

    Attributes
    ----------
    PYQT
        PyQt6 frontend.
    PYSIDE
        PySide6 frontend.
    """

    PYQT = "pyqt"
    PYSIDE = "pyside"


@unique
class WidgetPositionTypes(str, Enum):
    """Supported widget position types.

    This enum is used to to define the
    position of a widget in the main view of the GUI.

    .. warning::

        This enumerator refers to the usage of `QtWidget.DockWidget`;
        it may be changed in the future to support other GUI frameworks.

    Attributes
    ----------
    LEFT
        Left widget position.
    RIGHT
        Right widget position.
    TOP
        Top widget position.
    BOTTOM
        Bottom widget position.
    """

    CENTER = "center"
    LEFT = "left"
    RIGHT = "right"
    TOP = "top"
    BOTTOM = "bottom"


def _convert_widget_position_type(
    x: str | WidgetPositionTypes,
) -> WidgetPositionTypes:
    return x if isinstance(x, WidgetPositionTypes) else WidgetPositionTypes(x)


@runtime_checkable
class ModelInfoProtocol(AttrsInstance, Protocol):
    """Protocol equivalent to :class:`~sunflare.config.ModelInfo`.

    This protocol allows to implement the ``ModelInfo`` class
    in packages that do not depend on ``sunflare`` directly.

    The only required dependency is `attrs`_.

    _attrs: https://www.attrs.org/en/stable/
    """

    plugin_name: str
    plugin_id: str

    def read_configuration(self, timestamp: float) -> dict[str, Any]:
        """See :meth:`sunflare.config.ModelInfo.read_configuration`."""
        ...

    def describe_configuration(self, source: str) -> dict[str, Any]:
        """See :meth:`sunflare.config.ModelInfo.describe_configuration`."""
        ...


@runtime_checkable
class ControllerInfoProtocol(Protocol):
    """Protocol equivalent to :class:`~sunflare.config.ControllerInfo`.

    .. note::

        This protocol is currently used only for type checking purposes.
        within the Redsun application. In the future
        we might be able to expose this for usage in
        external packages.
    """

    plugin_name: str
    plugin_id: str


@runtime_checkable
class ViewInfoProtocol(Protocol):
    """Protocol equivalent to :class:`~sunflare.config.ViewInfo`.

    .. note::

        This protocol is currently used only for type checking purposes.
        within the Redsun application. In the future
        we might be able to expose this for usage in
        external packages.
    """

    plugin_name: str
    plugin_id: str
    position: WidgetPositionTypes


@define(kw_only=True)
class ViewInfo(ViewInfoProtocol):
    """View information model.

    All view information models inherit from this class.

    Parameters
    ----------
    plugin_name : ``str``, optional
        Widget plugin name.
        Equivalent to the name of the PyPI/Conda package.
    plugin_id : ``str``, optional
        Widget plugin ID.
        Associated with the exposed entry
        point in the plugin manifest.
    repository : ``str``, optional
        Widget repository URL. Defaults to ``N/A``.
    position : ``WidgetPositionTypes``
        Widget position in the main view of the GUI.
    """

    plugin_name: str = field(
        validator=validators.instance_of(str), on_setattr=setters.frozen
    )
    plugin_id: str = field(
        validator=validators.instance_of(str), on_setattr=setters.frozen
    )
    position: WidgetPositionTypes = field(
        converter=_convert_widget_position_type,
        validator=validators.in_(WidgetPositionTypes),
        on_setattr=setters.frozen,
    )


@define(kw_only=True)
class ControllerInfo(ControllerInfoProtocol):
    """Controller information model.

    All controller information models inherit from this class.

    Parameters
    ----------
    plugin_name : ``str``, optional
        Controller plugin name.
        Equivalent to the name of the PyPI/Conda package.
    plugin_id : ``str``, optional
        Controller plugin ID.
        Associated with the exposed entry point
        in the plugin manifest.
    """

    plugin_name: str = field(
        validator=validators.instance_of(str), on_setattr=setters.frozen
    )
    plugin_id: str = field(
        validator=validators.instance_of(str), on_setattr=setters.frozen
    )


@define(kw_only=True)
class ModelInfo(ModelInfoProtocol):
    """Base model for device information.

    All device information models inherit from this class.

    Attributes
    ----------
    plugin_name : ``str``, optional
        Model plugin name.
        Equivalent to the name of the PyPI/Conda package.
    plugin_id : ``str``, optional
        Model plugin ID.
        Associated with the exposed entry point
        in the plugin manifest.
    vendor : ``str``, optional
        Device vendor.
        Defaults to ``N/A``.
    family : ``str``, optional
        Device family (if applicable).
        Defaults to ``N/A``.
    serial_number : ``str``, optional
        Device serial number.
        Defaults to ``N/A``.
    """

    plugin_name: str = field(
        validator=validators.instance_of(str), on_setattr=setters.frozen
    )
    plugin_id: str = field(
        validator=validators.instance_of(str), on_setattr=setters.frozen
    )
    vendor: str = field(default="N/A", validator=validators.instance_of(str))
    family: str = field(
        default="N/A",
        validator=validators.instance_of(str),
    )
    serial_number: str = field(
        default="N/A",
        validator=validators.instance_of(str),
    )

    @cached_property
    def _type_map(self) -> dict[type, Dtype]:
        """Return the type map for the model information."""
        return {
            str: "string",
            float: "number",
            int: "integer",
            bool: "boolean",
            list: "array",
            tuple: "array",
            dict: "array",
            np.ndarray: "array",
            Mapping: "array",
        }

    def __get_shape(self, value: Any) -> list[int]:
        if isinstance(value, Sized) and not isinstance(value, str):
            if hasattr(value, "shape"):
                return list(getattr(value, "shape"))
            else:
                return [len(value)]
        return []

    def __get_type(self, value: T) -> Dtype:
        return self._type_map[type(value)]

    def read_configuration(self, timestamp: float = 0) -> dict[str, Reading[Any]]:
        """Read the model information as a Bluesky configuration dictionary.

        Parameters
        ----------
        timestamp : ``float``, optional
            Timestamp of the configuration.
            Use time.time() to get the current timestamp.
            Defaults to 0.

        Returns
        -------
        ``dict[str, Reading[Any]]``
            A dictionary containing the model information,
            compatible with Bluesky configuration representation.

        Notes
        -----
        See the `Configurable`_ protocol.

        .. _Configurable: https://blueskyproject.io/bluesky/main/hardware.html#bluesky.protocols.Configurable
        """
        return {
            **{
                key: {"value": value, "timestamp": timestamp}
                for key, value in asdict(self).items()
                if key not in ["plugin_name", "plugin_id"]
            }
        }

    def describe_configuration(
        self, source: str = "model_info"
    ) -> dict[str, Descriptor]:
        """Describe the model information as a Bluesky configuration dictionary.

        Parameters
        ----------
        source : ``str``, optional
            Source of the configuration.
            Defaults to ``model_info``.

        Returns
        -------
        ``dict[str, Descriptor]``
            A dictionary containing the model information description,
            compatible with Bluesky configuration representation.

        Notes
        -----
        See the `Configurable`_ protocol.

        .. _Configurable: https://blueskyproject.io/bluesky/main/hardware.html#bluesky.protocols.Configurable
        """
        return {
            **{
                key: {
                    "source": source,
                    "dtype": self.__get_type(value),
                    "shape": self.__get_shape(value),  # type: ignore[typeddict-item]
                }
                for key, value in asdict(self).items()
                if key not in ["plugin_name", "plugin_id"]
            }
        }


# helper private functions for type conversion
def _convert_frontend_type(x: str | FrontendTypes) -> FrontendTypes:
    return x if isinstance(x, FrontendTypes) else FrontendTypes(x)


@define(kw_only=True, slots=True)
class RedSunSessionInfo:
    """Redsun session configuration class.

    This class is used to store the configuration of a running Redsun application;
    it provides information about the hardware layout and the selected acquisition engine.

    A minimal configuration must include:

    - the selected frontend;
    - the selected acquisition engine;

    Attributes
    ----------
    session: ``str``
        The name of the current session. Defaults to ``Redsun``.
        It will be shown as the main window title.
    frontend : ``FrontendTypes``
        Frontend selected for the current session.
        Defaults to ``FrontendTypes.PYQT``.
    controllers : ``dict[str, ControllerInfo]``
        Controller informations dictionary.
        Defaults to an empty dictionary.
    models : ``dict[str, ModelInfo]``
        Model informations dictionary.
        Defaults to an empty dictionary.
    views : ``dict[str, ViewInfo]``
        View informations dictionary.
        Defaults to an empty dictionary.
    """

    session: str = field(
        default="Redsun",
        validator=validators.instance_of(str),
        on_setattr=setters.frozen,
    )
    frontend: FrontendTypes = field(
        converter=_convert_frontend_type,
        validator=validators.in_(FrontendTypes),
        on_setattr=setters.frozen,
    )
    models: dict[str, ModelInfoProtocol] = field(factory=dict)
    controllers: dict[str, ControllerInfoProtocol] = field(factory=dict)
    views: dict[str, ViewInfoProtocol] = field(factory=dict)

    @staticmethod
    def load_yaml(path: str) -> dict[str, Any]:
        """Load a YAML configuration file.

        This method is invoked before the actual construction of the model. It will do
        preliminary checks on the YAML file and store the configuration in a dictionary.

        Parameters
        ----------
        path : ``str``
            Path to the YAML file.

        Returns
        -------
        ``dict[str, Any]``
            A dictionary containing the configuration data.

        Raises
        ------
        ``FileExistsError``
            If the file does not exist.
        ``FileNotFoundError``
            If the path is not a file.
        ``ValueError``
            If the file is not a YAML file.
        ``yaml.YAMLError``
            If an error occurs while loading the file.
        """
        logger = logging.getLogger("redsun")

        path_obj = Path(path)

        data: dict[str, Any] = {}

        if not path_obj.is_absolute():
            path_obj = path_obj.resolve()

        if not path_obj.exists():
            logger.error(f"The file {path} does not exist.")
            raise FileExistsError(f"The file {path} does not exist.")

        if not path_obj.is_file():
            logger.error(f"The path {path} is not a file.")
            raise FileNotFoundError(f"The path {path} is not a file.")

        if path_obj.suffix not in [".yaml", ".yml"]:
            logger.error(f"The file {path} is not a YAML file.")
            raise ValueError(f"The file {path} is not a YAML file.")

        try:
            with open(path, "r") as file:
                data = yaml.safe_load(file)
        except yaml.YAMLError as e:
            logger.exception(f"Error loading YAML file {path}: {e}")
            raise yaml.YAMLError(f"Error loading YAML file {path}: {e}")

        return data

    def store_yaml(self, path: str) -> None:
        """Store the configuration in a YAML file.

        Parameters
        ----------
        path : ``str``
            Path to the desired YAML file.
        """

        def _serializer(inst: Any, field: Any, value: Any) -> Any:
            if isinstance(value, Enum):
                return value.value
            if isinstance(value, tuple):
                return list(value)
            return value

        path_obj = Path(path)
        with open(path_obj, "w") as file:
            yaml.dump(asdict(self, value_serializer=_serializer), file, sort_keys=False)

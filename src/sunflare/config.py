"""RedSun configuration classes and enumerators."""

from __future__ import annotations

from enum import Enum, unique
from pathlib import Path
from typing import Any, Sized, Tuple

import yaml
from attrs import Attribute, asdict, define, field, setters, validators

from sunflare.log import get_logger


@unique
class AcquisitionEngineTypes(str, Enum):
    """ 
    Supported acquisition engines.

    Acquisition engines are objects created within RedSun and operate
    as Bluesky plan managers for the acquisition process. 
    They are responsible for the orchestration of the different hardware 
    components currently loaded in RedSun.

    It is expected that new acquisition engines implement Bluesky's ``RunEngine`` public API.

    Attributes
    ----------
    BLUESKY
        Python-based data acquisition framework for scientific experiments. \
        For more informations, refer to the `Bluesky documentation page <https://blueskyproject.io/bluesky/index.html>`_.
    """

    BLUESKY = "bluesky"


@unique
class FrontendTypes(str, Enum):
    """Supported frontend types.

    Frontends are the supported GUI frameworks that are used to interact with the user.

    Attributes
    ----------
    QT
        Qt frontend.
    """

    QT = "qt"


@define(kw_only=True)
class ControllerInfo:
    """Controller information model.

    All controller information models inherit from this class.

    Parameters
    ----------
    plugin_name : ``str``, optional
        Controller plugin name.
        Equivalent to the name of the PyPI/Conda package.
        Defaults to ``N/A``.
    repository : ``str``, optional
        Controller repository URL. Defaults to ``N/A``.
    """

    plugin_name: str = field(
        default="N/A", validator=validators.instance_of(str), on_setattr=setters.frozen
    )
    repository: str = field(
        default="N/A", validator=validators.instance_of(str), on_setattr=setters.frozen
    )


@define(kw_only=True)
class ModelInfo:
    """Base model for device information.

    All device information models inherit from this class.

    Attributes
    ----------
    model_name : ``str``
        Device model name.
    vendor : ``str``, optional
        Detector vendor.
    serial_number : ``str``, optional
        Detector serial number.
    plugin_name : ``str``, optional
        Model plugin name.
        Equivalent to the name of the PyPI/Conda package.
        Defaults to ``N/A``.
    repository : ``str``, optional
        Model repository URL. Defaults to ``N/A``.
    """

    model_name: str = field(
        validator=validators.instance_of(str), on_setattr=setters.frozen
    )
    vendor: str = field(
        default="N/A", validator=validators.instance_of(str), on_setattr=setters.frozen
    )
    serial_number: str = field(
        default="N/A",
        converter=str,
        on_setattr=setters.frozen,
    )

    plugin_name: str = field(
        default="N/A", validator=validators.instance_of(str), on_setattr=setters.frozen
    )
    repository: str = field(
        default="N/A", validator=validators.instance_of(str), on_setattr=setters.frozen
    )

    __type_map = {
        str: "string",
        float: "number",
        int: "integer",
        bool: "boolean",
        list: "array",
        tuple: "array",
    }

    def __get_shape(self, value: Any) -> list[int]:
        if isinstance(value, Sized):
            if hasattr(value, "shape"):
                return list(getattr(value, "shape"))
            else:
                return [len(value)]
        return []

    def read_configuration(self) -> dict[str, Any]:
        """Read the model information as a Bluesky configuration dictionary.

        Returns
        -------
        ``dict[str, Any]``
            A dictionary containing the model information,
            compatible with Bluesky configuration representation.

        Notes
        -----
        See the `Configurable`_ protocol.

        .. _Configurable: https://blueskyproject.io/bluesky/main/hardware.html#bluesky.protocols.Configurable
        """
        return {
            **{
                key: {"value": value, "timestamp": 0}
                for key, value in asdict(self).items()
                if key != "model_name"
            }
        }

    def describe_configuration(self) -> dict[str, Any]:
        """Describe the model information as a Bluesky configuration dictionary.

        Returns
        -------
        ``dict[str, Any]``
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
                    "source": "model_info",
                    "dtype": self.__type_map[type(value)],
                    "shape": self.__get_shape(value),
                }
                for key, value in asdict(self).items()
                if key != "model_name"
            }
        }


@define(kw_only=True)
class DetectorInfo(ModelInfo):
    """Detector model information class.

    Attributes
    ----------
    exposure : ``float``
        Initial exposure time for the detector.
    egu : ``str``
        Engineering unit for exposure time. Defaults to ``s``.
    sensor_shape : ``Tuple[int, int]``
        Shape of the detector sensor.
    pixel_size : ``Tuple[float, float, float]``
        Detector pixel size.
    timings: ``ListParameter``, optional
        Detector trigger informations. Optional
    """

    exposure: float = field(validator=validators.instance_of(float))
    egu: str = field(
        default="s", validator=validators.instance_of(str), on_setattr=setters.frozen
    )
    sensor_shape: Tuple[int, int] = field(converter=tuple, on_setattr=setters.frozen)
    pixel_size: Tuple[float, float, float] = field(converter=tuple)

    @sensor_shape.validator
    def _validate_sensor_shape(
        self, _: Attribute[Tuple[int, ...]], value: Tuple[int, ...]
    ) -> None:
        if not all(isinstance(val, int) for val in value):
            raise ValueError("All values in the tuple must be integers.")
        if len(value) != 2:
            raise ValueError("The tuple must contain exactly two values.")

    @pixel_size.validator
    def _validate_pixel_size(
        self, _: Attribute[Tuple[float, ...]], value: Tuple[float, ...]
    ) -> None:
        if not all(isinstance(val, float) for val in value):
            raise ValueError("All values in the tuple must be floats.")
        if len(value) != 3:
            raise ValueError("The tuple must contain exactly three values.")


@define(kw_only=True)
class MotorInfo(ModelInfo):
    """Motor model information class.

    Attributes
    ----------
    axis : ``list[str]``
        Motor axis names.
    step_size : ``float``
        Motor step size.
    egu : ``str``
        Engineering unit for motor position.
    """

    axis: list[str] = field(factory=list, on_setattr=setters.frozen)
    step_size: dict[str, float] = field(factory=dict)
    egu: str = field(validator=validators.instance_of(str), on_setattr=setters.frozen)

    @axis.validator
    def _validate_axis(self, _: str, value: list[str]) -> None:
        if not all(isinstance(val, str) for val in value):
            raise ValueError("All values in the list must be strings.")
        if len(value) == 0:
            raise ValueError("The list must contain at least one element.")

    @step_size.validator
    def _validate_step_size(self, _: str, value: dict[str, float]) -> None:
        if not all(isinstance(val, float) for val in value.values()):
            raise ValueError("All values in the dictionary must be floats.")
        if len(value) == 0:
            raise ValueError("The dictionary must contain at least one element.")


@define(kw_only=True)
class RedSunSessionInfo:
    """RedSun session configuration class.

    This class is used to store the configuration of a running RedSun application;
    it provides information about the hardware layout and the selected acquisition engine.

    A minimal configuration must include the selected acquisition engine.

    Attributes
    ----------
    engine : ``AcquisitionEngineTypes``
        Acquisition engine selected for the current session. Mandatory.
    frontend : ``FrontendTypes``
        Frontend selected for the current session. Defaults to ``FrontendTypes.QT``.
    controllers : ``dict[str, ControllerInfo]``
        Controller informations dictionary.
        Defaults to an empty dictionary.
    models : ``dict[str, ModelInfo]``
        Model informations dictionary.
        Defaults to an empty dictionary.
    """

    engine: AcquisitionEngineTypes = field(
        converter=AcquisitionEngineTypes,
        validator=validators.in_(AcquisitionEngineTypes),
        on_setattr=setters.frozen,
    )
    frontend: FrontendTypes = field(
        default=FrontendTypes.QT,
        converter=FrontendTypes,
        validator=validators.in_(FrontendTypes),
        on_setattr=setters.frozen,
    )
    controllers: dict[str, ControllerInfo] = field(factory=dict)
    models: dict[str, ModelInfo] = field(factory=dict)

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
        logger = get_logger()

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

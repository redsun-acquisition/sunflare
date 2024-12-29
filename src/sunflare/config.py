"""RedSun configuration dataclasses and enumerators.

The module provides a set of `pydantic.BaseModel`_ and enumerators classes that are used to
provide a basic representation of a RedSun-compatible hardware interface. These models are used in plugins to be inherited
by custom models defined by the user, which can provide additional information about specific hardware components.

.. _pydantic.BaseModel: https://docs.pydantic.dev/latest/concepts/models/

"""

from __future__ import annotations

from enum import Enum, unique
from pathlib import Path
from typing import Any, ClassVar, Tuple, Union

import yaml
from attrs import Attribute, define, field, validators
from psygnal import SignalGroupDescriptor

from sunflare.log import get_logger


@unique
class AcquisitionEngineTypes(str, Enum):
    """ 
    Supported acquisition engine entities.

    Acquisition engines are singleton objects that are instantiated within RedSun and operate
    as workflow managers for the acquisition process. They are responsible for the orchestration
    of the different hardware components currently loaded in RedSun. Accross the entire
    module there can be only one active acquisition engine at a time, otherwise RedSun will 
    raise an exception.

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


@unique
class DetectorModelTypes(str, Enum):
    """Supported detector types.

    Detectors are devices that are used to capture visualizable data.

    Attributes
    ----------
    AREA
        Area detector (i.e. CCD, CMOS cameras).
    LINE
        Line detector (i.e. photodiode arrays).
    POINT
        Point detector (i.e. Avalanche Photodiode (APD) detector).
    """

    AREA = "area"
    LINE = "line"
    POINT = "point"


@unique
class MotorModelTypes(str, Enum):
    """Supported motor types.

    This enumerator is used to provide a default categorization for the built-in user interface provided by RedSun,
    to facilitate the correct building of the application layout.

    Attributes
    ----------
    STEPPER
        Stepper motor.
    """

    STEPPER = "stepper"


@define(kw_only=True)
class ControllerInfo:
    """Controller information model.

    Attributes
    ----------
    controller_name : ``str``
        The constructor class used to instantiate the controller.
        It class must be a subclass of `BaseController`.
    """

    controller_name: str = field(validator=validators.instance_of(str))
    events: ClassVar[SignalGroupDescriptor] = SignalGroupDescriptor()


@define(kw_only=True)
class DeviceModelInfo:
    """Base model for device information.

    All device information models inherit from this class.

    Attributes
    ----------
    model_name : ``str``
        Device model name.
    vendor : ``str``, optional
        Detector vendor. Optional for visualization purposes.
    serial_number : ``str``, optional
        Detector serial number. Optional for visualization purposes.
    """

    model_name: str = field(validator=validators.instance_of(str))
    vendor: str = field(default="N/A", validator=validators.instance_of(str))
    serial_number: str = field(default="N/A", validator=validators.instance_of(str))


@define(kw_only=True)
class DetectorModelInfo(DeviceModelInfo):
    """Detector model informations.

    Attributes
    ----------
    category : DetectorModelTypes
        - Detector type.
    sensor_size : ``Tuple[int, int]``
        - Detector sensor size in pixels: represents the 2D axis ``(Y, X)``.
    pixel_size : ``Tuple[float, float, float]``
        - Detector pixel size in micrometers: represents the 3D axis ``(Z, Y, X)``.
        - Defaults to ``(1, 1, 1)``.
    exposure_egu : ``str``
        - Engineering unit for exposure time, e.g. ``ms``, ``μs``. Defaults to ``ms``.
    """

    category = field(default=DetectorModelTypes.AREA, converter=DetectorModelTypes)
    sensor_size: Tuple[int, int] = field(converter=tuple)
    pixel_size: Tuple[float, float, float] = field(
        default=(1.0, 1.0, 1.0), converter=tuple
    )
    exposure_egu: str = field(default="ms")
    events: ClassVar[SignalGroupDescriptor] = SignalGroupDescriptor()

    @sensor_size.validator
    def _validate_sensor_size(
        self, _: Attribute[Tuple[int, int]], value: Tuple[int, int]
    ) -> None:
        if len(value) != 2:
            raise ValueError("Sensor size must be a tuple of two (2) integers")
        if any([val == 0 for val in value]):
            raise ValueError("Sensor size cannot be zero")

    @pixel_size.validator
    def _validate_pixel_size(
        self,
        _: Attribute[Tuple[float, float, float]],
        value: Tuple[float, float, float],
    ) -> None:
        if len(value) != 3:
            raise ValueError("Pixel size must be a tuple of three (3) floats")
        if any([val <= 0 for val in value]):
            raise ValueError("Pixel size must be greater than zero")


@define(kw_only=True)
class MotorModelInfo(DeviceModelInfo):
    """Motor model informations.

    Attributes
    ----------
    category : MotorModelTypes
        - Motor type. Defaults to ``stepper``.
    step_egu : ``str``
        - Engineering unit for steps, e.g. ``mm``, ``μm``. Defaults to ``μm``.
    step_size : ``Union[int, float]``
        - Motor step size in ``step_egu`` units. Defaults to 1.0.
    axes : ``list[str]``
        - Supported motor axes.
        - Accepted values are single character, capital strings, e.g. ``['X', 'Y', 'Z']``.
    return_home : ``bool``
        - If ``True``, motor will return to home position
        - (defined as  the initial position the motor had at RedSun's startup)
        - after RedSun is closed. Defaults to ``False``.
    """

    category: MotorModelTypes = field(
        default=MotorModelTypes.STEPPER, validator=validators.in_(MotorModelTypes)
    )
    step_egu: str = field(default="μm")
    step_size: Union[int, float] = field(default=1.0)
    axes: list[str] = field(factory=lambda: list(), converter=list)
    return_home: bool = field(default=False)
    events: ClassVar[SignalGroupDescriptor] = SignalGroupDescriptor()

    @axes.validator
    def _validate_axes(self, _: Attribute[list[str]], value: list[str]) -> None:
        for axis in value:
            if (
                not isinstance(axis, str)
                or len(axis) != 1
                or not axis.isalpha()
                or not axis.isupper()
            ):
                raise ValueError(
                    "Motor axes must be a list of single character, capital strings"
                )


def _build_controller_info(values: dict[str, Any]) -> dict[str, ControllerInfo]:
    """Build a dictionary of ``ControllerInfo`` from a dictionary of values.

    Parameters
    ----------
    values : ``dict[str, Any]``
        A dictionary of controller values.

    Returns
    -------
    ``dict[str, ControllerInfo]``
        A dictionary of controllers.
    """
    return {name: ControllerInfo(**cfg_info) for name, cfg_info in values.items()}


def _build_detector_info(values: dict[str, Any]) -> dict[str, DetectorModelInfo]:
    """Build a dictionary of ``DetectorModelInfo`` from a dictionary of values.

    Parameters
    ----------
    values : ``dict[str, Any]``
        A dictionary of detector model values.

    Returns
    -------
    ``dict[str, DetectorModelInfo]``
        A dictionary of detector models.
    """
    return {name: DetectorModelInfo(**cfg_info) for name, cfg_info in values.items()}


def _build_motor_info(values: dict[str, Any]) -> dict[str, MotorModelInfo]:
    """Build a dictionary of ``MotorModelInfo`` from a dictionary of values.

    Parameters
    ----------
    values : ``dict[str, Any]``
        A dictionary of motor model values.

    Returns
    -------
    ``dict[str, MotorModelInfo]``
        A dictionary of motor models.
    """
    return {name: MotorModelInfo(**cfg_info) for name, cfg_info in values.items()}


@define(kw_only=True)
class RedSunInstanceInfo:
    """RedSun instance configuration class.

    This class is used to store the configuration of a running RedSun application;
    it provides information about the hardware layout and the selected acquisition engine.
    All hardware models must be coherent with the selected acquisition engine.

    A minimal configuration should include the selected acquisition engine.

    Attributes
    ----------
    engine : ``AcquisitionEngineTypes``
        Acquisition engine selected for the current instance. Mandatory.
    frontend : ``FrontendTypes``
        Frontend selected for the current instance. Defaults to ``FrontendTypes.QT``.
    controllers : ``dict[str, ControllerInfo]``
        Controller informations dictionary.
        Defaults to an empty dictionary.
    detectors : ``dict[str, DetectorModelInfo]``
        Detector model informations dictionary.
        Defaults to an empty dictionary.
    motors : ``dict[str, MotorModelInfo]``
        Motor model informations dictionary.
        Defaults to an empty dictionary.
    """

    engine: AcquisitionEngineTypes = field(
        converter=AcquisitionEngineTypes,
        validator=validators.in_(AcquisitionEngineTypes),
    )
    frontend: FrontendTypes = field(
        default=FrontendTypes.QT,
        converter=FrontendTypes,
        validator=validators.in_(FrontendTypes),
    )
    controllers: dict[str, ControllerInfo] = field(
        factory=dict, converter=_build_controller_info
    )
    detectors: dict[str, DetectorModelInfo] = field(
        factory=dict, converter=_build_detector_info
    )
    motors: dict[str, MotorModelInfo] = field(factory=dict, converter=_build_motor_info)

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

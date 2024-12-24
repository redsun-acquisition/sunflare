"""RedSun configuration dataclasses and enumerators.

The module provides a set of `pydantic.BaseModel`_ and enumerators classes that are used to
provide a basic representation of a RedSun-compatible hardware interface. These models are used in plugins to be inherited
by custom models defined by the user, which can provide additional information about specific hardware components.

.. _pydantic.BaseModel: https://docs.pydantic.dev/latest/concepts/models/

"""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Any, ClassVar, Optional, Tuple, Union

import yaml
from psygnal import SignalGroupDescriptor
from pydantic import BaseModel, ConfigDict, Field

from sunflare.log import get_logger


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


class FrontendTypes(str, Enum):
    """Supported frontend types.

    Frontends are the supported GUI frameworks that are used to interact with the user.

    Attributes
    ----------
    QT
        Qt frontend.
    """

    QT = "qt"


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


class LightModelTypes(str, Enum):
    """Supported light source types.

    Attributes
    ----------
    LASER
        Laser light source.
    """

    LASER = "laser"


class ScannerModelTypes(str, Enum):
    """Supported scanner types.

    Attributes
    ----------
    GALVO
        Galvanometric scanner.
    """

    GALVO = "galvo"


class ControllerTypes(str, Enum):
    """Supported controller category types.

    Attributes
    ----------
    DEVICE
        Device controller.

        - These are only used internally and not exposed to the user.
    COMPUTATOR
        Renderer controller.
    PUBLISHER
        Publisher controller.
    MONITORER
        Monitorer controller.
    """

    DEVICE = "device"
    RENDERER = "renderer"
    PUBLISHER = "publisher"
    MONITORER = "monitorer"


class ControllerInfo(BaseModel):
    """Controller information model.

    Attributes
    ----------
    category : ``set[ControllerTypes]``
        Set of controller categories.
    controller_name : ``str``
        Controller name.
    """

    category: set[ControllerTypes] = Field(default=set())
    controller_name: str = Field(default=str())
    events: ClassVar[SignalGroupDescriptor] = SignalGroupDescriptor()

    # private field; it is used to bypass validation
    # in order to build device controllers internally
    _bypass: bool = False


class DeviceModelInfo(BaseModel):
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

    model_name: str = Field(description="Device model name")
    vendor: str = Field(default="N/A", description="Device vendor name")
    serial_number: str = Field(default="N/A", description="Device serial number")

    # needed to suppress the warning about the protected namespace
    model_config = ConfigDict(protected_namespaces=("model_config",))


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

    category: DetectorModelTypes = Field(default=DetectorModelTypes.AREA)
    sensor_size: Tuple[int, int] = Field(default_factory=lambda: (0, 0))
    pixel_size: Tuple[float, float, float] = Field(
        default_factory=lambda: (1.0, 1.0, 1.0)
    )
    exposure_egu: str = Field(default="ms")
    events: ClassVar[SignalGroupDescriptor] = SignalGroupDescriptor()


class LightModelInfo(DeviceModelInfo):
    r"""Light source model informations.

    .. warning:: This class is currently under active development and may see breaking changes. It is not yet
        fully implemented and may not be used in production.

    Attributes
    ----------
    category : LightModelTypes
        - Light source type. Defaults to ``laser``.
    wavelength : ``int``, optional
        - Light source wavelength in nanometers.
    power_egu : ``str``
        - Engineering unit for light source, .e.g. ``mW``, ``μW``. Defaults to ``mW``.
    range : ``Union[Tuple[float, float], Tuple[int, int]]``
        - Light source power range. Expressed in `power_egu` units.
        - Formatted as (min, max). Defaults to ``(0, 0)``.
    power_step: ``Union[float, int]``
        - Power increase/decrease minimum step size. Expressed in ``power_egu`` units.
    """

    power_egu: str = Field(default="mW")
    wavelength: Optional[int] = Field(default=None)
    category: LightModelTypes = Field(default=LightModelTypes.LASER)
    range: Union[Tuple[float, float], Tuple[int, int]] = Field(
        default_factory=lambda: (0, 0)
    )
    power_step: Union[float, int] = Field(default=0)
    events: ClassVar[SignalGroupDescriptor] = SignalGroupDescriptor()


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
        - Suggested values are single character, capital strings, e.g. ``['X', 'Y', 'Z']``.
    return_home : ``bool``
        - If ``True``, motor will return to home position
        - (defined as  the initial position the motor had at RedSun's startup)
        - after RedSun is closed. Defaults to ``False``.
    """

    category: MotorModelTypes = Field(default=MotorModelTypes.STEPPER)
    step_egu: str = Field(default="μm")
    step_size: Union[int, float] = Field(default=1.0)
    axes: list[str] = Field(default_factory=lambda: list())
    return_home: bool = Field(default=False)
    events: ClassVar[SignalGroupDescriptor] = SignalGroupDescriptor()


class ScannerModelInfo(DeviceModelInfo):
    """Scanner model informations.

    .. warning:: This class is currently under active development and may see breaking changes. It is not yet
        fully implemented and may not be used in production.

    Attributes
    ----------
    category : ScannerModelTypes
        - Scanner type. Defaults to ``galvo``.
    axes : ``list[str]``
        - Supported scanner axes. Suggestion is to be a list of
        - single character, capital strings, e.g. ``['X', 'Y', 'Z']``.
    """

    category: ScannerModelTypes = Field(default=ScannerModelTypes.GALVO)
    axes: list[str] = Field(default_factory=list)
    # TODO: investigate what other parameters are needed for scanner
    events: ClassVar[SignalGroupDescriptor] = SignalGroupDescriptor()


class RedSunInstanceInfo(BaseModel):
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

    engine: AcquisitionEngineTypes
    frontend: FrontendTypes = Field(default=FrontendTypes.QT)
    controllers: dict[str, ControllerInfo] = Field(default_factory=lambda: dict())
    detectors: dict[str, DetectorModelInfo] = Field(default_factory=lambda: dict())
    motors: dict[str, MotorModelInfo] = Field(default_factory=lambda: dict())

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
        dict[str, Any]
            A dictionary containing the configuration data.

        Raises
        ------
        FileNotFoundError
            If the file does not exist.
        ValueError
            If the file is not a YAML file.
        yaml.YAMLError
            If an error occurs while loading the file.
        """
        logger = get_logger()

        path_obj = Path(path)

        if not path_obj.is_absolute():
            path_obj = path_obj.resolve()

        if not path_obj.exists():
            logger.error(f"The file {path} does not exist.")
            raise FileNotFoundError(f"The file {path} does not exist.")

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
            raise e(f"Error loading YAML file {path}: {e}")

        return data

    @classmethod
    def from_yaml(cls, path: str) -> RedSunInstanceInfo:
        """Build the RedSun instance configuration from a YAML file.

        Parameters
        ----------
        path : ``str``
            Path to the YAML file.

        Returns
        -------
        RedSunInstanceInfo
            RedSun instance configuration.
        """
        data = cls.load_yaml(path)
        return cls(**data)

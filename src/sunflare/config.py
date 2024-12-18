"""RedSun configuration dataclasses and enums."""

from __future__ import annotations

from enum import Enum
from typing import Optional, Tuple, Union, ClassVar

from psygnal import SignalGroupDescriptor

from pydantic import Field, BaseModel, ConfigDict


class AcquisitionEngineTypes(str, Enum):
    r""" 
    Supported acquisition engine entities.

    Acquisition engines are singleton objects that are instantiated within RedSun and operate
    as workflow managers for the acquisition process. They are responsible for the orchestration
    of the different hardware components currently loaded in RedSun. Accross the entire
    module there can be only one active acquisition engine at a time, otherwise RedSun will 
    raise an exception.

    Attributes
    ----------
    BLUESKY: str
        Bluesky: a Python-based data acquisition framework for scientific experiments. \
        For more informations, refer to the `Bluesky documentation page<https://blueskyproject.io/bluesky/index.html>`_.
    """

    BLUESKY: str = "bluesky"


class FrontendTypes(str, Enum):
    """Supported frontend types.

    Frontends are the supported GUI frameworks that are used to interact with the user.

    Attributes
    ----------
    QT : str
        Qt frontend.
    """

    QT: str = "qt"


class DetectorModelTypes(str, Enum):
    """Supported detector types.

    Detectors are devices that are used to capture images or signals from the sample.

    Attributes
    ----------
    AREA : str
        Area detector (i.e. CCD, CMOS cameras).
    LINE : str
        Line detector (i.e. photodiode arrays).
    POINT : str
        Point detector (i.e. Avalanche Photodiode (APD) detector).
    """

    AREA: str = "area"
    LINE: str = "line"
    POINT: str = "point"


class PixelPhotometricTypes(str, Enum):
    """Supported pixel photometric types.

    Attributes
    ----------
    GRAY : str
        Gray scale pixel.
    RGB : str
        RGB pixel.
    """

    GRAY: str = "gray"
    RGB: str = "rgb"


class MotorModelTypes(str, Enum):
    """Supported motor types.

    Attributes
    ----------
    STEPPER : str
        Stepper motor.
    """

    STEPPER: str = "stepper"


class LightModelTypes(str, Enum):
    """Supported light source types.

    Attributes
    ----------
    LASER : str
        Laser light source.
    """

    LASER: str = "laser"


class ScannerModelTypes(str, Enum):
    """Supported scanner types.

    Attributes
    ----------
    GALVO : str
        Galvanometric scanner.
    """

    GALVO: str = "galvo"


class ControllerTypes(str, Enum):
    r"""Supported controller category types.

    Attributes
    ----------
    DEVICE : str
        Device controller. \
        These are only used internally and not exposed to the user.
    COMPUTATOR : str
        Computator controller.
    PUBLISHER : str
        Publisher controller.
    MONITORER : str
        Monitorer controller.
    """

    DEVICE: str = "device"
    COMPUTATOR: str = "computator"
    PUBLISHER: str = "publisher"
    MONITORER: str = "monitorer"


class ControllerInfo(BaseModel):
    """Controller information model.

    Attributes
    ----------
    category : Set[ControllerTypes]
        Set of controller categories.
    controller_name : str
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

    Attributes
    ----------
    model_name : str
        Device model name.
    vendor : Optional[str]
        Detector vendor. Optional for debugging purposes.
    serial_number : Optional[str]
        Detector serial number. Optional for debugging purposes.
    """

    model_name: str = Field(default=str())
    vendor: str = Field(default="N/A", description="Device vendor name")
    serial_number: str = Field(default="N/A", description="Device serial number")

    # needed to suppress the warning about the protected namespace
    model_config = ConfigDict(protected_namespaces=("model_config",))


class DetectorModelInfo(DeviceModelInfo):
    """Detector model informations.

    Attributes
    ----------
    category : DetectorModelTypes
        Detector type. Currently supported values are
        'area', 'line' and 'point'. Defaults to 'area'.
    sensor_size: Tuple[int]
        Detector sensor size in pixels: represents the 2D axis (Y, X).
    pixel_size : Tuple[float]
        Detector pixel size in micrometers: represents the 3D axis (Z, Y, X).
        Defaults to `(1, 1, 1)`.
    exposure_egu : str
        Engineering unit for exposure time, e.g. 'ms', 'μs'. Defaults to 'ms'.
    """

    category: str = Field(default=DetectorModelTypes.AREA)
    sensor_size: Tuple[int, int] = Field(default_factory=lambda: (0, 0))
    pixel_size: Tuple[float, float, float] = Field(
        default_factory=lambda: (1.0, 1.0, 1.0)
    )
    exposure_egu: str = Field(default="ms")
    events: ClassVar[SignalGroupDescriptor] = SignalGroupDescriptor()


class LightModelInfo(DeviceModelInfo):
    r"""Light source model informations.

    Attributes
    ----------
    category : LightModelTypes
        Light source type. Defaults to 'laser'.
    wavelength : int
        Light source wavelength in nanometers.
    power_egu : str
        Engineering unit for light source, .e.g. 'mW', 'μW'. Defaults to 'mW'.
    range : Union[Tuple[float, float], Tuple[int, int]]
        Light source power range. Expressed in `power_egu` units.
        Formatted as (min, max). Defaults to (0, 0).
    power_step: Union[float, int]
        Power increase/decrease minimum step size. Expressed in `power_egu` units.
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
        Motor type. Defaults to 'stepper'.
    step_egu : str
        Engineering unit for steps, e.g. 'mm', 'μm'. Defaults to 'μm'.
    step_size : Union[int, float]
        Motor step size in `step_egu` units. Defaults to 1.0.
    axes : list[str]
        Supported motor axes. Suggestion is to be a list of
        single character, capital strings, e.g. ['X', 'Y', 'Z'].
    return_home : bool
        If `True`, motor will return to home position
        (defined as  the initial position the motor had at RedSun's startup)
        after RedSun is closed. Defaults to `False`.
    """

    category: MotorModelTypes = Field(default=MotorModelTypes.STEPPER)
    step_egu: str = Field(default="μm")
    step_size: Union[int, float] = Field(default=1.0)
    axes: list[str] = Field(default_factory=lambda: list())
    return_home: bool = Field(default=False)
    events: ClassVar[SignalGroupDescriptor] = SignalGroupDescriptor()


class ScannerModelInfo(DeviceModelInfo):
    """Scanner model informations.

    Attributes
    ----------
    category : ScannerModelTypes
        Scanner type. Defaults to 'galvo'.
    axes : list[str]
        Supported scanner axes. Suggestion is to be a list of
        single character, capital strings, e.g. ['X', 'Y', 'Z'].
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
    engine : AcquisitionEngineTypes
        Acquisition engine selected for the current instance.
    controllers : Optional[Dict[str, ControllerInfo]]
        Controller informations dictionary.
        Defaults to an empty dictionary.
    detectors : Optional[Dict[str, DetectorModelInfo]]
        Detector model informations dictionary.
        Defaults to an empty dictionary.
    lights : Optional[Dict[str, LightModelInfo]]
        Light source model informations dictionary.
        Defaults to an empty dictionary.
    motors : Optional[Dict[str, MotorModelInfo]]
        Motor model informations dictionary.
        Defaults to an empty dictionary.
    scanners : Optional[Dict[str, ScannerModelInfo]]
        Scanner model informations dictionary.
        Defaults to an empty dictionary.
    """

    engine: AcquisitionEngineTypes = Field(default=AcquisitionEngineTypes.BLUESKY)
    frontend: FrontendTypes = Field(default=FrontendTypes.QT)
    controllers: dict[str, ControllerInfo] = Field(default_factory=lambda: dict())
    detectors: dict[str, DetectorModelInfo] = Field(default_factory=lambda: dict())
    lights: dict[str, LightModelInfo] = Field(default_factory=lambda: dict())
    motors: dict[str, MotorModelInfo] = Field(default_factory=lambda: dict())
    scanners: dict[str, ScannerModelInfo] = Field(default_factory=lambda: dict())

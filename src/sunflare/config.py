"""RedSun configuration dataclasses and enums."""

from enum import Enum
from typing import Any, Optional, Tuple, Union

from pydantic import Field, BaseModel


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
    EXENGINE : str
        ExEngine: execution engine for microscopy control.\\
        For more informations, refer to the `ExEngine documentation page<https://exengine.readthedocs.io/en/latest/index.html>`_
    """

    EXENGINE: str = "exengine"


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
    """Supported controller category types.

    Attributes
    ----------
    DEVICE : str
        Device controllers are used to expose lower hardware devices of the same type (e.g. motors, detectors, etc.) with a unique interface to facilitate
        the interaction with the acquisition engine and the upper layers. They do not provide computational capabilities other than the ones needed to interact with
        the hardware (i.e. compute motor steps or update detector exposure time).
    COMPUTATIONAL : str
        Computational controllers provide computational resources or define workflows that are independent of specific hardware devices and can inform
        the acquisition engine of a new workflow that can be injected into the acquisition process.
    """

    DEVICE: str = "device"
    COMPUTATIONAL: str = "computational"


class ControllerInfo(BaseModel):
    """Controller information model.

    Attributes
    ----------
    category : ControllerTypes
        Controller category. Defaults to 'device'.
    controllerName : str
        Controller name.
    supportedEngines : list[AcquisitionEngineTypes]
        Supported acquisition engines list. Defaults to ['exengine'].
    controllerParams : Dict[str, Any]
        Controller parameters dictionary. Used to store start-up configuration parameters.
        - They are exposed to the upper layers to allow the user to configure the controller at runtime.
    """

    category: ControllerTypes = Field(default=ControllerTypes.DEVICE)
    controllerName: str = Field(default=str())
    supportedEngines: list[AcquisitionEngineTypes] = Field(
        default_factory=lambda: [AcquisitionEngineTypes.EXENGINE]
    )
    controllerParams: dict[str, Any] = Field(default_factory=dict)


class DeviceModelInfo(BaseModel):
    """Base model for device information.

    Attributes
    ----------
    modelName : str
        Device model name.
    modelParams : Dict[str, Union[str, int, float]]
        Device model parameters dictionary. Used to store start-up configuration parameters.
    supportedEngines : list[AcquisitionEngineTypes]
        Supported acquisition engines list.
    vendor : Optional[str]
        Detector vendor. Optional for debugging purposes.
    serialNumber : Optional[str]
        Detector serial number. Optional for debugging purposes.
    """

    modelName: str
    modelParams: dict[str, Union[str, int, float]]
    supportedEngines: list[AcquisitionEngineTypes] = Field(
        default_factory=lambda: [AcquisitionEngineTypes.EXENGINE]
    )
    vendor: Optional[str] = Field(default="N/A", description="Device vendor name")
    serialNumber: Optional[str] = Field(
        default="N/A", description="Device serial number"
    )


class DetectorModelInfo(DeviceModelInfo):
    """Detector model informations.

    Attributes
    ----------
    category : DetectorModelTypes
        Detector type. Currently supported values are
        'area', 'line' and 'point'. Defaults to 'area'.
    sensorSize: Tuple[int]
        Detector sensor size in pixels: represents the 2D axis (Y, X).
    pixelSize : Tuple[float]
        Detector pixel size in micrometers: represents the 3D axis (Z, Y, X).
        Defaults to `(1, 1, 1)`.
    exposureEGU : str
        Engineering unit for exposure time, e.g. 'ms', 'μs'. Defaults to 'ms'.
    """

    category: str = Field(default=DetectorModelTypes.AREA)
    sensorSize: Tuple[int, int] = Field(default_factory=lambda: (0, 0))
    pixelSize: Tuple[float, float, float] = Field(default_factory=lambda: (1, 1, 1))
    exposureEGU: str = Field(default="ms")


class LightModelInfo(DeviceModelInfo):
    """Light source model informations.

    Attributes
    ----------
    category : LightModelTypes
        Light source type. Defaults to 'laser'.
    wavelength : int
        Light source wavelength in nanometers.
    powerEGU : str
        Engineering unit for light source, .e.g. 'mW', 'μW'. Defaults to 'mW'.
    minPower : Union[float, int]
        Minimum light source power.
    maxPower : Union[float, int]
        Maximum light source power.
    powerStep: Union[float, int]
        Power increase/decrease minimum step size.
    """

    powerEGU: str = Field(default="mW")
    wavelength: int
    category: LightModelTypes = Field(default=LightModelTypes.LASER)
    minPower: Union[float, int]
    maxPower: Union[float, int]
    powerStep: Union[float, int]


class MotorModelInfo(DeviceModelInfo):
    """Motor model informations.

    Attributes
    ----------
    category : MotorModelTypes
        Motor type. Defaults to 'stepper'.
    stepEGU : str
        Engineering unit for steps, e.g. 'mm', 'μm'. Defaults to 'μm'.
    axes : list[str]
        Supported motor axes. Suggestion is to be a list of
        single character, capital strings, e.g. ['X', 'Y', 'Z'].
    returnHome : bool
        If `True`, motor will return to home position
        (defined as  the initial position the motor had at RedSun's startup)
        after RedSun is closed. Defaults to `False`.
    """

    category: str = Field(default=MotorModelTypes.STEPPER)
    stepEGU: str = Field(default="μm")
    axes: list[str] = Field(default_factory=list)
    returnHome: bool = Field(default=False)


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

    category: ScannerModelTypes = ScannerModelTypes.GALVO
    axes: list[str] = Field(default_factory=list)
    # TODO: investigate what other parameters are needed for scanner


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
        Defaults to 'exengine'.
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

    engine: "AcquisitionEngineTypes" = AcquisitionEngineTypes.EXENGINE
    controllers: "Optional[dict[str, ControllerInfo]]" = Field(default_factory=dict)
    detectors: "Optional[dict[str, DetectorModelInfo]]" = Field(default_factory=dict)
    lights: "Optional[dict[str, LightModelInfo]]" = Field(default_factory=dict)
    motors: "Optional[dict[str, MotorModelInfo]]" = Field(default_factory=dict)
    scanners: "Optional[dict[str, ScannerModelInfo]]" = Field(default_factory=dict)

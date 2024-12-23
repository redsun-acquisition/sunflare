import os
import yaml

from sunflare.config import RedSunInstanceInfo, DetectorModelInfo, MotorModelInfo
from sunflare.engine.detector import DetectorModel
from sunflare.engine.motor import MotorModel

class MockDetectorModel(DetectorModel[DetectorModelInfo]):
    """Mock detector model."""

    def __init__(self, name: str, cfg_info: DetectorModelInfo) -> None:
        super().__init__(name, cfg_info)

    def shutdown(self) -> None:
        """Shutdown the detector."""
        ...

class MockMotorModel(MotorModel[MotorModelInfo]):
    """Mock motor model."""

    def __init__(self, name: str, cfg_info: MotorModelInfo) -> None:
        super().__init__(name, cfg_info)
    
    def shutdown(self) -> None:
        """Shutdown the motor."""
        ...

def test_detector_model(config_path: str) -> None:
    """Test the detector model info."""

    truth_dict = {
        "First mock detector": {
            "model_name": "MockDetectorModel",
        },
        "Second mock detector": {
            "model_name": "MockDetectorModel",
            "category": "line",
            "exposure_egu": "s",
        },
    }

    truth_configs = {
        name: DetectorModelInfo(**cfg_info)
        for name, cfg_info in truth_dict.items()
    }

    config_file = os.path.join(config_path, "detector_instance.yaml")
    config_dict = yaml.safe_load(open(config_file))
    instance = RedSunInstanceInfo(**config_dict)

    for (name, cfg_info), (truth_name, truth_cfg_info) in zip(instance.detectors.items(), truth_configs.items()):
        detector = MockDetectorModel(name=name, cfg_info=cfg_info)
        assert detector.name == truth_name
        assert detector.model_name == truth_cfg_info.model_name
        assert detector.model_info == truth_cfg_info
        assert detector.vendor == truth_cfg_info.vendor
        assert detector.serial_number == truth_cfg_info.serial_number
        assert detector.category == truth_cfg_info.category
        assert detector.sensor_size == truth_cfg_info.sensor_size
        assert detector.pixel_size == truth_cfg_info.pixel_size
        detector.shutdown()

def test_motor_model(config_path: str) -> None:
    """Test the motor model info."""

    truth_dict = {
        "Single axis motor": {
            "model_name": "MockMotorModel",
            "axes": ["X"],
        },
        "Double axis motor": {
            "model_name": "MockMotorModel",
            "axes": ["X", "Y"],
            "step_egu": "mm",
        },
    }

    truth_configs = {
        name: MotorModelInfo(**cfg_info)
        for name, cfg_info in truth_dict.items()
    }

    config_file = os.path.join(config_path, "motor_instance.yaml")
    config_dict = yaml.safe_load(open(config_file))
    instance = RedSunInstanceInfo(**config_dict)

    for (name, cfg_info), (truth_name, truth_cfg_info) in zip(instance.motors.items(), truth_configs.items()):
        motor = MockMotorModel(name=name, cfg_info=cfg_info)
        assert motor.name == truth_name
        assert motor.model_name == truth_cfg_info.model_name
        assert motor.model_info == truth_cfg_info
        assert motor.vendor == truth_cfg_info.vendor
        assert motor.serial_number == truth_cfg_info.serial_number
        assert motor.category == truth_cfg_info.category
        assert motor.axes == truth_cfg_info.axes
        assert motor.step_egu == truth_cfg_info.step_egu
        motor.shutdown()

def test_multi_model(config_path: str) -> None:
    """Test the multi model info."""

    truth_dict = {
        "First mock detector": {
            "model_name": "MockDetectorModel",
        },
        "Second mock detector": {
            "model_name": "MockDetectorModel",
            "category": "line",
            "exposure_egu": "s",
        },
        "Single axis motor": {
            "model_name": "MockMotorModel",
            "axes": ["X"],
        },
        "Double axis motor": {
            "model_name": "MockMotorModel",
            "axes": ["X", "Y"],
            "step_egu": "mm",
        },
    }

    truth_config_detectors = {
        name: DetectorModelInfo(**cfg_info)
        for name, cfg_info in truth_dict.items() if "Detector" in cfg_info["model_name"]
    }

    truth_configs_motors = {
        name: MotorModelInfo(**cfg_info)
        for name, cfg_info in truth_dict.items() if "Motor" in cfg_info["model_name"]
    }

    config_file = os.path.join(config_path, "multi_model_instance.yaml")
    config_dict = yaml.safe_load(open(config_file))
    instance = RedSunInstanceInfo(**config_dict)

    for (name, cfg_info), (truth_name, truth_cfg_info) in zip(instance.detectors.items(), truth_config_detectors.items()):
        detector = MockDetectorModel(name=name, cfg_info=cfg_info)
        assert detector.name == truth_name
        assert detector.model_name == truth_cfg_info.model_name
        assert detector.model_info == truth_cfg_info
        assert detector.vendor == truth_cfg_info.vendor
        assert detector.serial_number == truth_cfg_info.serial_number
        assert detector.category == truth_cfg_info.category
        assert detector.sensor_size == truth_cfg_info.sensor_size
        assert detector.pixel_size == truth_cfg_info.pixel_size
        detector.shutdown()
    
    for (name, cfg_info), (truth_name, truth_cfg_info) in zip(instance.motors.items(), truth_configs_motors.items()):
        motor = MockMotorModel(name=name, cfg_info=cfg_info)
        assert motor.name == truth_name
        assert motor.model_name == truth_cfg_info.model_name
        assert motor.model_info == truth_cfg_info
        assert motor.vendor == truth_cfg_info.vendor
        assert motor.serial_number == truth_cfg_info.serial_number
        assert motor.category == truth_cfg_info.category
        assert motor.axes == truth_cfg_info.axes
        assert motor.step_egu == truth_cfg_info.step_egu
        motor.shutdown()

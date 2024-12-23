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
        assert detector.name == truth_name
        assert detector.model_info == truth_cfg_info
        assert detector.vendor == truth_cfg_info.vendor
        assert detector.serial_number == truth_cfg_info.serial_number
        assert detector.category == truth_cfg_info.category
        assert detector.sensor_size == truth_cfg_info.sensor_size
        assert detector.pixel_size == truth_cfg_info.pixel_size
        detector.shutdown()

def test_motor_model(config_path: str) -> None:
    """Test the motor model info."""

    config_file = os.path.join(config_path, "motor_instance.yaml")
    config_dict = yaml.safe_load(open(config_file))
    instance = RedSunInstanceInfo(**config_dict)

    for name, cfg_info in instance.motors.items():
        motor = MockMotorModel(name=name, cfg_info=cfg_info)
        assert motor.name == name
        assert motor.model_info == cfg_info
        assert motor.vendor == cfg_info.vendor
        assert motor.serial_number == cfg_info.serial_number
        assert motor.category == cfg_info.category
        assert motor.axes == cfg_info.axes
        motor.shutdown()

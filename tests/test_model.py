import os
import yaml

import pytest

from typing import Any

from sunflare.config import DetectorModelInfo, MotorModelInfo, RedSunInstanceInfo
from mocks import MockDetectorModel, MockMotorModel

def test_detector_model(config_path: str) -> None:
    """Test the detector model info."""

    truth_dict: dict[str, Any] = {
        "First mock detector": {
            "model_name": "MockDetectorModel",
            "sensor_size": [10, 10],
        },
        "Second mock detector": {
            "model_name": "MockDetectorModel",
            "sensor_size": [10, 10],
            "category": "line",
            "exposure_egu": "s",
        },
    }

    truth_configs: dict[str, DetectorModelInfo] = {
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

def test_broken_detector_model() -> None:
    """Test the detector model info."""

    test_config: dict[str, Any] = {
        "model_name": "MockDetectorModel",
        "sensor_size": [10, 10, 100],
        "pixel_size": [1, 1, 1]
    }

    with pytest.raises(ValueError):
        DetectorModelInfo(**test_config)
    
    test_config = {
        "model_name": "MockDetectorModel",
        "sensor_size": [0, 10],
        "pixel_size": [1, 1, 1]
    }

    with pytest.raises(ValueError):
        DetectorModelInfo(**test_config)
    
    test_config = {
        "model_name": "MockDetectorModel",
        "sensor_size": [10, 10],
        "pixel_size": [1, 1]
    }

    with pytest.raises(ValueError):
        DetectorModelInfo(**test_config)
    
    test_config = {
        "model_name": "MockDetectorModel",
        "sensor_size": [10, 10],
        "pixel_size": [0, 1, 1]
    }

    with pytest.raises(ValueError):
        DetectorModelInfo(**test_config)

def test_broken_motor_model() -> None:
    test_config: dict[str, Any] = {
        "model_name": "MockMotorModel",
        "axes": [1, 2]
    }

    with pytest.raises(ValueError):
        MotorModelInfo(**test_config)
    
    test_config = {
        "model_name": "MockMotorModel",
        "axes": ["x", "a", "b"]
    }

    with pytest.raises(ValueError):
        MotorModelInfo(**test_config)

def test_motor_model(config_path: str) -> None:
    """Test the motor model info."""

    truth_dict: dict[str, Any] = {
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
    instance = RedSunInstanceInfo(**yaml.safe_load(open(config_file)))

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

    truth_dict: dict[str, Any] = {
        "First mock detector": {
            "model_name": "MockDetectorModel",
            "sensor_size": [10, 10],
        },
        "Second mock detector": {
            "model_name": "MockDetectorModel",
            "sensor_size": [10, 10],
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


    truth_config_detectors: dict[str, DetectorModelInfo] = {
        name: DetectorModelInfo(**cfg_info)
        for name, cfg_info in truth_dict.items() if "Detector" in cfg_info["model_name"]
    }

    truth_configs_motors: dict[str, MotorModelInfo] = {
        name: MotorModelInfo(**cfg_info)
        for name, cfg_info in truth_dict.items() if "Motor" in cfg_info["model_name"]
    }

    config_file = os.path.join(config_path, "multi_model_instance.yaml")
    instance = RedSunInstanceInfo(**yaml.safe_load(open(config_file)))

    for (name, det_info), (truth_name, det_cfg_info) in zip(instance.detectors.items(), truth_config_detectors.items()):
        detector = MockDetectorModel(name=name, cfg_info=det_info)
        assert detector.name == truth_name
        assert detector.model_name == det_cfg_info.model_name
        assert detector.model_info == det_cfg_info
        assert detector.vendor == det_cfg_info.vendor
        assert detector.serial_number == det_cfg_info.serial_number
        assert detector.category == det_cfg_info.category
        assert detector.sensor_size == det_cfg_info.sensor_size
        assert detector.pixel_size == det_cfg_info.pixel_size
        detector.shutdown()
    
    for (name, mot_info), (truth_name, mot_cfg_info) in zip(instance.motors.items(), truth_configs_motors.items()):
        motor = MockMotorModel(name=name, cfg_info=mot_info)
        assert motor.name == truth_name
        assert motor.model_name == mot_cfg_info.model_name
        assert motor.model_info == mot_cfg_info
        assert motor.vendor == mot_cfg_info.vendor
        assert motor.serial_number == mot_cfg_info.serial_number
        assert motor.category == mot_cfg_info.category
        assert motor.axes == mot_cfg_info.axes
        assert motor.step_egu == mot_cfg_info.step_egu
        motor.shutdown()

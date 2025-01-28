import os
import yaml

import pytest

from typing import Any, cast
from attrs import asdict

from sunflare.config import RedSunSessionInfo
from mocks import MockDetector, MockMotor, MockDetectorInfo, MockMotorInfo

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
            "exposure_egu": "s",
        },
    }

    truth_configs: dict[str, MockDetectorInfo] = {
        name: MockDetectorInfo(**cfg_info)
        for name, cfg_info in truth_dict.items()
    }

    config_file = os.path.join(config_path, "detector_instance.yaml")
    config_dict = yaml.safe_load(open(config_file))

    config_dict["models"] = {
        name : MockDetectorInfo(**info) for name, info in config_dict["models"].items()
    }

    session = RedSunSessionInfo(**config_dict)

    for (name, cfg_info), (truth_name, truth_cfg_info) in zip(session.models.items(), truth_configs.items()):
        cfg = cast(MockDetectorInfo, cfg_info)
        detector = MockDetector(name=name, cfg_info=cfg)
        assert detector.name == truth_name
        assert detector.parent is None
        assert detector.model_info == truth_cfg_info

def test_broken_detector_model() -> None:
    """Test the detector model info."""

    test_config: dict[str, Any] = {
        "model_name": "MockDetectorModel",
        "sensor_size": [10, 10, 100],
        "pixel_size": [1, 1, 1]
    }

    with pytest.raises(ValueError):
        MockDetectorInfo(**test_config)
    
    test_config = {
        "model_name": "MockDetectorModel",
        "sensor_size": [0, 10],
        "pixel_size": [1, 1, 1]
    }

    with pytest.raises(ValueError):
        MockDetectorInfo(**test_config)
    
    test_config = {
        "model_name": "MockDetectorModel",
        "sensor_size": [10, 10],
        "pixel_size": [1, 1]
    }

    with pytest.raises(ValueError):
        MockDetectorInfo(**test_config)
    
    test_config = {
        "model_name": "MockDetectorModel",
        "sensor_size": [10, 10],
        "pixel_size": [0, 1, 1]
    }

    with pytest.raises(ValueError):
        MockDetectorInfo(**test_config)

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
        name: MockMotorInfo(**cfg_info)
        for name, cfg_info in truth_dict.items()
    }

    config_file = os.path.join(config_path, "motor_instance.yaml")
    config_dict = RedSunSessionInfo.load_yaml(config_file)
    config_dict["models"] = {
        name : MockMotorInfo(**info) for name, info in config_dict["models"].items()
    }
    session = RedSunSessionInfo(**config_dict)

    for (name, cfg_info), (truth_name, truth_cfg_info) in zip(session.models.items(), truth_configs.items()):
        cfg = cast(MockMotorInfo, cfg_info)
        motor = MockMotor(name=name, cfg_info=cfg)
        assert motor.name == truth_name
        assert motor.parent is None
        assert motor.model_info == truth_cfg_info

def test_broken_motor_model() -> None:
    test_config: dict[str, Any] = {
        "model_name": "MockMotor",
        "axes": [1, 2]
    }

    with pytest.raises(ValueError):
        MockMotorInfo(**test_config)
    
    test_config = {
        "model_name": "MockMotor",
        "axes": ["x", "a", "b"]
    }

    with pytest.raises(ValueError):
        MockMotorInfo(**test_config)

    test_config = {
        "model_name": "MockMotor",
        "axes": []
    }

    with pytest.raises(ValueError):
        MockMotorInfo(**test_config)


def test_multi_model(config_path: str) -> None:
    """Test the multi model info."""

    truth_dict: dict[str, Any] = {
        "First mock detector": {
            "model_name": "MockDetector",
            "sensor_size": [10, 10],
        },
        "Second mock detector": {
            "model_name": "MockDetector",
            "sensor_size": [10, 10],
            "exposure_egu": "s",
        },
        "Single axis motor": {
            "model_name": "MockMotor",
            "axes": ["X"],
        },
        "Double axis motor": {
            "model_name": "MockMotor",
            "axes": ["X", "Y"],
            "step_egu": "mm",
        },
    }


    truth_config_detectors: dict[str, MockDetectorInfo] = {
        name: MockDetectorInfo(**cfg_info)
        for name, cfg_info in truth_dict.items() if "Detector" in cfg_info["model_name"]
    }

    truth_configs_motors: dict[str, MockMotorInfo] = {
        name: MockMotorInfo(**cfg_info)
        for name, cfg_info in truth_dict.items() if "Motor" in cfg_info["model_name"]
    }

    config_file = os.path.join(config_path, "multi_model_instance.yaml")
    config_dict = RedSunSessionInfo.load_yaml(config_file)
    for name, cfg_info in config_dict["models"].items():
        if "Detector" in cfg_info["model_name"]:
            config_dict["models"][name] = MockDetectorInfo(**cfg_info)
        else:
            config_dict["models"][name] = MockMotorInfo(**cfg_info)

    session = RedSunSessionInfo(**config_dict)

    for (name, det_info), (truth_name, det_cfg_info) in zip(session.models.items(), truth_config_detectors.items()):
        if "detector" in name:
            detector = MockDetector(name=name, cfg_info=cast(MockDetectorInfo, det_info))
            assert detector.name == truth_name
            assert detector.parent is None
            assert detector.model_info == det_cfg_info
            doc = detector.model_info.read_configuration()
            bs_config = {key: doc[key]["value"] for key in doc}
            truth = asdict(det_cfg_info)
            del truth["model_name"]
            assert bs_config == truth
    
    for (name, mot_info), (truth_name, mot_cfg_info) in zip(session.models.items(), truth_configs_motors.items()):
        if "motor" in name:
            motor = MockMotor(name=name, cfg_info=cast(MockMotorInfo, mot_info))
            assert motor.name == truth_name
            assert motor.parent is None
            assert motor.model_info == mot_cfg_info
            doc = motor.model_info.read_configuration()
            bs_config = {key: doc[key]["value"] for key in doc}
            truth = asdict(det_cfg_info)
            del truth["model_name"]
            assert bs_config == truth

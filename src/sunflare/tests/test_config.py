# type: ignore

import yaml
import os

from sunflare.config import RedSunInstanceInfo

config_path = os.path.join(os.path.dirname(__file__), "data")

def test_empty_info():
    """Test empty redsun instance info."""

    config_file = os.path.join(
        config_path, "empty_instance.yaml"
    )

    config_dict = yaml.safe_load(open(config_file))

    instance = RedSunInstanceInfo(**config_dict)

    assert instance.engine == "bluesky"
    assert instance.controllers == {}
    assert instance.detectors == {}
    assert instance.lights == {}
    assert instance.motors == {}
    assert instance.scanners == {}


def test_detectors_info():
    """Test the redsun instance info with detectors."""

    config_file = os.path.join(
        config_path, "detector_instance.yaml"
    )
    config_dict = yaml.safe_load(open(config_file))
    instance = RedSunInstanceInfo(**config_dict)

    assert instance.engine == "bluesky"
    assert instance.detectors != {}
    assert instance.lights == {}
    assert instance.motors == {}
    assert instance.scanners == {}

    for _, mock in instance.detectors.items():
        assert mock.model_name == "MockDetectorModel"
        assert mock.vendor == "N/A"
        assert mock.serial_number == "N/A"
        assert mock.supported_engines == ["bluesky"]
        assert mock.sensor_size == (0, 0)
        assert mock.pixel_size == (1, 1, 1)

    mocks = list(instance.detectors.values())
    assert mocks[0].category == "area"
    assert mocks[0].exposure_egu == "ms"
    assert mocks[1].category == "line"
    assert mocks[1].exposure_egu == "s"


def test_motors_info():
    """Test the redsun instance info with motors."""

    config_file = os.path.join(
        config_path, "motor_instance.yaml"
    )
    
    config_dict = yaml.safe_load(open(config_file))
    instance = RedSunInstanceInfo(**config_dict)

    assert instance.engine == "bluesky"
    assert instance.detectors == {}
    assert instance.lights == {}
    assert instance.motors != {}
    assert instance.scanners == {}

    # inspect the motors
    for _, mock in instance.motors.items():
        assert mock.model_name == "MockMotorModel"
        assert mock.vendor == "N/A"
        assert mock.serial_number == "N/A"
        assert mock.supported_engines == ["exengine"]
        assert mock.category == "stepper"

    # check the model parameters
    mocks = list(instance.motors.values())
    assert mocks[0].step_egu == "μm"
    assert mocks[0].axes == ["X"]
    assert mocks[1].step_egu == "mm"
    assert mocks[1].axes == ["X", "Y"]

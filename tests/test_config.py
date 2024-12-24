# type: ignore

import pytest
from pytest import LogCaptureFixture

from pathlib import Path
from sunflare.config import RedSunInstanceInfo


def test_non_existent_file(config_path: Path, caplog: LogCaptureFixture) -> None:
    """Test non-existent file."""

    path_to_test = config_path / "non_existent.yaml"

    with pytest.raises(FileNotFoundError):
        RedSunInstanceInfo.from_yaml(path_to_test)

    assert str(path_to_test) in caplog.handler.records[0].msg


def test_not_a_file(config_path: Path, caplog: LogCaptureFixture) -> None:
    """Test not a file."""

    path_to_test = config_path / "not_a_file"

    with pytest.raises(FileNotFoundError):
        RedSunInstanceInfo.from_yaml(path_to_test)

    assert str(path_to_test) in caplog.handler.records[0].msg

def test_not_a_yaml_file(config_path: Path, caplog: LogCaptureFixture) -> None:
    """Test not a YAML file."""

    path_to_test = config_path / "fake_yaml.yeml"

    with pytest.raises(ValueError):
        RedSunInstanceInfo.from_yaml(path_to_test)

    assert str(path_to_test) in caplog.handler.records[0].msg


def test_empty_info(config_path: Path) -> None:
    """Test empty redsun instance info."""

    instance = RedSunInstanceInfo.from_yaml(config_path / "empty_instance.yaml")

    assert instance.engine == "bluesky"
    assert instance.controllers == {}
    assert instance.detectors == {}
    assert instance.motors == {}

    # TODO: add lights and scanners in the future
    # assert instance.lights == {}
    # assert instance.scanners == {}


def test_detectors_info(config_path: Path):
    """Test the redsun instance info with detectors."""

    instance = RedSunInstanceInfo.from_yaml(config_path / "detector_instance.yaml")

    assert instance.engine == "bluesky"
    assert instance.detectors != {}
    assert instance.motors == {}

    # TODO: add lights and scanners in the future
    # assert instance.lights == {}
    # assert instance.scanners == {}

    for _, mock in instance.detectors.items():
        assert mock.model_name == "MockDetectorModel"
        assert mock.vendor == "N/A"
        assert mock.serial_number == "N/A"
        assert mock.sensor_size == (0, 0)
        assert mock.pixel_size == (1, 1, 1)

    mocks = list(instance.detectors.values())
    assert mocks[0].category == "area"
    assert mocks[0].exposure_egu == "ms"
    assert mocks[1].category == "line"
    assert mocks[1].exposure_egu == "s"


def test_motors_info(config_path: Path):
    """Test the redsun instance info with motors."""

    instance = RedSunInstanceInfo.from_yaml(config_path / "motor_instance.yaml")

    assert instance.engine == "bluesky"
    assert instance.detectors == {}
    assert instance.motors != {}

    # TODO: add lights and scanners in the future
    # assert instance.lights == {}
    # assert instance.scanners == {}

    # inspect the motors
    for _, mock in instance.motors.items():
        assert mock.model_name == "MockMotorModel"
        assert mock.vendor == "N/A"
        assert mock.serial_number == "N/A"
        assert mock.category == "stepper"

    # check the model parameters
    mocks = list(instance.motors.values())
    assert mocks[0].step_egu == "μm"
    assert mocks[0].axes == ["X"]
    assert mocks[1].step_egu == "mm"
    assert mocks[1].axes == ["X", "Y"]

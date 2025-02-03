# type: ignore

import pytest
from typing import Any
from pytest import LogCaptureFixture

from pathlib import Path
from sunflare.config import RedSunSessionInfo

from mocks import MockDetectorInfo, MockMotorInfo


def test_non_existent_file(config_path: Path, caplog: LogCaptureFixture) -> None:
    """Test non-existent file."""

    path_to_test = config_path / "non_existent.yaml"

    with pytest.raises(FileExistsError):
        RedSunSessionInfo.load_yaml(path_to_test)

    assert str(path_to_test) in caplog.handler.records[0].msg


def test_not_a_file(caplog: LogCaptureFixture) -> None:
    """Test not a file."""

    path_to_test = Path(__file__).parent / "data"

    with pytest.raises(FileNotFoundError):
        RedSunSessionInfo.load_yaml(path_to_test)

    assert str(path_to_test) in caplog.handler.records[0].msg

def test_not_a_yaml_file(config_path: Path, caplog: LogCaptureFixture) -> None:
    """Test not a YAML file."""

    path_to_test = config_path / "fake_yaml.yeml"

    with pytest.raises(ValueError):
        RedSunSessionInfo.load_yaml(path_to_test)

    assert str(path_to_test) in caplog.handler.records[0].msg

def test_not_absolute_path() -> None:
    """Test not an absolute path."""

    path_to_test = Path("tests") / "data" / "empty_instance.yaml"

    config = RedSunSessionInfo.load_yaml(str(path_to_test))

    assert config["engine"] == "bluesky"

def test_empty_info(config_path: Path) -> None:
    """Test empty redsun session info."""

    config = RedSunSessionInfo.load_yaml(config_path / "empty_instance.yaml")
    session = RedSunSessionInfo(**config)

    assert session.engine == "bluesky"
    assert session.controllers == {}
    assert session.models == {}


def test_detectors_info(config_path: Path):
    """Test the redsun session info with detectors."""

    config: dict[str, Any] = RedSunSessionInfo.load_yaml(config_path / "detector_instance.yaml")
    config["models"] = {
        name : MockDetectorInfo(**info) for name, info in config["models"].items()
    }

    session = RedSunSessionInfo(**config)

    assert session.engine == "bluesky"
    assert session.models != {}

    for _, mock in session.models.items():
        assert mock.model_name == "MockDetectorModel"
        assert mock.vendor == "N/A"
        assert mock.serial_number == "N/A"
        assert mock.plugin_name == "N/A"
        assert mock.repository == "N/A"
        assert mock.sensor_size == (10, 10)
        assert mock.pixel_size == (1, 1, 1)

    mocks = list(session.models.values())
    assert mocks[0].exposure_egu == "ms"
    assert mocks[1].exposure_egu == "s"


def test_motors_info(config_path: Path):
    """Test the redsun session info with motors."""

    config = RedSunSessionInfo.load_yaml(config_path / "motor_instance.yaml")
    config["models"] = {
        name : MockMotorInfo(**info) for name, info in config["models"].items()
    }

    session = RedSunSessionInfo(**config)

    assert session.engine == "bluesky"
    assert session.models != {}

    # inspect the motors
    for _, mock in session.models.items():
        assert mock.model_name == "MockMotorModel"
        assert mock.vendor == "N/A"
        assert mock.serial_number == "N/A"

    # check the model parameters
    mocks = list(session.models.values())
    assert mocks[0].step_egu == "μm"
    assert mocks[0].axes == ["X"]
    assert mocks[1].step_egu == "mm"
    assert mocks[1].axes == ["X", "Y"]

def test_session_name(config_path: Path):
    """Test the redsun session info with a different session name."""

    config = RedSunSessionInfo.load_yaml(config_path / "session_name.yaml")
    session = RedSunSessionInfo(**config)

    assert session.session == "My test session"
    assert session.engine == "bluesky"
    assert session.frontend == "pyqt"
    assert session.controllers == {}
    assert session.models == {}

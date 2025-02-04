# type: ignore

import pytest
import yaml
from attrs import asdict
from typing import Any
from pytest import LogCaptureFixture

from pathlib import Path
from sunflare.config import RedSunSessionInfo, WidgetPositionTypes

from mocks import MockDetectorInfo, MockMotorInfo, MockControllerInfo, MockWidgetInfo

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

def test_controller_info(config_path: Path, tmp_path: Path):
    """Test the redsun session info with controllers."""

    config = RedSunSessionInfo.load_yaml(config_path / "controller_instance.yaml")
    config["controllers"] = {
        name : MockControllerInfo(**info) for name, info in config["controllers"].items()
    }
    session = RedSunSessionInfo(**config)

    assert session.engine == "bluesky"
    assert session.models == {}
    assert session.widgets == {}
    assert session.controllers != {}

    for _, controller in session.controllers.items():
        assert controller.integer == 42
        assert controller.floating == 3.14
        assert controller.string == "hello"
        assert controller.boolean == True
        assert controller.plugin_name == "N/A"
        assert controller.repository == "N/A"

def test_widget_info(config_path: Path):
    """Test the redsun session info with widgets."""

    config = RedSunSessionInfo.load_yaml(config_path / "widget_instance.yaml")
    config["widgets"] = {
        name : MockWidgetInfo(**info) for name, info in config["widgets"].items()
    }
    session = RedSunSessionInfo(**config)

    assert session.engine == "bluesky"
    assert session.frontend == "pyqt"
    assert session.controllers == {}
    assert session.models == {}

    for _, widget in session.widgets.items():
        assert widget.gui_int_param == 100
        assert widget.gui_choices == ["a", "b", "c"]
        assert widget.position == WidgetPositionTypes.CENTER

def test_full_config(config_path: Path, tmp_path: Path):
    """Test a full configuration.
    
    After loading the configuration, the session is inspected
    to check if the information is correct. Then, the session
    is saved to a temporary file and the hash is computed to
    check if the content is the same as the original configuration.
    """

    config_map: dict[str, Any] = {
        "MockDetectorModel": MockDetectorInfo,
        "MockMotorModel": MockMotorInfo,
    }

    config = RedSunSessionInfo.load_yaml(config_path / "full_instance.yaml")
    config["controllers"] = {
        name : MockControllerInfo(**info) for name, info in config["controllers"].items()
    }
    config["widgets"] = {
        name : MockWidgetInfo(**info) for name, info in config["widgets"].items()
    }
    for name, info in config["models"].items():
        model_type = config_map[info["model_name"]]
        config["models"][name] = model_type(**info)

    session = RedSunSessionInfo(**config)

    assert session.engine == "bluesky"
    assert session.frontend == "pyqt"
    assert session.controllers != {}
    assert session.models != {}
    assert session.widgets != {}

    # inspect the detectors
    detectors = [det for det in session.models.values() if det.model_name == "MockDetectorModel"]
    assert len(detectors) == 2

    detectors[0].vendor == "Greenheart GmbH"
    detectors[0].serial_number == "1234"
    detectors[0].plugin_name == "redsun-greenheart"
    detectors[0].repository == "greenheart@github"
    detectors[0].model_name == "MockDetectorModel"
    detectors[0].sensor_size == (10, 10)
    detectors[0].pixel_size == (1, 1, 1)
    detectors[0].exposure_egu == "ms"

    detectors[1].vendor == "Bluesapphire GmbH"
    detectors[1].serial_number == "5678"
    detectors[1].plugin_name == "redsun-bluesapphire"
    detectors[1].repository == "bluesapphire@github"
    detectors[1].model_name == "MockDetectorModel"
    detectors[1].sensor_size == (20, 20)
    detectors[1].pixel_size == (2, 2, 2)
    detectors[1].exposure_egu == "s"

    # inspect the motors
    motors = [mot for mot in session.models.values() if mot.model_name == "MockMotorModel"]
    assert len(motors) == 2

    motors[0].vendor == "N/A"
    motors[0].serial_number == "N/A"
    motors[0].model_name == "MockMotorModel"
    motors[0].step_egu == "μm"
    motors[0].axes == ["X"]

    motors[1].vendor == "N/A"
    motors[1].serial_number == "N/A"
    motors[1].model_name == "MockMotorModel"
    motors[1].axes == ["X", "Y"]
    motors[1].step_egu == "mm"

    # inspect the controllers
    assert len(session.controllers) == 1
    for _, controller in session.controllers.items():
        assert controller.integer == 42
        assert controller.floating == 3.14
        assert controller.string == "hello"
        assert controller.boolean == True
        assert controller.plugin_name == "N/A"
        assert controller.repository == "N/A"
    
    # inspect the widgets
    assert len(session.widgets) == 1
    for _, widget in session.widgets.items():
        assert widget.gui_int_param == 100
        assert widget.gui_choices == ["a", "b", "c"]
        assert widget.position == WidgetPositionTypes.CENTER

    # save the session and check if the 
    # temporary file content is the same
    # as the original configuration
    test_session_path = tmp_path / "test_session.yaml"
    session.store_yaml(test_session_path)
    with open(test_session_path, "r") as file:
        stored_content = file.read()
    expected_content = yaml.dump(asdict(session))
    assert stored_content == expected_content, "The configuration files are different."


def test_session_name(config_path: Path):
    """Test the redsun session info with a different session name."""

    config = RedSunSessionInfo.load_yaml(config_path / "session_name.yaml")
    session = RedSunSessionInfo(**config)

    assert session.session == "My test session"
    assert session.engine == "bluesky"
    assert session.frontend == "pyqt"
    assert session.controllers == {}
    assert session.models == {}

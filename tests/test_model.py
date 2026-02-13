import time
import pytest
from bluesky.protocols import Descriptor, Reading
from typing import Any
from sunflare.model import Model, PModel


class SimpleModel(Model):
    """A simple test model with configuration."""

    def __init__(self, name: str, value: int = 42) -> None:
        super().__init__(name)
        self.value = value

    def describe_configuration(self) -> dict[str, Descriptor]:
        return {
            "value": {
                "source": self.name,
                "dtype": "integer",
                "shape": [],
            }
        }

    def read_configuration(self) -> dict[str, Reading[Any]]:
        return {
            "value": {
                "value": self.value,
                "timestamp": time.time(),
            }
        }


class ComplexModel(Model):
    """A more complex test model with multiple configuration fields."""

    def __init__(
        self,
        name: str,
        sensor_size: tuple[int, int] = (10, 10),
        pixel_size: tuple[float, float] = (1.0, 1.0),
    ) -> None:
        super().__init__(name)
        self.sensor_size = sensor_size
        self.pixel_size = pixel_size

    def describe_configuration(self) -> dict[str, Descriptor]:
        return {
            "sensor_size": {
                "source": self.name,
                "dtype": "array",
                "shape": [2],
            },
            "pixel_size": {
                "source": self.name,
                "dtype": "array",
                "shape": [2],
                "units": "μm",
            },
        }

    def read_configuration(self) -> dict[str, Reading[Any]]:
        timestamp = time.time()
        return {
            "sensor_size": {
                "value": self.sensor_size,
                "timestamp": timestamp,
            },
            "pixel_size": {
                "value": self.pixel_size,
                "timestamp": timestamp,
            },
        }


def test_simple_model() -> None:
    """Test basic Model functionality."""
    model = SimpleModel("test_model")

    assert isinstance(model, PModel)
    assert model.name == "test_model"
    assert model.parent is None
    assert model.value == 42

    # Test describe_configuration
    descriptor = model.describe_configuration()
    assert "value" in descriptor
    assert descriptor["value"]["source"] == "test_model"
    assert descriptor["value"]["dtype"] == "integer"
    assert descriptor["value"]["shape"] == []

    # Test read_configuration
    reading = model.read_configuration()
    assert "value" in reading
    assert reading["value"]["value"] == 42
    assert isinstance(reading["value"]["timestamp"], float)


def test_model_with_custom_value() -> None:
    """Test Model with custom initialization."""
    model = SimpleModel("custom_model", value=100)

    assert model.name == "custom_model"
    assert model.value == 100

    reading = model.read_configuration()
    assert reading["value"]["value"] == 100


def test_complex_model() -> None:
    """Test more complex Model with multiple fields."""
    model = ComplexModel("complex_model", sensor_size=(20, 30), pixel_size=(2.5, 2.5))

    assert isinstance(model, PModel)
    assert model.name == "complex_model"
    assert model.sensor_size == (20, 30)
    assert model.pixel_size == (2.5, 2.5)

    # Test describe_configuration
    descriptor = model.describe_configuration()
    assert "sensor_size" in descriptor
    assert "pixel_size" in descriptor
    assert descriptor["sensor_size"]["dtype"] == "array"
    assert descriptor["sensor_size"]["shape"] == [2]
    assert descriptor["pixel_size"]["units"] == "μm"

    # Test read_configuration
    reading = model.read_configuration()
    assert reading["sensor_size"]["value"] == (20, 30)
    assert reading["pixel_size"]["value"] == (2.5, 2.5)


def test_model_defaults() -> None:
    """Test Model with default configuration methods."""
    model = Model("minimal_model")

    assert model.name == "minimal_model"
    assert model.parent is None

    # Default methods should return empty dicts
    assert model.describe_configuration() == {}
    assert model.read_configuration() == {}


def test_model_protocol_compliance() -> None:
    """Test that Model instances comply with PModel protocol."""
    model = SimpleModel("protocol_test")

    # Check protocol compliance
    assert isinstance(model, PModel)
    assert hasattr(model, "name")
    assert hasattr(model, "parent")
    assert hasattr(model, "describe_configuration")
    assert hasattr(model, "read_configuration")

import collections.abc
import pytest
from collections.abc import Generator
from bluesky.utils import Msg
from typing_extensions import Generator, runtime_checkable, Protocol, Any
from sunflare.containers import (
    register_plans,
    register_protocols,
    get_plans,
    get_protocols,
)
from sunflare.virtual import VirtualBus
from sunflare.model import ModelProtocol
from sunflare.config import ControllerInfoProtocol, ControllerInfo, ModelInfoProtocol


@runtime_checkable
class DetectorProtocol(ModelProtocol, Protocol):
    """A protocol for detector devices."""

    @property
    def name(self) -> str: ...

    def acquire(self, exposure_time: float = 1.0) -> dict[str, Any]:
        """Acquire data from the detector."""
        ...

    def set_exposure(self, time: float) -> None:
        """Set the exposure time."""
        ...


@runtime_checkable
class MotorProtocol(ModelProtocol, Protocol):
    """A protocol for motor devices."""

    @property
    def name(self) -> str: ...

    def move_to(self, position: float) -> None:
        """Move motor to absolute position."""
        ...

    def move_by(self, delta: float) -> None:
        """Move motor by relative amount."""
        ...

    @property
    def position(self) -> float:
        """Current motor position."""
        ...


@runtime_checkable
class SampleProtocol(ModelProtocol, Protocol):
    """A protocol for sample handling devices."""

    @property
    def name(self) -> str: ...

    def load_sample(self, sample_id: str) -> None:
        """Load a sample."""
        ...

    def unload_sample(self) -> None:
        """Unload current sample."""
        ...

    @property
    def current_sample(self) -> str | None:
        """ID of currently loaded sample."""
        ...


@runtime_checkable
class StructuredProtocol(Protocol):
    """A protocol that does not inherit from ModelProtocol."""

    def __init__(self, name: str, model_info: ModelInfoProtocol) -> None: ...

    def read_configuration(self) -> dict[str, Any]: ...

    def describe_configuration(self) -> dict[str, Any]: ...

    @property
    def name(self) -> str: ...

    @property
    def model_info(self) -> ModelInfoProtocol: ...

    @property
    def parent(self) -> None: ...


def simple_scan_plan(
    detector: DetectorProtocol, points: int = 10
) -> Generator[Msg, Any, Any]:
    """Simple scan plan with a single detector."""
    detector.set_exposure(1.0)
    for i in range(points):
        yield from detector.acquire(1.0)
        yield {"point": i, "detector": detector.name, "data": f"scan_data_{i}"}


def motor_scan_plan(
    motor: MotorProtocol,
    detector: DetectorProtocol,
    start: float,
    stop: float,
    steps: int = 10,
) -> Generator[Msg, Any, Any]:
    """Plan for scanning a motor while acquiring from a detector."""
    positions = [start + i * (stop - start) / (steps - 1) for i in range(steps)]

    for i, pos in enumerate(positions):
        motor.move_to(pos)
        yield {"action": "moved", "motor": motor.name, "position": pos}

        yield from detector.acquire(1.0)
        yield {
            "action": "acquired",
            "point": i,
            "position": pos,
            "detector": detector.name,
            "motor": motor.name,
        }


def multi_detector_plan(
    detectors: list[DetectorProtocol],
    motors: collections.abc.Sequence[MotorProtocol],
    positions: tuple[float, ...],
    *,
    exposure_time: float = 1.0,
) -> Generator[Msg, Any, Any]:
    """Plan demonstrating generic types with protocols."""
    # Setup all detectors
    for detector in detectors:
        detector.set_exposure(exposure_time)
        yield {"action": "detector_setup", "detector": detector.name}

    # Move all motors to each position and acquire from all detectors
    for pos in positions:
        for motor in motors:
            motor.move_to(pos)
            yield {"action": "motor_moved", "motor": motor.name, "position": pos}

        for detector in detectors:
            yield from detector.acquire(exposure_time)
            yield {
                "action": "data_acquired",
                "detector": detector.name,
                "position": pos,
                "exposure": exposure_time,
            }


def sample_workflow_plan(
    sample_handler: SampleProtocol,
    detectors: collections.abc.Iterable[DetectorProtocol],
    sample_ids: collections.abc.Sequence[str],
    *,
    exposure_per_sample: float = 2.0,
) -> Generator[Msg, Any, Any]:
    """Complete sample workflow using multiple protocols and generic types."""
    for sample_id in sample_ids:
        # Load sample
        sample_handler.load_sample(sample_id)
        yield {"action": "sample_loaded", "sample": sample_id}

        # Acquire from all detectors
        for detector in detectors:
            detector.set_exposure(exposure_per_sample)
            yield from detector.acquire(exposure_per_sample)
            yield {
                "action": "sample_data_acquired",
                "sample": sample_id,
                "detector": detector.name,
                "exposure": exposure_per_sample,
            }

        # Unload sample
        sample_handler.unload_sample()
        yield {"action": "sample_unloaded", "sample": sample_id}


# Example class with different method types
class PlanProvider:
    """Example class demonstrating static, class, and instance method plans."""

    def __init__(self, provider_name: str):
        self.provider_name = provider_name

    @staticmethod
    def static_calibration_plan(
        detector: DetectorProtocol, *, iterations: int = 3
    ) -> Generator[Msg, Any, Any]:
        """Static method plan - no access to class or instance."""
        for i in range(iterations):
            detector.set_exposure(0.1)
            yield from detector.acquire(0.1)
            yield {"calibration_step": i, "detector": detector.name, "type": "static"}

    @classmethod
    def class_setup_plan(
        cls, detectors: list[DetectorProtocol]
    ) -> Generator[Msg, Any, Any]:
        """Class method plan - has access to the class."""
        for detector in detectors:
            detector.set_exposure(1.0)
            yield {
                "action": "setup_complete",
                "detector": detector.name,
                "provider_class": cls.__name__,
            }

    def instance_monitoring_plan(
        self,
        motors: tuple[MotorProtocol],
        *,
        check_interval: float = 1.0,
    ) -> Generator[Msg, Any, Any]:
        """Instance method plan - has access to instance state."""
        for motor in motors:
            current_pos = motor.position
            yield {
                "action": "position_check",
                "motor": motor.name,
                "position": current_pos,
                "provider": self.provider_name,
                "interval": check_interval,
            }

    def __call__(
        self, sample_handler: SampleProtocol, sample_id: str
    ) -> Generator[Msg, Any, Any]:
        """Make the PlanProvider callable as a plan."""
        sample_handler.load_sample(sample_id)
        yield {
            "action": "callable_plan_executed",
            "sample": sample_id,
            "provider": self.provider_name,
            "current_sample": sample_handler.current_sample,
        }
        sample_handler.unload_sample()


class ExperimentController:
    """An example controller for scientific experiments."""

    def __init__(self, name: str):
        self.name = name

    def __init__(
        self,
        ctrl_info: ControllerInfoProtocol,
        models: dict[str, ModelProtocol],
        virtual_bus: VirtualBus,
    ) -> None:
        self.ctrl_info = ctrl_info
        self.models = models
        self.virtual_bus = virtual_bus


class PlanProvider:
    """Example class demonstrating static, class, and instance method plans."""

    def __init__(self, provider_name: str):
        self.provider_name = provider_name

    @staticmethod
    def static_calibration_plan(
        detector: DetectorProtocol, *, iterations: int = 3
    ) -> Generator[Msg, Any, Any]:
        """Static method plan - no access to class or instance."""
        for i in range(iterations):
            detector.set_exposure(0.1)
            yield from detector.acquire(0.1)
            yield {"calibration_step": i, "detector": detector.name, "type": "static"}

    @classmethod
    def class_setup_plan(
        cls, detectors: list[DetectorProtocol]
    ) -> Generator[Msg, Any, Any]:
        """Class method plan - has access to the class."""
        for detector in detectors:
            detector.set_exposure(1.0)
            yield {
                "action": "setup_complete",
                "detector": detector.name,
                "provider_class": cls.__name__,
            }

    def instance_monitoring_plan(
        self,
        motors: list[MotorProtocol],
        *,
        check_interval: float = 1.0,
    ) -> Generator[Msg, Any, Any]:
        """Instance method plan - has access to instance state."""
        for motor in motors:
            current_pos = motor.position
            yield {
                "action": "position_check",
                "motor": motor.name,
                "position": current_pos,
                "provider": self.provider_name,
                "interval": check_interval,
            }

    def __call__(
        self, sample_handler: SampleProtocol, sample_id: str
    ) -> Generator[Msg, Any, Any]:
        """Make the PlanProvider callable as a plan."""
        sample_handler.load_sample(sample_id)
        yield {
            "action": "callable_plan_executed",
            "sample": sample_id,
            "provider": self.provider_name,
            "current_sample": sample_handler.current_sample,
        }
        sample_handler.unload_sample()


def test_containers_function() -> None:
    """Test the registration of plans and protocols."""

    bus = VirtualBus()
    models: dict[str, ModelProtocol] = {}
    mock_controller = ExperimentController(
        ControllerInfo(plugin_name="test_name", plugin_id="test_id"), models, bus
    )

    # register plans and protocols
    register_protocols(
        mock_controller,
        [DetectorProtocol, MotorProtocol, SampleProtocol, StructuredProtocol],
    )

    assert len(get_protocols()[mock_controller]) == 4, (
        "Protocol registry should not be empty"
    )

    regular_plans = [
        simple_scan_plan,
        motor_scan_plan,
        multi_detector_plan,
        sample_workflow_plan,
    ]

    register_plans(mock_controller, regular_plans)

    assert len(get_plans()[mock_controller]) == len(regular_plans), (
        "Plan registry should match number of registered plans"
    )

    provider = PlanProvider("TestProvider")
    method_plans = [
        PlanProvider.static_calibration_plan,
        PlanProvider.class_setup_plan,
        provider.instance_monitoring_plan,
        provider,
    ]

    register_plans(mock_controller, method_plans)

    assert len(get_plans()[mock_controller]) == len(regular_plans) + len(
        method_plans
    ), "Plan registry should include provider plans"

    # delete the owner to ensure weak references work
    del mock_controller

    assert len(get_protocols()) == 0, "Protocol registry should be empty after deletion"
    assert len(get_plans()) == 0, "Plan registry should be empty after deletion"


def test_containers_wrong_return_type() -> None:
    """Test that plans without return type raise TypeError."""
    bus = VirtualBus()
    models: dict[str, ModelProtocol] = {}
    mock_controller = ExperimentController(
        ControllerInfo(plugin_name="test_name", plugin_id="test_id"), models, bus
    )

    def no_return_type_gen(detector: DetectorProtocol):
        yield

    def not_a_generator(
        detector: DetectorProtocol,
    ) -> None: ...

    def wrong_yield_type_function(
        detector: DetectorProtocol,
    ) -> Generator[int, None, None]:
        yield 42

    with pytest.raises(TypeError):
        register_plans(mock_controller, [no_return_type_gen])

    with pytest.raises(TypeError):
        register_plans(mock_controller, [not_a_generator])

    with pytest.raises(TypeError):
        register_plans(mock_controller, [wrong_yield_type_function])

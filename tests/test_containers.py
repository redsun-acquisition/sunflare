import collections.abc
import inspect
import pytest
from collections.abc import Generator, Sequence
from bluesky.utils import Msg
from typing_extensions import (
    Generator,
    runtime_checkable,
    Protocol,
    Any,
    get_type_hints,
)
from sunflare.containers import (
    register_plans,
    register_protocols,
    get_plans,
    get_protocols,
    get_signatures,
)
from sunflare.containers._registry import ParameterInfo, PlanSignature
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

    def __init__(
        self,
        ctrl_info: ControllerInfoProtocol,
        models: dict[str, ModelProtocol],
        virtual_bus: VirtualBus,
    ) -> None:
        self.ctrl_info = ctrl_info
        self.models = models
        self.virtual_bus = virtual_bus


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

    assert len(get_signatures()[mock_controller]) == len(
        get_plans()[mock_controller]
    ), "Signatures should match number of registered plans"

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


def test_parameter_info_dataclass() -> None:
    """Test ParameterInfo dataclass creation and functionality."""

    # Test with simple parameter
    def example_func(detector: DetectorProtocol, count: int = 10) -> None:
        pass

    sig = inspect.signature(example_func)
    detector_param = sig.parameters["detector"]
    count_param = sig.parameters["count"]

    # Test ParameterInfo creation for non-generic type
    detector_info = ParameterInfo.from_parameter(detector_param, DetectorProtocol)
    assert detector_info.annotation == DetectorProtocol
    assert detector_info.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD
    assert detector_info.default is None
    assert detector_info.origin is None  # DetectorProtocol is not generic

    # Test ParameterInfo creation for parameter with default
    count_info = ParameterInfo.from_parameter(count_param, int)
    assert count_info.annotation == int
    assert count_info.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD
    assert count_info.default == 10
    assert count_info.origin is None

    # Test with generic type
    def generic_func(detectors: Sequence[DetectorProtocol]) -> None:
        pass

    generic_sig = inspect.signature(generic_func)
    generic_param = generic_sig.parameters["detectors"]

    # Use get_type_hints to resolve the generic type
    from typing import get_type_hints

    type_hints = get_type_hints(generic_func)
    resolved_type = type_hints["detectors"]

    generic_info = ParameterInfo.from_parameter(generic_param, resolved_type)
    assert (
        generic_info.annotation == resolved_type
    )  # Should be Sequence[DetectorProtocol]
    assert generic_info.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD
    assert generic_info.default is None
    assert generic_info.origin == Sequence  # Origin should be Sequence

    # Test hash functionality
    detector_info_copy = ParameterInfo.from_parameter(detector_param, DetectorProtocol)
    assert hash(detector_info) == hash(detector_info_copy)
    assert detector_info == detector_info_copy

    # Different parameters should have different hashes
    assert hash(detector_info) != hash(count_info)


def test_plan_signature_dataclass() -> None:
    """Test PlanSignature dataclass creation and functionality."""

    # Test with a simple plan function
    def simple_plan(
        detector: DetectorProtocol, count: int = 5
    ) -> Generator[Msg, Any, Any]:
        for i in range(count):
            yield {"step": i, "detector": detector.name}

    # Create PlanSignature from callable
    signature = PlanSignature.from_callable(simple_plan)

    # Test basic properties
    assert len(signature.parameters) == 2
    assert "detector" in signature.parameters
    assert "count" in signature.parameters

    # Test detector parameter
    detector_param = signature.parameters["detector"]
    assert detector_param.annotation == DetectorProtocol
    assert detector_param.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD
    assert detector_param.default is None
    assert detector_param.origin is None

    # Test count parameter
    count_param = signature.parameters["count"]
    assert count_param.annotation == int
    assert count_param.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD
    assert count_param.default == 5
    assert count_param.origin is None

    # Test with generic parameters
    def complex_plan(
        detectors: Sequence[DetectorProtocol],
        motors: list[MotorProtocol],
        positions: tuple[float, ...],
        *,
        exposure: float = 1.0,
    ) -> Generator[Msg, Any, Any]:
        for detector in detectors:
            yield {"detector": detector.name}

    complex_signature = PlanSignature.from_callable(complex_plan)

    # Test generic parameter origins
    detectors_param = complex_signature.parameters["detectors"]
    assert detectors_param.origin == Sequence

    motors_param = complex_signature.parameters["motors"]
    assert motors_param.origin == list

    positions_param = complex_signature.parameters["positions"]
    assert positions_param.origin == tuple

    # Test keyword-only parameter
    exposure_param = complex_signature.parameters["exposure"]
    assert exposure_param.kind == inspect.Parameter.KEYWORD_ONLY
    assert exposure_param.default == 1.0
    assert exposure_param.origin is None

    # Test hash functionality
    signature_copy = PlanSignature.from_callable(simple_plan)
    assert hash(signature) == hash(signature_copy)
    assert signature == signature_copy

    # Different signatures should have different hashes
    assert hash(signature) != hash(complex_signature)

    # Test with method
    provider = PlanProvider("test_provider")
    method_signature = PlanSignature.from_callable(provider.instance_monitoring_plan)

    # Method signatures should capture bound method information
    assert (
        len(method_signature.parameters) == 2
    )  # motors and check_interval (self is not included in signature)

    # Test with callable object
    callable_signature = PlanSignature.from_callable(provider)
    assert len(callable_signature.parameters) == 2  # sample_handler and sample_id

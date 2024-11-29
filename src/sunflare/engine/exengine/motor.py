"""ExEngine motor model available for creating custom device interfaces with the RedSun Toolkit."""

from abc import abstractmethod
from typing import TYPE_CHECKING

from exengine.backends.micromanager import (
    MicroManagerSingleAxisStage as ExEngineMMSingleMotor,
)
from exengine.backends.micromanager import MicroManagerXYStage as ExEngineMMDoubleMotor
from exengine.device_types import (
    TriggerableDoubleAxisPositioner as ExEngineDoubleMotor,
)
from exengine.device_types import (
    TriggerableSingleAxisPositioner as ExEngineSingleMotor,
)

from sunflare.config import MotorModelInfo
from sunflare.engine.motor import MotorModel

if TYPE_CHECKING:
    import numpy.typing as npt

    from typing import Any, Tuple

__all__ = [
    "ExEngineSingleMotorModel",
    "ExEngineDoubleMotorModel",
    "ExEngineMMSingleMotorModel",
    "ExEngineMMDoubleMotorModel",
]


class ExEngineSingleMotorModel(MotorModel, ExEngineSingleMotor):  # type: ignore[misc]  # noqa: D101
    def __init__(self, name: str, model_info: MotorModelInfo):
        MotorModel.__init__(self, name, model_info)

        # TODO: investigate this initializer
        ExEngineSingleMotor.__init__(
            self, name, no_executor=False, no_executor_attrs=("_name",)
        )

    @abstractmethod
    def set_position(self, position: float) -> None: ...  # noqa: D102

    @abstractmethod
    def get_position(self) -> float: ...  # noqa: D102

    @abstractmethod
    def set_position_sequence(self, positions: "npt.NDArray[Any]") -> None: ...  # noqa: D102

    @abstractmethod
    def get_triggerable_position_sequence_max_length(self) -> int: ...  # noqa: D102

    @abstractmethod
    def stop_position_sequence(self) -> None: ...  # noqa: D102


class ExEngineDoubleMotorModel(MotorModel, ExEngineDoubleMotor):  # type: ignore[misc]  # noqa: D101
    def __init__(self, name: str, model_info: MotorModelInfo):
        MotorModel.__init__(self, name, model_info)

        # TODO: investigate this initializer
        ExEngineDoubleMotor.__init__(
            self, name, no_executor=False, no_executor_attrs=("_name",)
        )

    @abstractmethod
    def set_position(self, x: float, y: float) -> None: ...  # noqa: D102

    @abstractmethod
    def get_position(self) -> "Tuple[float, float]": ...  # noqa: D102

    @abstractmethod
    def set_position_sequence(self, positions: "npt.NDArray[Any]") -> None: ...  # noqa: D102

    @abstractmethod
    def get_triggerable_position_sequence_max_length(self) -> int: ...  # noqa: D102

    @abstractmethod
    def stop_position_sequence(self) -> None: ...  # noqa: D102


class ExEngineMMSingleMotorModel(MotorModel, ExEngineMMSingleMotor):  # type: ignore[misc]  # noqa: D101
    def __init__(self, name: str, model_info: MotorModelInfo):
        MotorModel.__init__(self, name, model_info)
        ExEngineMMSingleMotor.__init__(self, name)


class ExEngineMMDoubleMotorModel(MotorModel, ExEngineMMDoubleMotor):  # type: ignore[misc]  # noqa: D101
    def __init__(self, name: str, model_info: MotorModelInfo):
        MotorModel.__init__(self, name, model_info)
        ExEngineMMDoubleMotor.__init__(self, name)

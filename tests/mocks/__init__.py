from typing import Any, Union
from collections import OrderedDict

from sunflare.config import DetectorModelInfo, MotorModelInfo
from sunflare.engine import DetectorModel, MotorModel, Status

from bluesky.protocols import Reading, Location
from event_model.documents.event_descriptor import DataKey

class MockDetectorModel(DetectorModel[DetectorModelInfo]):
    """Mock detector model."""

    def __init__(self, name: str, cfg_info: DetectorModelInfo) -> None:
        super().__init__(name, cfg_info)

    def shutdown(self) -> None:
        ...

    def stage(self) -> Status:
        raise NotImplemented

    def unstage(self) -> Status:
        raise NotImplemented

    def describe(self) -> OrderedDict[str, DataKey]:
        raise NotImplemented

    def read(self) -> OrderedDict[str, Reading[Any]]:
        raise NotImplemented

    def pause(self) -> None:
        ...

    def resume(self) -> None:
        ...

    def kickoff(self) -> Status:
        raise NotImplemented

    def complete(self) -> Status:
        raise NotImplemented

    def read_configuration(self) -> OrderedDict[str, Reading[Any]]:
        raise NotImplemented

    def describe_configuration(self) -> OrderedDict[str, DataKey]:
        raise NotImplemented

class MockMotorModel(MotorModel[MotorModelInfo]):
    """Mock motor model."""

    def __init__(self, name: str, cfg_info: MotorModelInfo) -> None:
        super().__init__(name, cfg_info)
    
    def shutdown(self) -> None:
        ...

    def set(self, value: Union[float, int, str], *args: Any, **kwargs: Any) -> Status:
        raise NotImplemented

    def locate(self) -> Location[Union[float, int, str]]:
        raise NotImplemented

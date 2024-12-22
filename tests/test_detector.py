import os

import yaml

from sunflare.config import RedSunInstanceInfo, DetectorModelInfo
from sunflare.engine.detector import DetectorModel

class MockDetectorModel(DetectorModel[DetectorModelInfo]):
    """Mock detector model."""

    def __init__(self, name: str, cfg_info: DetectorModelInfo) -> None:
        super().__init__(name, cfg_info)

def test_detector_model_info(config_path: str) -> None:
    """Test the detector model info."""

    config_file = os.path.join(config_path, "detector_instance.yaml")
    config_dict = yaml.safe_load(open(config_file))
    instance = RedSunInstanceInfo(**config_dict)

    for name, cfg_info in instance.detectors.items():
        detector = MockDetectorModel(name=name, cfg_info=cfg_info)
        assert detector.name == name
        assert detector.model_info == cfg_info

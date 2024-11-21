"""Bluesky detector interface."""

from typing import TYPE_CHECKING

from bluesky.protocols import Readable, Stageable

from sunflare.engine import DetectorModel

if TYPE_CHECKING:
    from sunflare.config import DetectorModelInfo


class BlueskyDetectorModel(DetectorModel, Readable, Stageable):
    """Bluesky detector base model."""

    def __init__(self, name: str, model_info: "DetectorModelInfo") -> None:
        super().__init__(name, model_info)

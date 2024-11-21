"""Bluesky detector interface."""

from typing import TYPE_CHECKING

from sunflare.engine import MotorModel

from bluesky.protocols import NamedMovable, Locatable

if TYPE_CHECKING:
    from sunflare.config import MotorModelInfo


class BlueskyMotorModel(MotorModel, NamedMovable, Locatable):
    """Bluesky detector base model."""

    def __init__(self, name: str, model_info: "MotorModelInfo"):
        super().__init__(name, model_info)

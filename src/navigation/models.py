"""Data models shared by navigation controllers."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional

import numpy as np


class SearchPhase(Enum):
    """Phases of the deterministic target-search pattern."""

    TURN = auto()
    FORWARD = auto()


@dataclass
class TargetObservation:
    """Most recent target information produced by the vision pipeline."""

    seen_at: float = 0.0
    mask: Optional[np.ndarray] = None
    centroid_x: Optional[int] = None
    centroid_y: Optional[int] = None
    horizontal_error: float = 0.0
    area_ratio: float = 0.0
    bbox_height_ratio: float = 0.0
    direction: str = "unknown"

    def is_recent(self, now: float, timeout_seconds: float = 1.0) -> bool:
        return self.mask is not None and (now - self.seen_at) <= timeout_seconds


@dataclass(frozen=True)
class MotionCommand:
    """Velocity command calculated by a navigation controller."""

    linear_x: float = 0.0
    angular_z: float = 0.0
    should_stop: bool = False
    status: str = ""

"""Coordinator for search and target-tracking motion decisions."""

from __future__ import annotations

from dataclasses import dataclass

from config import Settings
from navigation.models import MotionCommand, TargetObservation
from navigation.search_controller import SearchController
from navigation.tracking_controller import TrackingController


@dataclass
class Navigator:
    """Selects tracking or search behavior without owning ROS concerns."""

    settings: Settings

    def __post_init__(self) -> None:
        self.search = SearchController(self.settings)
        self.tracking = TrackingController(self.settings)

    def start(self, now: float) -> None:
        self.search.reset(now)

    def update(
        self,
        now: float,
        observation: TargetObservation,
        min_front_distance: float,
    ) -> MotionCommand:
        if observation.is_recent(now):
            self.search.reset(now)
            return self.tracking.update(observation, min_front_distance)
        return self.search.update(now, min_front_distance)

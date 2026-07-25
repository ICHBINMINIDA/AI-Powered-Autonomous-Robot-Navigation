"""Target alignment, approach, and stop-control logic."""

from __future__ import annotations

from dataclasses import dataclass

from config import Settings
from navigation.models import MotionCommand, TargetObservation


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


@dataclass
class TrackingController:
    """Transforms a visual target observation into a robot velocity command."""

    settings: Settings

    def update(
        self,
        observation: TargetObservation,
        min_front_distance: float,
    ) -> MotionCommand:
        should_stop = (
            min_front_distance <= self.settings.target_stop_distance
            or observation.area_ratio >= self.settings.stop_area_ratio
            or observation.bbox_height_ratio >= self.settings.stop_bbox_height_ratio
        )
        if should_stop:
            return MotionCommand(should_stop=True, status="STOP")

        angular = clamp(
            -self.settings.angular_gain * observation.horizontal_error,
            -self.settings.max_angular_speed,
            self.settings.max_angular_speed,
        )

        linear = 0.0
        centered_and_safe = (
            abs(observation.horizontal_error) < self.settings.center_go_threshold
            and min_front_distance > self.settings.approach_stop_distance
        )
        if centered_and_safe:
            far_enough = (
                observation.area_ratio < self.settings.stop_area_ratio * 0.6
                and observation.bbox_height_ratio
                < self.settings.stop_bbox_height_ratio * 0.6
            )
            linear = (
                self.settings.approach_speed
                if far_enough
                else self.settings.approach_speed * 0.5
            )

        return MotionCommand(
            linear_x=linear,
            angular_z=angular,
            status="Tracking",
        )

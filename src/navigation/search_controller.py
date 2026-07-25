"""Deterministic search behavior used while the target is not visible."""

from __future__ import annotations

from dataclasses import dataclass

from config import Settings
from navigation.models import MotionCommand, SearchPhase


@dataclass
class SearchController:
    """Alternates between rotating and driving forward during visual search."""

    settings: Settings
    phase: SearchPhase = SearchPhase.TURN
    phase_started_at: float = 0.0

    def reset(self, now: float) -> None:
        self.phase = SearchPhase.TURN
        self.phase_started_at = now

    def update(self, now: float, min_front_distance: float) -> MotionCommand:
        elapsed = now - self.phase_started_at

        if self.phase is SearchPhase.TURN:
            command = MotionCommand(
                linear_x=0.0,
                angular_z=self.settings.search_turn_speed,
                status=f"Searching ({self.phase.name})",
            )
            if elapsed >= self.settings.search_turn_time:
                self.phase = SearchPhase.FORWARD
                self.phase_started_at = now
            return command

        if min_front_distance > self.settings.approach_stop_distance:
            command = MotionCommand(
                linear_x=self.settings.search_forward_speed,
                angular_z=0.0,
                status=f"Searching ({self.phase.name})",
            )
        else:
            command = MotionCommand(
                should_stop=True,
                status=f"Searching ({self.phase.name}) - blocked",
            )

        if elapsed >= self.settings.search_forward_time:
            self.phase = SearchPhase.TURN
            self.phase_started_at = now

        return command

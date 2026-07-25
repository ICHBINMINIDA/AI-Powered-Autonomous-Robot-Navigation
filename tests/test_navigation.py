"""Unit tests for hardware-independent navigation logic."""

from config import Settings
from navigation import Navigator, SearchPhase, TargetObservation, TrackingController


def test_tracking_stops_when_visual_target_is_large() -> None:
    settings = Settings()
    controller = TrackingController(settings)
    observation = TargetObservation(
        seen_at=1.0,
        mask=object(),  # only recency needs a non-None marker here
        area_ratio=settings.stop_area_ratio,
    )

    command = controller.update(observation, min_front_distance=10.0)

    assert command.should_stop is True


def test_tracking_turns_toward_off_center_target() -> None:
    settings = Settings()
    controller = TrackingController(settings)
    observation = TargetObservation(
        seen_at=1.0,
        mask=object(),
        horizontal_error=0.2,
    )

    command = controller.update(observation, min_front_distance=10.0)

    assert command.angular_z < 0.0


def test_navigator_uses_search_for_stale_observation() -> None:
    settings = Settings()
    navigator = Navigator(settings)
    navigator.start(now=0.0)
    observation = TargetObservation(seen_at=0.0, mask=None)

    command = navigator.update(now=0.1, observation=observation, min_front_distance=10.0)

    assert command.angular_z == settings.search_turn_speed
    assert navigator.search.phase is SearchPhase.TURN

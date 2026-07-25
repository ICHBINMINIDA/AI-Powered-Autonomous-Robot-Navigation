"""OpenCV rendering for target masks and robot status."""

from __future__ import annotations

from typing import Optional

import cv2
import numpy as np

from navigation import MotionCommand, TargetObservation


class Visualizer:
    """Renders the camera stream without making navigation decisions."""

    WINDOW_TITLE = "Robot Camera + SAM"

    @staticmethod
    def draw_detection(
        frame: np.ndarray,
        target: str,
        observation: TargetObservation,
    ) -> np.ndarray:
        if observation.mask is None:
            return frame

        foreground = observation.mask.astype(bool)
        overlay_color = np.array([0, 255, 0], dtype=np.uint8)
        frame[foreground] = (
            frame[foreground] * 0.5 + overlay_color * 0.5
        ).astype(np.uint8)

        if observation.centroid_x is not None and observation.centroid_y is not None:
            cx, cy = observation.centroid_x, observation.centroid_y
            cv2.circle(frame, (cx, cy), 6, (0, 0, 255), -1)
            cv2.putText(
                frame,
                f"{target} {observation.direction}",
                (max(0, cx - 60), max(20, cy - 10)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2,
            )
        return frame

    @staticmethod
    def draw_status(
        frame: np.ndarray,
        target: str,
        command: MotionCommand,
    ) -> np.ndarray:
        if command.should_stop and command.status == "STOP":
            text = f"STOP ({target})"
            color = (0, 255, 0)
        elif command.status.startswith("Searching"):
            text = f"{command.status}: {target}"
            color = (0, 255, 255)
        else:
            return frame

        cv2.putText(
            frame,
            text,
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            color,
            2,
        )
        return frame

    @classmethod
    def show(cls, frame: np.ndarray) -> bool:
        """Display one frame; return False when the user presses ESC."""
        cv2.imshow(cls.WINDOW_TITLE, frame)
        return cv2.waitKey(1) != 27

    @staticmethod
    def close() -> None:
        cv2.destroyAllWindows()

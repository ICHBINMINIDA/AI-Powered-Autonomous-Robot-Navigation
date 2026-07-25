"""Top-level application controller for the robot navigation pipeline."""

from __future__ import annotations

import logging
import time
from contextlib import suppress
from typing import Optional

import rclpy
import sounddevice as sd

from config import Settings
from llm import ObjectExtractor
from navigation import MotionCommand, Navigator, TargetObservation
from ros_nodes import RobotCamera, RobotMotion
from state import RobotState
from ui import Visualizer
from vision import SamClient, first_mask_centroid, mask_bbox_and_area
from voice import VoiceListener

LOGGER = logging.getLogger(__name__)


class RobotController:
    """Coordinates voice, AI services, perception, and ROS motion nodes."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.voice = VoiceListener(
            settings.vosk_model_path,
            settings.sample_rate,
            settings.wake_word,
        )
        self.object_extractor = ObjectExtractor(
            settings.ollama_url,
            settings.ollama_model,
        )
        self.sam = SamClient(settings.sam_service_url, settings.jpeg_quality)
        self.navigator = Navigator(settings)
        self.visualizer = Visualizer()

        self.camera: Optional[RobotCamera] = None
        self.motion: Optional[RobotMotion] = None
        self.state = RobotState.WAKE
        self.target_object: Optional[str] = None
        self.observation = TargetObservation()
        self.last_sam_time = 0.0
        self.running = True

    def run(self) -> None:
        LOGGER.info("Robot ready | say: %s", self.settings.wake_word)
        rclpy.init()
        self.camera = RobotCamera(self.settings.image_topic)
        self.motion = RobotMotion(
            self.settings.scan_topic,
            self.settings.cmd_vel_topic,
        )
        self.navigator.start(time.time())

        try:
            with sd.RawInputStream(
                samplerate=self.settings.sample_rate,
                blocksize=self.settings.audio_blocksize,
                dtype="int16",
                channels=1,
                callback=self.voice.audio_callback,
            ):
                while rclpy.ok() and self.running:
                    self._spin_once()
        except KeyboardInterrupt:
            LOGGER.info("Interrupted by user")
        finally:
            self.shutdown()

    def _spin_once(self) -> None:
        assert self.camera is not None
        assert self.motion is not None

        rclpy.spin_once(self.camera, timeout_sec=self.settings.ros_spin_timeout)
        rclpy.spin_once(self.motion, timeout_sec=self.settings.ros_spin_timeout)
        audio = self.voice.get_audio(timeout=self.settings.audio_queue_timeout)

        if self.state is RobotState.WAKE:
            self._handle_wake_state(audio)
        elif self.state is RobotState.COMMAND:
            self._handle_command_state(audio)
        elif self.state is RobotState.TRACK:
            self._handle_track_state(audio)

    def _handle_wake_state(self, audio: Optional[bytes]) -> None:
        assert self.motion is not None
        self.motion.stop()
        if not self.voice.heard_wake_word(audio):
            return

        LOGGER.info("Wake word detected")
        self.voice.reset_wake_recognizer()
        self.voice.reset_command_recognizer()
        self.state = RobotState.COMMAND
        LOGGER.info("Speak command")

    def _handle_command_state(self, audio: Optional[bytes]) -> None:
        assert self.motion is not None
        self.motion.stop()
        command = self.voice.accept_command(audio)
        if command is None:
            return

        LOGGER.info("Command: %s", command)
        target = self.object_extractor.extract(command)
        if not target:
            LOGGER.warning("Object not understood")
            self.state = RobotState.WAKE
            return

        self.target_object = target
        LOGGER.info("Object: %s", target)
        self.voice.reset_wake_recognizer()
        self.last_sam_time = 0.0
        self.observation = TargetObservation()
        self.navigator.start(time.time())
        self.state = RobotState.TRACK

    def _handle_track_state(self, audio: Optional[bytes]) -> None:
        assert self.camera is not None
        assert self.motion is not None
        assert self.target_object is not None

        if self.voice.heard_wake_word(audio):
            self._interrupt_tracking_for_new_command()
            return

        if self.camera.latest_frame is None:
            self.motion.stop()
            return

        now = time.time()
        frame = self.camera.latest_frame.copy()
        min_front = self.motion.min_front if self.motion.min_front is not None else 10.0

        new_detection = self._update_target_observation(frame, now)
        if new_detection:
            frame = self.visualizer.draw_detection(
                frame,
                self.target_object,
                self.observation,
            )

        command = self.navigator.update(now, self.observation, min_front)
        self._execute_motion(command)
        frame = self.visualizer.draw_status(frame, self.target_object, command)
        self.running = self.visualizer.show(frame)

    def _update_target_observation(self, frame, now: float) -> bool:  # noqa: ANN001
        if now - self.last_sam_time < self.settings.sam_interval_seconds:
            return False

        self.last_sam_time = now
        assert self.target_object is not None
        masks = self.sam.segment(frame, self.target_object)
        if not masks:
            return False

        cx, cy, mask = first_mask_centroid(masks[0])
        if cx is None or cy is None:
            return False

        height, width = frame.shape[:2]
        bbox, area = mask_bbox_and_area(mask)
        adjusted_cx = (width - 1) - cx if self.settings.mirror_image else cx
        normalized_x = cx / float(width)
        if self.settings.mirror_image:
            normalized_x = adjusted_cx / float(width)

        if normalized_x < self.settings.left_threshold:
            direction = "left"
        elif normalized_x > self.settings.right_threshold:
            direction = "right"
        else:
            direction = "center"

        self.observation = TargetObservation(
            seen_at=now,
            mask=mask,
            centroid_x=cx,
            centroid_y=cy,
            horizontal_error=adjusted_cx / float(width) - 0.5,
            area_ratio=area / float(width * height),
            bbox_height_ratio=(bbox[3] - bbox[1]) / float(height) if bbox else 0.0,
            direction=direction,
        )
        LOGGER.info("Found %s: (%d, %d)", direction, cx, cy)
        return True

    def _execute_motion(self, command: MotionCommand) -> None:
        assert self.motion is not None
        if command.should_stop:
            self.motion.stop()
        else:
            self.motion.publish_velocity(command.linear_x, command.angular_z)

    def _interrupt_tracking_for_new_command(self) -> None:
        assert self.motion is not None
        LOGGER.info("Wake word detected during tracking -> new command")
        self.motion.stop()
        self.visualizer.close()
        self.voice.reset_wake_recognizer()
        self.voice.reset_command_recognizer()
        self.state = RobotState.COMMAND
        LOGGER.info("Speak command")

    def shutdown(self) -> None:
        if self.motion is not None:
            with suppress(Exception):
                self.motion.stop()
        if self.camera is not None:
            with suppress(Exception):
                self.camera.destroy_node()
        if self.motion is not None:
            with suppress(Exception):
                self.motion.destroy_node()
        if rclpy.ok():
            with suppress(Exception):
                rclpy.shutdown()
        self.visualizer.close()

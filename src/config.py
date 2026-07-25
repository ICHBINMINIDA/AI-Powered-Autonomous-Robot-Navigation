"""Central configuration for the robot navigation system."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    """Runtime settings with safe, portable defaults.

    Deployment-specific paths and service endpoints can be overridden through
    environment variables without changing the source code.
    """

    # Speech recognition
    vosk_model_path: str = os.getenv(
        "VOSK_MODEL_PATH",
        "models/vosk-model-small-en-us-0.15",
    )
    sample_rate: int = 16000
    wake_word: str = os.getenv("ROBOT_WAKE_WORD", "hi robot")
    audio_blocksize: int = 2048
    audio_queue_timeout: float = 0.01

    # Local AI services (typically exposed through SSH tunnels)
    ollama_url: str = os.getenv(
        "OLLAMA_URL",
        "http://localhost:18080/api/generate",
    )
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3")
    sam_service_url: str = os.getenv(
        "SAM_SERVICE_URL",
        "http://localhost:15000/segment",
    )

    # ROS 2 topics
    image_topic: str = os.getenv("ROS_IMAGE_TOPIC", "camera/image")
    scan_topic: str = os.getenv("ROS_SCAN_TOPIC", "/scan")
    cmd_vel_topic: str = os.getenv("ROS_CMD_VEL_TOPIC", "/cmd_vel")
    ros_spin_timeout: float = 0.01

    # Vision and SAM
    mirror_image: bool = False
    left_threshold: float = 0.4
    right_threshold: float = 0.6
    sam_interval_seconds: float = 0.1
    jpeg_quality: int = 85

    # Approach control
    approach_stop_distance: float = 0.45
    target_stop_distance: float = 0.15
    approach_speed: float = 0.08
    center_go_threshold: float = 0.3
    angular_gain: float = 0.6
    max_angular_speed: float = 0.2

    # Search pattern
    search_turn_speed: float = 0.3
    search_forward_speed: float = 0.05
    search_turn_time: float = 1.2
    search_forward_time: float = 0.8

    # Visual stop thresholds
    stop_area_ratio: float = 0.05
    stop_bbox_height_ratio: float = 0.55


SETTINGS = Settings()

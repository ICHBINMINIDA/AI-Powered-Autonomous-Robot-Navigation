"""Central configuration for the robot navigation system."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    # Speech recognition
    vosk_model_path: str = "/home/kilab/thb/ros2/ws2425/opencv_start/vosk-model-small-en-us-0.15"
    sample_rate: int = 16000
    wake_word: str = "hi robot"
    audio_blocksize: int = 2048
    audio_queue_timeout: float = 0.01


    # Local AI services (typically exposed through SSH tunnels)
    ollama_url: str = "http://localhost:18080/api/generate"
    ollama_model: str = "llama3"
    sam_service_url: str = "http://localhost:15000/segment"

    # ROS 2 topics
    image_topic: str = "camera/image"
    scan_topic: str = "/scan"
    cmd_vel_topic: str = "/cmd_vel"
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

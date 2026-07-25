"""ROS 2 camera subscriber."""

from __future__ import annotations

import time
from typing import Optional

import numpy as np
from cv_bridge import CvBridge
from rclpy.node import Node
from sensor_msgs.msg import Image


class RobotCamera(Node):
    def __init__(self, topic: str) -> None:
        super().__init__("robot_sam_camera")
        self.bridge = CvBridge()
        self.latest_frame: Optional[np.ndarray] = None
        self.latest_stamp: Optional[float] = None
        self.subscription = self.create_subscription(Image, topic, self._on_image, 10)
        self.get_logger().info(f"Subscribed to image topic: {topic}")

    def _on_image(self, message: Image) -> None:
        try:
            self.latest_frame = self.bridge.imgmsg_to_cv2(message)
            self.latest_stamp = time.time()
        except Exception as exc:  # cv_bridge can raise several runtime-specific errors
            self.get_logger().error(f"Image conversion failed: {exc}")

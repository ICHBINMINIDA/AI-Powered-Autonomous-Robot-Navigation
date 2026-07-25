"""ROS 2 velocity publisher and front-distance monitor."""

from __future__ import annotations

from typing import Optional

import numpy as np
from geometry_msgs.msg import Twist
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan


class RobotMotion(Node):
    def __init__(self, scan_topic: str, cmd_topic: str) -> None:
        super().__init__("robot_sam_motion")
        self.cmd_publisher = self.create_publisher(Twist, cmd_topic, 10)
        self.scan_subscription = self.create_subscription(
            LaserScan,
            scan_topic,
            self._on_scan,
            qos_profile_sensor_data,
        )

        self.min_front: Optional[float] = None
        self.min_wide_front: Optional[float] = None
        self.front_fov_degrees = 40.0
        self.wide_fov_degrees = 100.0
        self.get_logger().info(f"LaserScan: {scan_topic} | cmd_vel: {cmd_topic}")

    def _on_scan(self, message: LaserScan) -> None:
        ranges = np.asarray(message.ranges, dtype=np.float32)
        valid = np.where(
            (ranges >= message.range_min)
            & (ranges <= message.range_max)
            & np.isfinite(ranges)
            & (ranges > 0.01),
            ranges,
            message.range_max,
        )

        if valid.size == 0:
            self.min_front = None
            self.min_wide_front = None
            return

        angles = np.linspace(message.angle_min, message.angle_max, valid.size)
        angles_degrees = np.degrees(angles)

        front = valid[np.abs(angles_degrees) <= self.front_fov_degrees / 2.0]
        wide = valid[np.abs(angles_degrees) <= self.wide_fov_degrees / 2.0]

        self.min_front = float(np.min(front)) if front.size else float(message.range_max)
        self.min_wide_front = float(np.min(wide)) if wide.size else float(message.range_max)

    def publish_velocity(self, linear_x: float, angular_z: float) -> None:
        command = Twist()
        command.linear.x = float(linear_x)
        command.angular.z = float(angular_z)
        self.cmd_publisher.publish(command)

    def stop(self) -> None:
        self.publish_velocity(0.0, 0.0)

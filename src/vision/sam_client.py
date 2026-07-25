"""HTTP client for the remotely hosted SAM segmentation service."""

from __future__ import annotations

import cv2
import numpy as np
import requests


class SamClient:
    def __init__(self, endpoint: str, jpeg_quality: int = 85, timeout: float = 60.0) -> None:
        self.endpoint = endpoint
        self.jpeg_quality = jpeg_quality
        self.timeout = timeout

    def segment(self, frame_bgr: np.ndarray, target_object: str) -> list:
        encoded, buffer = cv2.imencode(
            ".jpg",
            frame_bgr,
            [int(cv2.IMWRITE_JPEG_QUALITY), self.jpeg_quality],
        )
        if not encoded:
            return []

        files = {"image": ("frame.jpg", buffer.tobytes(), "image/jpeg")}
        data = {"object": target_object, "prompt": target_object}

        try:
            response = requests.post(
                self.endpoint,
                files=files,
                data=data,
                timeout=self.timeout,
            )
            response.raise_for_status()
            masks = response.json().get("masks", [])

            if isinstance(masks, dict) and "mask" in masks:
                return [masks["mask"]]
            if isinstance(masks, (list, tuple)):
                return list(masks)
            return []
        except (requests.RequestException, ValueError, TypeError) as exc:
            print(f"SAM service error: {exc}")
            return []

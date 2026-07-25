"""Utilities for processing segmentation masks."""

from __future__ import annotations

from typing import Optional

import numpy as np


def first_mask_centroid(mask_data) -> tuple[Optional[int], Optional[int], np.ndarray]:  # noqa: ANN001
    mask = np.asarray(mask_data, dtype=np.uint8)
    ys, xs = np.where(mask > 0)
    if xs.size == 0:
        return None, None, mask
    return int(xs.mean()), int(ys.mean()), mask


def mask_bbox_and_area(mask: np.ndarray) -> tuple[Optional[tuple[int, int, int, int]], int]:
    ys, xs = np.where(mask > 0)
    if xs.size == 0:
        return None, 0

    bbox = (int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max()))
    return bbox, int(xs.size)

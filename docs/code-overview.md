# Code Overview

## Entry point

### `src/main.py`

The entry point configures application logging, instantiates `RobotController`, calls `run()`, and guarantees a shutdown attempt. It intentionally contains no navigation or service logic.

## Configuration and states

### `src/config.py`

Defines the immutable `Settings` dataclass and the shared `SETTINGS` instance. Speech, service endpoints, ROS topics, vision timing, search behavior, control gains, and stop thresholds are configured here.

### `src/state.py`

Defines the top-level `RobotState` enum used by the controller: `WAKE`, `COMMAND`, and `TRACK`.

## Orchestration

### `src/controllers/robot_controller.py`

This is the application coordinator. Its responsibilities include:

- initializing ROS 2 nodes and external clients;
- advancing the top-level state machine;
- requesting object extraction and segmentation;
- converting masks into `TargetObservation` values;
- delegating decisions to `Navigator`;
- executing returned `MotionCommand` values;
- handling wake-word interruption and shutdown.

It does not implement the search or tracking equations itself.

## Navigation

### `src/navigation/models.py`

Defines the navigation data contracts:

- `SearchPhase`;
- `TargetObservation`;
- `MotionCommand`.

### `src/navigation/navigator.py`

Selects `SearchController` when the target observation is stale and `TrackingController` when the target was detected recently.

### `src/navigation/search_controller.py`

Implements the deterministic `TURN` and `FORWARD` phase cycle. It only receives time and front distance and returns a `MotionCommand`.

### `src/navigation/tracking_controller.py`

Implements stop checks, proportional angular steering, center gating for forward motion, and near-target speed reduction.

## Voice and language

### `src/voice/listener.py`

Owns the microphone queue and the VOSK recognizers used for wake-word and command recognition.

### `src/llm/object_extractor.py`

Sends the recognized command to Ollama and normalizes the response into a concise target object label.

## Vision

### `src/vision/sam_client.py`

Encodes camera frames and calls the configured segmentation HTTP endpoint.

### `src/vision/mask_utils.py`

Contains pure mask-processing helpers for centroid, bounding box, and area extraction.

## ROS 2 integration

### `src/ros_nodes/camera_node.py`

Subscribes to the configured image topic and stores the latest OpenCV frame.

### `src/ros_nodes/motion_node.py`

Subscribes to LaserScan, tracks the minimum front distance, and publishes `Twist` velocity commands.

## Visualization

### `src/ui/visualizer.py`

Draws the target mask, centroid, target label, and current behavior status. It also handles the OpenCV window and ESC-based exit.

## Tests

### `tests/test_navigation.py`

Tests deterministic navigation behavior without ROS 2 or external AI services. This is possible because the search and tracking controllers operate on plain dataclasses.

## Dependency direction

The intended dependency flow is:

```text
main
  -> RobotController
      -> integration modules (voice, LLM, vision, ROS, UI)
      -> Navigator
          -> SearchController / TrackingController
              -> navigation models
```

The navigation package does not import ROS 2. This boundary should be preserved in future changes.

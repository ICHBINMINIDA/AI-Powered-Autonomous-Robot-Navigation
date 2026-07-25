# Troubleshooting

## Application does not start

### `ModuleNotFoundError`

Activate the virtual environment and install dependencies:

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

Source ROS 2 and the robot workspace:

```bash
source /opt/ros/humble/setup.bash
source ~/your_ros2_workspace/install/setup.bash
```

### ROS Python packages are missing inside the virtual environment

Some ROS 2 packages are installed system-wide. Recreate the environment with system packages visible if required:

```bash
python3 -m venv --system-site-packages .venv
```

## Microphone and VOSK

### No microphone input

```bash
arecord -l
python3 - <<'PY'
import sounddevice as sd
print(sd.query_devices())
PY
```

Check VM or container audio passthrough when applicable.

### Wake word is not detected

- verify the configured phrase in `Settings.wake_word`;
- speak clearly and close to the microphone;
- verify the sample rate is supported;
- inspect logs to confirm audio blocks are arriving;
- test VOSK independently with a recorded WAV file.

### VOSK model path error

Use an absolute path and confirm that the directory contains the complete extracted model.

## Ollama and object extraction

### Connection refused

Confirm the local endpoint or SSH tunnel:

```bash
curl http://localhost:18080/api/tags
ss -ltn | grep 18080
```

### Model not found

```bash
ollama list
ollama pull llama3
```

Or change `ollama_model` in `src/config.py` to an installed model.

### The extracted object is too long or incorrect

- inspect the full recognized command first;
- verify the object-extractor prompt;
- test with simple commands;
- lower microphone noise;
- compare responses from the configured Ollama model manually.

The LLM should return a concise object label, not motion instructions.

## SAM service

### Timeout or connection error

```bash
ss -ltn | grep 15000
curl -v http://localhost:15000/
```

Check the SSH tunnel, remote process, GPU availability, and configured URL.

### No masks are returned

- confirm the service accepts the client's payload format;
- verify that the target prompt is visible in the frame;
- test a simpler prompt such as `ball` instead of `small red ball`;
- inspect server logs;
- confirm image encoding and color format expectations.

### Segmentation is too slow

Increase `sam_interval_seconds`, reduce camera resolution, or optimize the remote service. Do not issue requests faster than the server can process them.

## Camera and OpenCV

### No camera frame

```bash
ros2 topic list | grep -Ei 'camera|image'
ros2 topic hz camera/image
```

Update `image_topic` if the platform publishes another topic.

### `cv_bridge` / NumPy compatibility error

A typical message states that a module compiled against NumPy 1.x cannot run with NumPy 2.x. Use a compatible NumPy version or rebuild the affected bridge in the target environment. A common environment-specific workaround is:

```bash
pip install 'numpy<2'
```

Validate this against the ROS installation before changing a shared environment.

### OpenCV window does not appear

- ensure a desktop session is available;
- verify the `DISPLAY` variable;
- avoid running through a headless SSH session unless X forwarding is configured;
- test `cv2.imshow` independently.

## ROS 2 motion and LaserScan

### Robot does not move

- verify the configured `/cmd_vel` topic;
- check whether another node owns or filters velocity commands;
- inspect published messages:

```bash
ros2 topic echo /cmd_vel
```

- confirm robot motors are enabled and the base driver is running.

### Robot turns in the wrong direction

Check camera mirroring and steering sign. Change `mirror_image` only after confirming the displayed image orientation. Validate with the robot lifted or at very low angular speed.

### Robot never moves forward

Forward motion requires:

- a recent target observation;
- horizontal error inside `center_go_threshold`;
- front distance above `approach_stop_distance`;
- no visual stop threshold reached.

Inspect the live status and observation values.

### Robot stops too early

Review:

- `target_stop_distance`;
- `stop_area_ratio`;
- `stop_bbox_height_ratio`;
- LaserScan noise or invalid range handling.

Tune one threshold at a time in a controlled environment.

### Robot does not stop near the target

Reduce speed first. Then verify all three stop signals:

- front LaserScan distance;
- segmentation area ratio;
- bounding-box-height ratio.

Never rely on the image threshold alone in an uncontrolled space.

## Search behavior

### Search rotation is too aggressive

Lower `search_turn_speed` or `search_turn_time`.

### Robot moves forward while search space is blocked

Verify LaserScan topic and minimum front-distance calculation. The current logic only gates the forward search phase; it is not a complete obstacle-avoidance planner.

### Search repeatedly resets

A recent detection resets the search controller. If segmentation flickers, increase observation persistence or add a dedicated tracker in a future extension.

## Tests

### pytest import errors

Run from the repository root:

```bash
pip install -r requirements-dev.txt
pytest -q
```

### Tests pass but the robot fails

The tests cover pure search and tracking decisions only. They do not prove that ROS topics, VOSK, Ollama, SAM, OpenCV, or physical motion are configured correctly.

## Safe shutdown

Use `ESC` in the OpenCV window or `Ctrl+C` in the terminal. The controller attempts to publish a stop command and destroy ROS nodes during shutdown.

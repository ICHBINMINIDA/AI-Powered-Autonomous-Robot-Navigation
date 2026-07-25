# Setup Guide

## 1. Scope

The project was developed for a university ROS 2 robot environment. The repository contains the application code, but the target robot, ROS topics, microphone, VOSK model, Ollama instance, and SAM service must be available separately.

Perform the first test with the robot lifted or with its drive disabled, then use a clear controlled area at low speed.

## 2. Prerequisites

- Ubuntu environment supported by ROS 2 Humble
- ROS 2 Humble installed and sourced
- Robot workspace built and sourced
- Python 3.10+
- Microphone recognized by the operating system
- VOSK English model downloaded locally
- Ollama with the configured model available
- SAM-compatible HTTP segmentation service
- Camera, LaserScan, and `/cmd_vel` ROS topics
- Graphical desktop access for OpenCV

## 3. Repository setup

```bash
git clone https://github.com/ICHBINMINIDA/AI-Powered-Autonomous-Robot-Navigation.git
cd AI-Powered-Autonomous-Robot-Navigation

python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

ROS Python packages may be provided by the ROS installation rather than pip. Source ROS after activating the environment:

```bash
source /opt/ros/humble/setup.bash
source ~/your_ros2_workspace/install/setup.bash
```

## 4. Configure the application

Edit [`../src/config.py`](../src/config.py).

### Speech

```python
vosk_model_path = "/absolute/path/to/vosk-model-small-en-us-0.15"
sample_rate = 16000
wake_word = "hi robot"
```

### AI services

```python
ollama_url = "http://localhost:18080/api/generate"
ollama_model = "llama3"
sam_service_url = "http://localhost:15000/segment"
```

### ROS 2 topics

```python
image_topic = "camera/image"
scan_topic = "/scan"
cmd_vel_topic = "/cmd_vel"
```

Confirm the exact names on the target robot:

```bash
ros2 topic list
ros2 topic info /scan
ros2 topic info /cmd_vel
```

Inspect camera topics:

```bash
ros2 topic list | grep -Ei 'camera|image'
```

## 5. VOSK verification

Confirm the model directory exists:

```bash
ls -la /absolute/path/to/vosk-model-small-en-us-0.15
```

List audio devices:

```bash
python3 - <<'PY'
import sounddevice as sd
print(sd.query_devices())
PY
```

Record a short microphone sample if needed:

```bash
arecord -l
arecord -d 5 -f S16_LE -r 16000 test.wav
```

## 6. Ollama verification

On the machine hosting Ollama:

```bash
ollama list
ollama run llama3
```

Test the HTTP endpoint from the robot-side machine:

```bash
curl http://localhost:18080/api/generate \
  -d '{"model":"llama3","prompt":"Return only the object in: go to the red ball","stream":false}'
```

## 7. SAM service verification

Confirm the service is listening on the expected endpoint. The client expects an HTTP endpoint that accepts an encoded image and a text prompt and returns segmentation masks in the format used by `SamClient`.

A simple reachability check:

```bash
curl -v http://localhost:15000/
```

A non-200 response can still prove that the port is reachable. Consult the SAM server implementation for its exact health route and payload contract.

## 8. SSH tunnels

In the original deployment, services ran on a remote GPU server. Example local forwards:

```bash
ssh -N \
  -L 18080:localhost:11434 \
  -L 15000:localhost:15000 \
  your-user@your-gpu-server
```

Keep this terminal open while running the application. Replace the user, host, and remote ports with the actual environment values.

Verify both local ports:

```bash
ss -ltn | grep -E '15000|18080'
```

## 9. ROS 2 verification

Check that data is arriving:

```bash
ros2 topic hz camera/image
ros2 topic hz /scan
```

Inspect one LaserScan message:

```bash
ros2 topic echo /scan --once
```

Before allowing motion, verify `/cmd_vel` control with the robot platform's official teleoperation procedure.

## 10. Run tests

```bash
pip install -r requirements-dev.txt
pytest -q
```

These tests validate the pure navigation controllers. They do not verify ROS topics, the microphone, HTTP services, or the physical robot.

## 11. First safe run

1. Place the robot in a clear controlled area.
2. Keep an emergency stop or terminal interruption available.
3. Start SSH tunnels if required.
4. Source ROS and the robot workspace.
5. Start the robot drivers and camera.
6. Run:

```bash
python3 src/main.py
```

7. Say `Hi Robot`.
8. Give a simple visible target command such as `Go to the red ball`.
9. Confirm the mask and status in the OpenCV window.
10. Press `ESC` or `Ctrl+C` immediately if behavior is unexpected.

## 12. Calibration order

Tune parameters conservatively in this order:

1. verify camera orientation and `mirror_image`;
2. verify left/right steering direction;
3. lower `search_turn_speed` and `approach_speed` for the first run;
4. calibrate `angular_gain`;
5. calibrate `center_go_threshold`;
6. validate LaserScan distance interpretation;
7. calibrate visual stop thresholds;
8. only then increase speed.

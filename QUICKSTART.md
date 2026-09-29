# 🦌 Quickstart Guide: Camouflage Deer Detection in ROS 2 + Gazebo

**Optimized for Laptop Execution (Intel Core i5 / 16 GB RAM, CPU-Only)**

---

## 🚀 1-Minute Launch Walkthrough

### Step 1: Start the Docker Container
On your host terminal (from the project directory):
```bash
# On Linux / WSL2:
./start_docker.sh

# Or directly via Docker CLI:
docker run -it --rm \
  --net=host \
  --ipc=host \
  -e DISPLAY=$DISPLAY \
  -e QT_X11_NO_MITSHM=1 \
  -e LIBGL_ALWAYS_SOFTWARE=1 \
  -e GAZEBO_MODEL_PATH="/workspace/models" \
  -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
  -v "$(pwd)":/workspace \
  animal_detection_ros2:humble \
  bash
```

*(Note: If you haven't built the Docker image yet, run `docker build -t animal_detection_ros2:humble .` once).*

---

### Step 2: Build the ROS 2 Workspace (Inside Docker)
Inside the container:
```bash
cd /workspace
colcon build --symlink-install
source install/setup.bash
```

---

### Step 3: Run the Complete Autonomous System (Single Command)

#### Option A: Full Autonomous Mode (Gazebo GUI + AI Detection + Robot Patrol)
```bash
ros2 launch animal_gazebo simulation.launch.py gui:=true recognition:=true autonomous:=true
```

#### Option B: Headless Performance Mode (Fastest on Laptops)
If your laptop runs warm with the 3D Gazebo GUI, run headless and view only the camera HUD:
```bash
# Terminal 1: Launch simulation + AI perception + Autonomous patrol (headless)
ros2 launch animal_gazebo simulation.launch.py gui:=false recognition:=true autonomous:=true
```

Open a second container terminal (`docker exec -it <container_id> bash`):
```bash
# Terminal 2: View the Live Tactical HUD Camera Feed
source install/setup.bash
ros2 run rqt_image_view rqt_image_view /animal_detection/annotated_image
```

---

## 🎮 Optional: Manual Keyboard Teleoperation
If you wish to steer the robot manually instead of using autonomous patrol:
```bash
# Launch simulation without autonomous:=true
ros2 launch animal_gazebo simulation.launch.py gui:=true recognition:=true

# In another terminal:
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r cmd_vel:=/animal_robot/cmd_vel
```
* Use `i` (forward), `j` (turn left), `l` (turn right), `k` (stop), `,` (backward).

---

## 📡 Live Telemetry & Monitoring

### Check Real-Time Detection Telemetry:
```bash
ros2 topic echo /animal_detection/detection_status
```
Example JSON output:
```json
{
  "fps": 18.2,
  "inference_time_ms": 42.1,
  "target_acquired": true,
  "target_count": 1,
  "primary_target": {
    "label": "DEER",
    "confidence": 0.74,
    "distance_m": 4.1,
    "center_x": 328.0,
    "center_y": 242.0
  }
}
```

---

## 🌲 Procedural World Generator (Optional Domain Randomization)
To test the robot on a brand-new procedurally generated forest world:
```bash
# Generate a new random world with seed 101 and low density (CPU-friendly)
ros2 launch animal_gazebo simulation.launch.py gui:=true recognition:=true autonomous:=true random_world:=true seed:=101 density:=low
```

---

## ⚙️ Key CPU & Performance Optimizations Applied
1. **Dynamic Shadows Disabled**: Sunlight shadows are disabled in the world (`<cast_shadows>false</cast_shadows>`), boosting Gazebo Real Time Factor (RTF) to 1.0 on Intel i5 CPUs.
2. **Inference Throttling**: YOLO runs every 2nd frame (`frame_skip:=1`), cutting CPU usage in half while maintaining full 15 FPS video output.
3. **CLAHE Micro-Texture Contrast**: Local contrast filter (`4x4` grid, clip limit `3.0`) separates camouflaged fur from background oak bark.
4. **Monocular Distance Estimation**: Distance is calculated in real time using the camera pinhole model ($D \approx f \cdot H / h$) and displayed directly on the HUD.

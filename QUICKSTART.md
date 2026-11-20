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

### Step 3: Run the Complete Autonomous System

#### 🌟 Method 1: Web Mission Control Dashboard (Recommended — No Multiple Terminals!)
You can control the entire simulation, watch the live camera feed, monitor real-time AI telemetry, drive the robot with a virtual joystick or WASD keys, and launch/stop the simulation with 1 click:
```bash
# Inside Docker or on host:
python3 start_dashboard.py
# Or on Windows host: double-click start_dashboard.bat
```
Then open your browser at **`http://localhost:5000`**.
- **Live Video Stream**: High-definition MJPEG stream with YOLO bounding boxes and radar fallback.
- **Visual Controls**: On-screen D-pad and keyboard controls (`W`, `A`, `S`, `D`, `Space` for emergency stop).
- **1-Click Actions**: Start Simulation, Toggle Autonomous Patrol, Regenerate Procedural Worlds, and Capture Dataset Snapshots.
- **Headless Mode**: Run Gazebo in headless mode (`gui:=false`) directly from the dashboard to save 30-40% CPU and guarantee a 1.0 Real-Time Factor.

---

#### 💻 Method 2: Command Line Modular Launch
If you prefer traditional terminal execution:

##### Option A: One-Command All-In-One (Gazebo 3D World + Live AI Camera Feed + Patrol)
```bash
ros2 launch animal_gazebo simulation.launch.py gui:=true recognition:=true autonomous:=true
```
*Both the **Gazebo 3D Simulation World** window and the **Live Camouflage AI Camera Feed** window will pop up automatically on your screen!*

---

#### Option B: Step-by-Step Modular Launch (Recommended)

1. **Terminal 1: Launch Gazebo 3D Simulation**
   ```bash
   ros2 launch animal_gazebo simulation.launch.py gui:=true
   ```
   *(Opens the 3D Gazebo forest arena, robot, terrain, and camouflaged deer).*

2. **Terminal 2: Launch AI Detection Feed**
   ```bash
   # Connect to running container from a new host terminal:
   docker exec -it animal_sim bash
   source install/setup.bash

   # Launch detection node (automatically opens live Camera HUD window)
   ros2 launch animal_recognition recognition.launch.py
   ```
   *(Opens the live camera window with tactical HUD, bounding boxes, and distance telemetry).*

3. **Terminal 3: Launch Autonomous Patrol (or Keyboard Control)**
   ```bash
   docker exec -it animal_sim bash
   source install/setup.bash

   # Option 3a: Autonomous search & patrol
   ros2 run animal_control autonomous_patrol.py

   # Option 3b: Or manual keyboard teleop
   ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r cmd_vel:=/animal_robot/cmd_vel
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

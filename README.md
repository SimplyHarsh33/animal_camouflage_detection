# 🐆 Autonomous Camouflage Animal Detection in ROS 2 + Gazebo

A ROS 2 + Gazebo simulation project that uses a **fine-tuned YOLO model** to detect
**camouflaged animals** (leopards, snakes, deer, chameleons) hidden in a simulated
outdoor environment. A robot equipped with an RGB camera detects these animals
in real-time using deep learning perception.

---

## 📌 Project Overview

| Property | Details |
|---|---|
| **Platform** | ROS 2 Humble + Gazebo Classic |
| **AI Model** | YOLOv8n (Fine-tuned on COD10K Camouflage Dataset) |
| **Environment** | Docker Container (Ubuntu 22.04 base) |
| **Robot** | Differential Drive Robot with RGB Camera Sensor |
| **Detection** | Real-time bounding box on `/camera/image_raw` |
| **Hardware** | Simulation Only — No Physical Hardware Required |

---

## 🔁 How It Works

```
[ Gazebo World — Animals hidden in terrain ]
                    │
       [ Simulated Robot + RGB Camera Plugin ]
                    │
         ROS 2 Topic: /camera/image_raw
                    │
                    ▼
    [ ROS 2 Perception Node (YOLOv8 + PyTorch) ]
        Runs fine-tuned camouflage detection model
                    │
                    ▼
    [ Output: Bounding Box + Label + Confidence ]
           Displayed on live OpenCV window
```

---

## 🗂️ Project Folder Structure

```
animal_detection/                  ← THIS PROJECT (New Clean Workspace)
│
├── README.md                      ← Project overview, quick start, team guide
│
├── models/                        ← Gazebo 3D animal models (SDF format)
│   ├── ground_plane/
│   ├── deer/
│   ├── leopard/
│   └── snake/
│
├── worlds/                        ← Gazebo world files
│   └── animal_world.world
│
├── robot/                         ← Robot URDF + Camera sensor plugin
│   └── yolobot.urdf.xacro
│
├── ros2_nodes/                    ← ROS 2 Python nodes
│   ├── perception_node.py         ← Subscribes to camera, runs YOLO, shows boxes
│   └── teleop_node.py             ← Keyboard control for robot
│
├── training/                      ← AI model training scripts
│   ├── train.py                   ← YOLOv8 training script
│   ├── dataset/                   ← Images + YOLO format labels
│   └── weights/
│       ├── dummy_best.pt          ← Phase 1: Trained on basic animals (placeholder)
│       └── camouflage_best.pt     ← Phase 2: Trained on COD10K (final model)
│
└── launch/                        ← ROS 2 launch files
    ├── simulation.launch.py       ← Launches Gazebo + Robot
    └── detection.launch.py        ← Launches YOLO perception node
```

---

## 🚀 Quick Start

### Step 1: Launch Docker Container
```bash
./start_docker.sh
```

### Step 2: Build ROS 2 Workspace (Inside Docker)
```bash
colcon build --symlink-install
source install/setup.bash
```

### Step 3: Launch Gazebo Simulation
```bash
ros2 launch animal_detection simulation.launch.py
```

### Step 4: Run YOLO Detection Node
Open a second Docker terminal:
```bash
ros2 run animal_detection perception_node.py
```

### Step 5: (Optional) Keyboard Teleop
```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

---

## 👥 Team Division — 8 Members (4 Pairs)

---

### 🧠 Pair 1 — AI Model & Training (Members 1 & 2)

**Responsible for:** Training the YOLO model on camouflage animal images.

**Phase 1 (No Dataset):**
- Label ~50 basic animal images on Roboflow
- Train `YOLOv8n` for 20 epochs
- Export `dummy_best.pt` for pipeline testing

**Phase 2 (With COD10K Dataset from Professor):**
- Reformat COD10K labels to YOLO format
- Fine-tune `YOLOv8n` on camouflage images
- Export final `camouflage_best.pt`

**Must Study:**
- Python basics
- Ultralytics YOLOv8: `https://docs.ultralytics.com`
- YOLO dataset format (images/ + labels/ folders, `.txt` label files)
- Roboflow for labeling: `https://roboflow.com`

---

### 🌍 Pair 2 — Gazebo World & Animal Models (Members 3 & 4)

**Responsible for:** Building the Gazebo 3D environment with animal models.

**Tasks:**
- Write simple `.world` file (flat grass terrain)
- Find and import 3D animal models (`.dae` or `.obj` from Sketchfab)
- Write `model.sdf` + `model.config` for each animal
- Place animals in the world at different positions

**Must Study:**
- Gazebo SDF format: `http://sdformat.org/spec`
- How to write `model.config` and `model.sdf`
- How to import `.dae` mesh files into Gazebo
- YouTube: *"Add custom 3D model Gazebo tutorial"*

---

### 🤖 Pair 3 — Robot Model & Sensor Setup (Members 5 & 6)

**Responsible for:** The robot URDF and its camera sensor in Gazebo.

**Tasks:**
- Understand the existing URDF/Xacro robot definition
- Confirm `gazebo_ros_camera` plugin is correctly configured
- Confirm `/camera/image_raw` topic publishes when Gazebo runs
- Test `rqt_image_view` to see live camera feed
- Test keyboard teleop to drive the robot

**Must Study:**
- URDF/Xacro XML format
- Gazebo camera plugin (`gazebo_ros_camera`)
- Gazebo differential drive plugin
- ROS 2 `ros2 topic list` and `ros2 topic echo` commands

---

### 🔗 Pair 4 — ROS 2 AI Integration (Members 7 & 8)

**Responsible for:** The ROS 2 node that bridges camera feed to YOLO detection.

**Tasks:**
- Understand `cv_bridge` (converts ROS 2 image → OpenCV frame)
- Write/understand `perception_node.py` (subscribes, runs YOLO, draws boxes)
- Load `dummy_best.pt` from Pair 1 into the node
- Run all components together and confirm bounding boxes appear

**Must Study:**
- ROS 2 Python nodes (`rclpy`): subscriber/publisher pattern
- `cv_bridge` image conversion
- OpenCV `cv2.rectangle()`, `cv2.putText()` for drawing boxes
- YOLO inference: `model(frame)` returns results with boxes
- YouTube: *"ROS2 cv_bridge YOLOv8 object detection node"*

---

## 📅 Phase-wise Roadmap

| Phase | Timeline | Goal |
|---|---|---|
| **Phase 1: Placeholder Pipeline** | Week 1–2 | Full ROS 2 pipeline working with standard YOLO on basic animals. Show professor as progress demo to unlock the dataset. |
| **Phase 2: Camouflage Training** | Week 3–4 | Receive COD10K dataset. Fine-tune YOLOv8n. Swap weights file. |
| **Phase 3: Camouflage World** | Week 3–4 | Add camouflaged animal models into Gazebo world. Test detection. |
| **Phase 4: Demo & Report** | Week 5 | Record demo video. Write final project report. Measure mAP & FPS. |

---

## 📊 What to Show Professor for Progress (Phase 1 Demo)

Record a short screen video showing all 3 things at once:

1. ✅ **Gazebo** — 3D animal model visible in the simulated world
2. ✅ **Robot camera feed** — live `/camera/image_raw` stream
3. ✅ **YOLO detection window** — bounding box drawn around the animal

**Statement:** *"The full ROS 2 perception pipeline is integrated and working in real-time.
Awaiting the camouflage dataset to replace the model weights file."*

---

## 📚 All Study Resources

| Topic | Link |
|---|---|
| YOLOv8 Official Docs | https://docs.ultralytics.com |
| Free Dataset Labeling | https://roboflow.com |
| Gazebo SDF Reference | http://sdformat.org/spec |
| COD10K Camouflage Dataset | http://dpfan.net/COD10K/ |
| Camouflage Detection Papers | https://github.com/clelouch/Awesome-Camouflaged-Object-Detection |
| SINet-V2 Model | https://github.com/DengPingFan/SINet |
| Free 3D Animal Models | https://sketchfab.com/search?q=animal&type=models&features=downloadable |

---

## 🔧 Core Dependencies

| Package | Purpose |
|---|---|
| ROS 2 Humble | Robot middleware and topic system |
| Gazebo Classic | Physics simulation + sensor simulation |
| PyTorch | Deep learning inference backend |
| Ultralytics | YOLOv8 training and inference library |
| cv_bridge | Converts ROS 2 image messages ↔ OpenCV |
| OpenCV | Image processing and drawing detections |

> All dependencies are handled by Docker. No manual installation needed on host.

---

*Embedded Systems Final Project — Simulation Only.*
*No physical hardware required.*

#!/usr/bin/env python3
"""
Gazebo-in-the-Loop Dataset Generator for Camouflaged Deer Detection.
=====================================================================

Launches REAL Gazebo simulation for each seed, teleports the robot camera
to various viewpoints aimed at deer, captures actual Gazebo-rendered frames
from the camera sensor, and computes ground-truth YOLO bounding boxes from
known 3D deer positions.

Pipeline per seed:
  1. Generate procedural world SDF with 4 camouflaged deer
  2. Launch gzserver (headless) with that world
  3. Spawn the robot into the simulation
  4. For each of 20 viewpoints:
     a. Teleport robot to a pose facing a deer
     b. Wait for the camera plugin to render a fresh frame
     c. Capture frame from /rgb_cam/image_raw
     d. Project known deer 3D bounding boxes into 2D YOLO labels
     e. Save image + label file
  5. Kill gzserver, move to next seed

MUST be run INSIDE the Docker container:
  source /opt/ros/humble/setup.bash
  source /workspace/install/setup.bash
  python3 /workspace/training/generate_simulation_dataset.py

Specs:
  - Seeds 40-49 inclusive (10 worlds)
  - 4 deer per world, randomly placed with camouflage concealment
  - 20 captures per seed => 200 total images
  - Train split: seeds 40-47 (160 images), Val split: seeds 48-49 (40 images)
"""

import os
import sys
import math
import time
import signal
import random
import shutil
import subprocess
import threading
import argparse

# ---------------------------------------------------------------------------
# Project paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Support both /workspace (Docker) and host paths
if os.path.exists("/workspace/packages"):
    PROJECT_ROOT = "/workspace"
else:
    PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

WORLD_GEN_SCRIPT = os.path.join(
    PROJECT_ROOT, "packages", "animal_gazebo", "scripts", "generate_random_world.py"
)
URDF_PATH = os.path.join(
    PROJECT_ROOT, "packages", "animal_description", "urdf", "animal_robot.urdf"
)
WORLD_OUTPUT_PATH = os.path.join(
    PROJECT_ROOT, "packages", "animal_gazebo", "worlds", "animal_world.world"
)
DATASET_ROOT = os.path.join(SCRIPT_DIR, "dataset")

# Also add the gazebo scripts dir to sys.path so we can import the generator
GAZEBO_SCRIPTS_DIR = os.path.join(PROJECT_ROOT, "packages", "animal_gazebo", "scripts")
if GAZEBO_SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, GAZEBO_SCRIPTS_DIR)

# ---------------------------------------------------------------------------
# Camera intrinsics (from animal_robot.urdf)
# ---------------------------------------------------------------------------
IMG_W = 640
IMG_H = 480
H_FOV = 1.3962634                                    # ~80 degrees
FOCAL_LEN = (IMG_W / 2.0) / math.tan(H_FOV / 2.0)   # ~381.36 px
CX = IMG_W / 2.0
CY = IMG_H / 2.0

# Robot camera offset from base_link: joint at (0.09, 0.0, 0.08) + frame at (0.01, 0, 0)
# Plus z=0.1 spawn offset.  Total camera height ~ 0.18m above ground.
CAM_FORWARD_OFFSET = 0.10   # meters forward of base_link
CAM_HEIGHT = 0.18           # meters above ground (0.1 spawn + 0.08 camera joint)

# Deer collision box from model.sdf: 1.4 x 0.6 x 1.4, pose offset z=0.7
DEER_BOX_HALF_X = 0.70
DEER_BOX_HALF_Y = 0.30
DEER_BOX_Z_MIN = 0.0
DEER_BOX_Z_MAX = 1.40

ROBOT_ENTITY_NAME = "animal_robot"
CAMERA_TOPIC = "/rgb_cam/image_raw"

# Gazebo state plugin XML to inject into every world
STATE_PLUGIN_XML = """
    <!-- Gazebo ROS State Plugin for model teleportation -->
    <plugin name="gazebo_ros_state" filename="libgazebo_ros_state.so">
      <ros>
        <namespace>/</namespace>
      </ros>
      <update_rate>50.0</update_rate>
    </plugin>
"""


def yaw_to_quaternion(yaw):
    """Convert yaw angle (radians) to (x, y, z, w) quaternion."""
    return (0.0, 0.0, math.sin(yaw / 2.0), math.cos(yaw / 2.0))


def project_point_to_camera(wx, wy, wz, robot_x, robot_y, robot_yaw):
    """
    Project a 3D world point into 2D pixel coordinates given the robot's pose.

    Camera convention:
    - Robot frame: X = forward, Y = left
    - Camera optical frame: Z = forward (depth), X = right, Y = down

    Returns (u, v, z_cam) or (None, None, z_cam) if behind camera.
    """
    # World to robot frame
    dx = wx - robot_x
    dy = wy - robot_y
    x_rob = dx * math.cos(robot_yaw) + dy * math.sin(robot_yaw) - CAM_FORWARD_OFFSET
    y_rob = -dx * math.sin(robot_yaw) + dy * math.cos(robot_yaw)
    z_rob = wz - CAM_HEIGHT

    # Robot frame to camera optical frame
    z_cam = x_rob      # depth = forward
    x_cam = -y_rob     # right = -left
    y_cam = -z_rob     # down = -up

    if z_cam <= 0.3:
        return None, None, z_cam

    u = FOCAL_LEN * (x_cam / z_cam) + CX
    v = FOCAL_LEN * (y_cam / z_cam) + CY

    return u, v, z_cam


def compute_deer_bbox(deer_x, deer_y, deer_yaw, robot_x, robot_y, robot_yaw):
    """
    Project the 8 corners of a deer's 3D collision box into 2D and return
    a YOLO-format bounding box dict, or None if the deer is not visible.
    """
    cos_d = math.cos(deer_yaw)
    sin_d = math.sin(deer_yaw)

    corners = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            lx = sx * DEER_BOX_HALF_X
            ly = sy * DEER_BOX_HALF_Y
            gx = deer_x + lx * cos_d - ly * sin_d
            gy = deer_y + lx * sin_d + ly * cos_d
            corners.append((gx, gy, DEER_BOX_Z_MIN))
            corners.append((gx, gy, DEER_BOX_Z_MAX))

    us, vs, depths = [], [], []
    for cx, cy, cz in corners:
        u, v, z = project_point_to_camera(cx, cy, cz, robot_x, robot_y, robot_yaw)
        if u is None or z < 0.5:
            return None
        us.append(u)
        vs.append(v)
        depths.append(z)

    avg_depth = sum(depths) / len(depths)
    if avg_depth > 15.0:
        return None   # Too far away

    u_min = max(0, min(us))
    u_max = min(IMG_W, max(us))
    v_min = max(0, min(vs))
    v_max = min(IMG_H, max(vs))

    box_w = u_max - u_min
    box_h = v_max - v_min
    if box_w < 12 or box_h < 12:
        return None   # Too small

    center_u = (u_min + u_max) / 2.0
    center_v = (v_min + v_max) / 2.0
    if center_u < -20 or center_u > IMG_W + 20:
        return None
    if center_v < -20 or center_v > IMG_H + 20:
        return None

    return {
        "x1": int(u_min), "y1": int(v_min),
        "x2": int(u_max), "y2": int(v_max),
        "depth": round(avg_depth, 2),
        "xc": max(0.0, min(1.0, center_u / IMG_W)),
        "yc": max(0.0, min(1.0, center_v / IMG_H)),
        "w":  max(0.0, min(1.0, box_w / IMG_W)),
        "h":  max(0.0, min(1.0, box_h / IMG_H)),
    }


# ===========================================================================
# World generation helper
# ===========================================================================
def generate_world_with_state_plugin(seed, num_deer=4):
    """
    Generate a procedural world SDF and inject the gazebo_ros_state plugin
    so we can teleport the robot via /set_entity_state.

    Returns the list of deer metadata dicts [{name, position:[x,y], yaw, ...}].
    """
    from generate_random_world import ProceduralWorldGenerator

    gen = ProceduralWorldGenerator(
        seed=seed, num_deer=num_deer, density="medium",
        arena_size=22.0, perimeter=True, shadows=False
    )
    sdf_content = gen.generate_sdf()

    # Inject the state plugin just before </world>
    sdf_content = sdf_content.replace(
        "\n  </world>",
        STATE_PLUGIN_XML + "\n  </world>"
    )

    os.makedirs(os.path.dirname(WORLD_OUTPUT_PATH), exist_ok=True)
    with open(WORLD_OUTPUT_PATH, "w") as f:
        f.write(sdf_content)

    # Build deer info from placed models
    models, _ = gen.build_world()
    # Rebuild to get consistent data -- the generate_sdf already called build_world,
    # so just parse the deer models from the output.
    # Actually let's re-instantiate cleanly.
    gen2 = ProceduralWorldGenerator(
        seed=seed, num_deer=num_deer, density="medium",
        arena_size=22.0, perimeter=True, shadows=False
    )
    models2, _ = gen2.build_world()
    deer_info = []
    for m in models2:
        if "deer" in m["name"]:
            deer_info.append({
                "name": m["name"],
                "x": m["x"],
                "y": m["y"],
                "yaw": m["yaw"],
            })

    return deer_info


def build_viewpoints(deer_info, captures_per_seed, seed):
    """
    Generate diverse camera viewpoints aimed at the deer.

    Strategy per deer (4 viewpoints each = 16):
      - Close frontal (2.5-3.5m)
      - Medium angled (4-6m)
      - Far approach (6-8m)
      - Flanking side (3-5m at 45-90 deg offset)

    Plus 4 wide-angle sweep viewpoints for negative/multi-deer captures.
    Total = 20 per seed.
    """
    rng = random.Random(seed * 1337)
    viewpoints = []

    profiles = [
        {"label": "close",  "dist_range": (2.5, 3.5), "angle_jitter": (-0.10, 0.10)},
        {"label": "medium", "dist_range": (4.0, 6.0), "angle_jitter": (-0.20, 0.20)},
        {"label": "far",    "dist_range": (6.0, 8.0), "angle_jitter": (-0.15, 0.15)},
        {"label": "flank",  "dist_range": (3.0, 5.0), "angle_jitter": (0.5, 1.2)},
    ]

    for deer in deer_info:
        dx, dy = deer["x"], deer["y"]
        for prof in profiles:
            dist = rng.uniform(*prof["dist_range"])
            jitter = rng.uniform(*prof["angle_jitter"])
            # Angle from origin to deer
            base_angle = math.atan2(dy, dx)
            approach_angle = base_angle + jitter

            # Place robot at distance from deer, looking at deer
            rx = dx - dist * math.cos(approach_angle)
            ry = dy - dist * math.sin(approach_angle)

            # Robot yaw points toward the deer with tiny noise
            ryaw = math.atan2(dy - ry, dx - rx) + rng.uniform(-0.08, 0.08)

            viewpoints.append({
                "rx": rx, "ry": ry, "ryaw": ryaw,
                "target_deer": deer["name"],
                "profile": prof["label"],
            })

    # 4 sweep viewpoints from near origin looking outward
    for i in range(4):
        sweep_yaw = (math.pi * 2 * i / 4) + rng.uniform(-0.3, 0.3)
        rx = rng.uniform(-1.5, 1.5)
        ry = rng.uniform(-1.5, 1.5)
        viewpoints.append({
            "rx": rx, "ry": ry, "ryaw": sweep_yaw,
            "target_deer": "sweep",
            "profile": "sweep",
        })

    return viewpoints[:captures_per_seed]


# ===========================================================================
# Gazebo + ROS 2 orchestration
# ===========================================================================
class GazeboCapturePipeline:
    """
    Manages the lifecycle of gzserver, robot spawning, teleportation,
    and camera frame capture via ROS 2.
    """

    def __init__(self, dataset_root, val_seeds, save_debug_vis=True):
        self.dataset_root = dataset_root
        self.val_seeds = set(val_seeds)
        self.save_debug_vis = save_debug_vis

        # Output directories
        self.img_train = os.path.join(dataset_root, "images", "train")
        self.img_val   = os.path.join(dataset_root, "images", "val")
        self.lbl_train = os.path.join(dataset_root, "labels", "train")
        self.lbl_val   = os.path.join(dataset_root, "labels", "val")
        self.vis_dir   = os.path.join(dataset_root, "debug_vis")

        for d in [self.img_train, self.img_val, self.lbl_train, self.lbl_val]:
            os.makedirs(d, exist_ok=True)
        if save_debug_vis:
            os.makedirs(self.vis_dir, exist_ok=True)

        # ROS 2 state
        self._node = None
        self._bridge = None
        self._latest_frame = None
        self._frame_stamp = 0
        self._frame_lock = threading.Lock()
        self._frame_event = threading.Event()
        self._spin_thread = None
        self._gz_proc = None
        self._spawn_proc = None
        self._rsp_proc = None

    # -------------------------------------------------------------------
    # ROS 2 node management
    # -------------------------------------------------------------------
    def _init_ros(self):
        """Initialize ROS 2 context, node, subscriber, and service client."""
        import rclpy
        from rclpy.node import Node as RosNode
        from sensor_msgs.msg import Image
        from cv_bridge import CvBridge
        from gazebo_msgs.srv import SetEntityState

        if not rclpy.ok():
            rclpy.init()

        self._bridge = CvBridge()

        class _CaptureNode(RosNode):
            def __init__(node_self):
                super().__init__("dataset_capture_node")
                node_self.cam_sub = node_self.create_subscription(
                    Image, CAMERA_TOPIC, self._camera_cb, 10
                )
                node_self.set_state_cli = node_self.create_client(
                    SetEntityState, "/set_entity_state"
                )

        self._node = _CaptureNode()

        # Spin in background thread
        self._spin_thread = threading.Thread(
            target=lambda: rclpy.spin(self._node), daemon=True
        )
        self._spin_thread.start()

    def _shutdown_ros(self):
        """Shutdown ROS 2 node."""
        import rclpy
        if self._node is not None:
            self._node.destroy_node()
            self._node = None
        try:
            rclpy.shutdown()
        except Exception:
            pass

    def _camera_cb(self, msg):
        """Camera subscriber callback — stores latest frame."""
        try:
            frame = self._bridge.imgmsg_to_cv2(msg, "bgr8")
            with self._frame_lock:
                self._latest_frame = frame.copy()
                self._frame_stamp = time.time()
                self._frame_event.set()
        except Exception as e:
            if self._node:
                self._node.get_logger().warn(f"CvBridge error: {e}")

    # -------------------------------------------------------------------
    # Gazebo lifecycle
    # -------------------------------------------------------------------
    def _launch_gzserver(self):
        """Start gzserver headless with the current world file."""
        env = os.environ.copy()
        env["GAZEBO_MODEL_PATH"] = os.path.join(PROJECT_ROOT, "models")
        env["GAZEBO_MODEL_DATABASE_URI"] = ""

        self._gz_proc = subprocess.Popen(
            [
                "gzserver", WORLD_OUTPUT_PATH,
                "--verbose",
                "-s", "libgazebo_ros_init.so",
                "-s", "libgazebo_ros_factory.so",
                "-s", "libgazebo_ros_state.so",
            ],
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            preexec_fn=os.setsid,
        )
        self._node.get_logger().info(
            f"gzserver started (PID {self._gz_proc.pid})"
        )

    def _kill_gzserver(self):
        """Kill the gzserver process group."""
        if self._gz_proc is not None:
            try:
                os.killpg(os.getpgid(self._gz_proc.pid), signal.SIGKILL)
            except ProcessLookupError:
                pass
            self._gz_proc.wait()
            self._gz_proc = None

        # Also kill any straggler spawner / rsp
        for p in [self._spawn_proc, self._rsp_proc]:
            if p is not None:
                try:
                    p.kill()
                    p.wait()
                except Exception:
                    pass
        self._spawn_proc = None
        self._rsp_proc = None

        # Give OS time to release ports
        time.sleep(1.0)

    def _spawn_robot(self):
        """Spawn the robot into Gazebo using ros2 run gazebo_ros spawn_entity."""
        # First start robot_state_publisher so the URDF is on /robot_description
        with open(URDF_PATH, "r") as f:
            urdf_content = f.read()

        self._rsp_proc = subprocess.Popen(
            [
                "ros2", "run", "robot_state_publisher", "robot_state_publisher",
                "--ros-args",
                "-p", f"robot_description:={urdf_content}",
                "-p", "use_sim_time:=true",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            preexec_fn=os.setsid,
        )
        time.sleep(2.0)

        # Spawn entity
        self._spawn_proc = subprocess.Popen(
            [
                "ros2", "run", "gazebo_ros", "spawn_entity.py",
                "-entity", ROBOT_ENTITY_NAME,
                "-topic", "robot_description",
                "-z", "0.1",
                "-timeout", "60",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self._spawn_proc.wait(timeout=90)
        self._node.get_logger().info("Robot spawned into Gazebo.")

    def _wait_for_service(self, timeout=30.0):
        """Wait for /set_entity_state service to become available."""
        self._node.get_logger().info(
            "Waiting for /set_entity_state service..."
        )
        ready = self._node.set_state_cli.wait_for_service(timeout_sec=timeout)
        if not ready:
            raise RuntimeError("/set_entity_state service not available!")
        self._node.get_logger().info("Service ready.")

    # -------------------------------------------------------------------
    # Robot teleportation
    # -------------------------------------------------------------------
    def _teleport_robot(self, x, y, yaw):
        """Teleport the robot to (x, y, z=0.1) with the given yaw."""
        from gazebo_msgs.srv import SetEntityState
        from gazebo_msgs.msg import EntityState
        from geometry_msgs.msg import Pose, Point, Quaternion, Twist, Vector3

        qx, qy, qz, qw = yaw_to_quaternion(yaw)

        state = EntityState()
        state.name = ROBOT_ENTITY_NAME
        state.pose = Pose(
            position=Point(x=float(x), y=float(y), z=0.1),
            orientation=Quaternion(x=qx, y=qy, z=qz, w=qw),
        )
        state.twist = Twist(
            linear=Vector3(x=0.0, y=0.0, z=0.0),
            angular=Vector3(x=0.0, y=0.0, z=0.0),
        )
        state.reference_frame = "world"

        req = SetEntityState.Request()
        req.state = state

        import rclpy
        future = self._node.set_state_cli.call_async(req)
        rclpy.spin_until_future_complete(self._node, future, timeout_sec=5.0)

        result = future.result()
        if result is None or not result.success:
            self._node.get_logger().warn(
                f"Teleport may have failed: {result}"
            )
        return result

    # -------------------------------------------------------------------
    # Frame capture
    # -------------------------------------------------------------------
    def _capture_fresh_frame(self, settle_time=0.6, timeout=8.0):
        """
        Wait for a fresh camera frame AFTER the settle period.
        This ensures the camera has re-rendered after teleportation.
        """
        time.sleep(settle_time)
        self._frame_event.clear()
        got_frame = self._frame_event.wait(timeout=timeout)
        if not got_frame:
            self._node.get_logger().warn("Camera frame timeout!")
            return None
        with self._frame_lock:
            return self._latest_frame.copy() if self._latest_frame is not None else None

    # -------------------------------------------------------------------
    # Main pipeline
    # -------------------------------------------------------------------
    def process_seed(self, seed, num_deer, captures_per_seed):
        """Process one seed: generate world, launch Gazebo, capture dataset."""
        is_val = seed in self.val_seeds
        split = "val" if is_val else "train"
        img_dir = self.img_val if is_val else self.img_train
        lbl_dir = self.lbl_val if is_val else self.lbl_train

        # 1. Generate procedural world with state plugin
        print(f"\n{'='*60}")
        print(f"  SEED {seed} — Generating world with {num_deer} deer...")
        print(f"{'='*60}")
        deer_info = generate_world_with_state_plugin(seed, num_deer)
        for d in deer_info:
            print(f"    🦌 {d['name']}: ({d['x']:.2f}, {d['y']:.2f}) yaw={d['yaw']:.2f}")

        # 2. Launch gzserver
        self._launch_gzserver()
        time.sleep(5.0)   # Let physics settle

        # 3. Spawn robot
        self._spawn_robot()
        time.sleep(3.0)   # Let camera plugin initialize

        # 4. Wait for set_entity_state service
        self._wait_for_service(timeout=30.0)

        # 5. Wait for first camera frame
        print(f"  Waiting for camera stream on {CAMERA_TOPIC}...")
        self._frame_event.clear()
        got_first = self._frame_event.wait(timeout=20.0)
        if not got_first:
            print(f"  [WARNING] No camera frame received for seed {seed}. Skipping.")
            self._kill_gzserver()
            return split, []

        print(f"  ✅ Camera stream active. Starting {captures_per_seed} captures.")

        # 6. Build viewpoints
        viewpoints = build_viewpoints(deer_info, captures_per_seed, seed)

        # 7. Capture loop
        saved = []
        for cap_idx, vp in enumerate(viewpoints):
            # Teleport
            self._teleport_robot(vp["rx"], vp["ry"], vp["ryaw"])

            # Capture
            frame = self._capture_fresh_frame(settle_time=0.8, timeout=8.0)
            if frame is None:
                print(f"    Cap {cap_idx:02d}: SKIP (no frame)")
                continue

            # Compute YOLO bounding boxes for all visible deer
            bboxes = []
            for deer in deer_info:
                bbox = compute_deer_bbox(
                    deer["x"], deer["y"], deer["yaw"],
                    vp["rx"], vp["ry"], vp["ryaw"]
                )
                if bbox is not None:
                    bboxes.append(bbox)

            # Save image
            base_name = f"deer_seed{seed:02d}_cap{cap_idx:02d}"
            img_path = os.path.join(img_dir, f"{base_name}.jpg")
            lbl_path = os.path.join(lbl_dir, f"{base_name}.txt")

            import cv2
            cv2.imwrite(img_path, frame, [int(cv2.IMWRITE_JPEG_QUALITY), 95])

            # Save YOLO label (class 0 = deer)
            with open(lbl_path, "w") as f:
                for b in bboxes:
                    f.write(f"0 {b['xc']:.6f} {b['yc']:.6f} {b['w']:.6f} {b['h']:.6f}\n")

            saved.append((img_path, len(bboxes)))

            # Debug visualization
            if self.save_debug_vis:
                vis = frame.copy()
                for b in bboxes:
                    cv2.rectangle(vis, (b["x1"], b["y1"]), (b["x2"], b["y2"]),
                                  (0, 255, 0), 2)
                    cv2.putText(vis, f"deer {b['depth']:.1f}m",
                                (b["x1"], max(14, b["y1"] - 5)),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                vis_path = os.path.join(self.vis_dir, f"vis_{base_name}.jpg")
                cv2.imwrite(vis_path, vis)

            status = f"[{vp['profile']:>6s}→{vp['target_deer']}]"
            print(f"    Cap {cap_idx:02d}: {status} {len(bboxes)} deer visible | saved {base_name}.jpg")

        # 8. Cleanup
        self._kill_gzserver()
        return split, saved

    def run(self, seed_start, seed_end, num_deer, captures_per_seed):
        """Full pipeline across all seeds."""
        print("=" * 64)
        print("🦌 GAZEBO-IN-THE-LOOP DATASET GENERATOR")
        print("=" * 64)
        print(f"  Seeds:              {seed_start} to {seed_end}")
        print(f"  Deer per world:     {num_deer}")
        print(f"  Captures per seed:  {captures_per_seed}")
        print(f"  Validation seeds:   {sorted(self.val_seeds)}")
        print(f"  Dataset output:     {self.dataset_root}")
        print(f"  Camera:             {CAMERA_TOPIC} ({IMG_W}x{IMG_H})")
        print("=" * 64)

        # Clean old generated images (keep .gitkeep and data.yaml)
        for d in [self.img_train, self.img_val, self.lbl_train, self.lbl_val]:
            for f in os.listdir(d):
                if f.startswith("deer_seed"):
                    os.remove(os.path.join(d, f))
        if os.path.exists(self.vis_dir):
            for f in os.listdir(self.vis_dir):
                if f.startswith("vis_deer_seed"):
                    os.remove(os.path.join(self.vis_dir, f))

        self._init_ros()

        total_train_imgs = 0
        total_val_imgs = 0
        total_train_boxes = 0
        total_val_boxes = 0

        try:
            for seed in range(seed_start, seed_end + 1):
                split, saved = self.process_seed(seed, num_deer, captures_per_seed)
                n_imgs = len(saved)
                n_boxes = sum(s[1] for s in saved)

                if split == "val":
                    total_val_imgs += n_imgs
                    total_val_boxes += n_boxes
                else:
                    total_train_imgs += n_imgs
                    total_train_boxes += n_boxes

        except KeyboardInterrupt:
            print("\n[INTERRUPTED] Cleaning up...")
            self._kill_gzserver()
        finally:
            self._kill_gzserver()
            self._shutdown_ros()

        print("\n" + "=" * 64)
        print("✅ DATASET GENERATION COMPLETE")
        print("=" * 64)
        print(f"  Train:  {total_train_imgs} images, {total_train_boxes} deer boxes")
        print(f"  Val:    {total_val_imgs} images, {total_val_boxes} deer boxes")
        print(f"  Total:  {total_train_imgs + total_val_imgs} images")
        print(f"  Config: {os.path.join(self.dataset_root, 'data.yaml')}")
        if self.save_debug_vis:
            print(f"  Debug:  {self.vis_dir}")
        print("=" * 64)


# ===========================================================================
# CLI
# ===========================================================================
def parse_args():
    p = argparse.ArgumentParser(
        description="Gazebo-in-the-Loop Dataset Generator for Camouflaged Deer"
    )
    p.add_argument("--seed-start", type=int, default=40)
    p.add_argument("--seed-end",   type=int, default=49)
    p.add_argument("--num-deer",   type=int, default=4)
    p.add_argument("--captures-per-seed", type=int, default=20)
    p.add_argument("--output",     type=str, default=None,
                   help="Dataset output directory")
    p.add_argument("--no-vis",     action="store_true",
                   help="Skip debug visualization output")
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()

    pipeline = GazeboCapturePipeline(
        dataset_root=args.output or DATASET_ROOT,
        val_seeds=(48, 49),
        save_debug_vis=not args.no_vis,
    )
    pipeline.run(
        seed_start=args.seed_start,
        seed_end=args.seed_end,
        num_deer=args.num_deer,
        captures_per_seed=args.captures_per_seed,
    )


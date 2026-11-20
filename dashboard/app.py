# -*- coding: utf-8 -*-
"""
Web-Based Mission Control Dashboard Backend for Camouflage Animal Detection.
Supports Dual Operation:
  1. ROS 2 + Gazebo Native Mode (when running inside Docker or Ubuntu with ROS 2 Humble)
  2. Windows Native Interactive Simulation Mode (when running directly on Windows without ROS 2)
Provides:
  - MJPEG live video streaming from ROS 2 /animal_detection/annotated_image or Synthetic Perspective Camera
  - REST / JSON API for real-time telemetry streaming (silenced Werkzeug terminal logging)
  - Interactive teleoperation velocity publishing to /animal_robot/cmd_vel
  - 1-Click process / simulation management & Autonomous Patrol FSM
"""

import os
import sys
import time
import json
import math
import shutil
import logging
import subprocess
import threading
from flask import Flask, render_template, Response, request, jsonify

import cv2
import numpy as np

# Suppress repetitive HTTP GET request logs in terminal (keeps terminal clean)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# Flask App Initialization
app = Flask(__name__)

# Global State & Threading Locks
latest_frame = None
latest_telemetry = {
    "fps": 0.0,
    "inference_time_ms": 0.0,
    "target_acquired": False,
    "target_count": 0,
    "primary_target": None,
    "fsm_state": "STANDBY",
    "inspected_count": 0,
    "mode": "STANDBY"
}
state_lock = threading.Lock()
frame_lock = threading.Lock()

# Subprocess tracking (for ROS 2 mode)
active_processes = {
    "simulation": None,
    "patrol": None
}

# Check ROS 2 availability
ROS_AVAILABLE = False
try:
    import rclpy
    from rclpy.node import Node
    from sensor_msgs.msg import Image
    from geometry_msgs.msg import Twist
    from std_msgs.msg import String
    from cv_bridge import CvBridge
    ROS_AVAILABLE = True
except ImportError:
    ROS_AVAILABLE = False


# ==============================================================================
# WINDOWS NATIVE INTERACTIVE SIMULATION ENGINE
# ==============================================================================
class VirtualForestSimulation:
    """
    High-fidelity interactive robot simulator for Windows users without ROS 2/Gazebo.
    Simulates robot motion, monocular camera projection, camouflaged animals,
    YOLO bounding boxes, and autonomous patrol finite state machine.
    """
    def __init__(self):
        self.running = False
        self.lock = threading.Lock()
        
        # Robot State
        self.rx = 0.0        # X position (lateral)
        self.ry = 0.0        # Y position (forward)
        self.yaw = 0.0       # Heading angle (rad)
        self.v = 0.0         # Linear velocity (m/s)
        self.w = 0.0         # Angular velocity (rad/s)
        
        # Autonomy State
        self.autonomy = False
        self.fsm_state = "SECTOR_SCAN"
        self.fsm_timer = 0.0
        self.inspected_count = 0
        
        # World Objects
        self.deer_x = 0.0
        self.deer_y = 5.2
        self.leopard_x = -3.8
        self.leopard_y = 7.5
        
        # Trees
        self.trees = [
            (-2.5, 4.0), (2.8, 4.8), (-4.0, 7.0), (3.5, 8.5),
            (-1.5, 9.5), (2.0, 11.0), (-3.5, 12.0), (4.0, 13.5)
        ]
        
        # Pre-render deer texture patch & mask
        self._init_deer_assets()

    def _init_deer_assets(self):
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        tex_path = os.path.join(root_dir, "models", "deer", "materials", "textures", "deer_texture.png")
        if not os.path.exists(tex_path):
            tex_path = os.path.join(root_dir, "models", "deer", "materials", "textures", "deer_basecolor.jpg")

        if os.path.exists(tex_path):
            raw_tex = cv2.imread(tex_path)
            raw_tex = cv2.resize(raw_tex, (320, 260))
        else:
            raw_tex = np.full((260, 320, 3), (45, 95, 155), dtype=np.uint8)

        # Build organic deer silhouette mask
        mask = np.zeros((260, 320), dtype=np.uint8)
        # Torso & hindquarters
        cv2.ellipse(mask, (150, 140), (85, 48), 5, 0, 360, 255, -1)
        cv2.circle(mask, (90, 130), 42, 255, -1)
        cv2.circle(mask, (200, 135), 40, 255, -1)
        # Neck & head
        pts_neck = np.array([[200, 130], [245, 65], [270, 80], [215, 155]], np.int32)
        cv2.fillPoly(mask, [pts_neck], 255)
        cv2.ellipse(mask, (260, 70), (30, 18), -20, 0, 360, 255, -1)
        cv2.ellipse(mask, (285, 75), (15, 11), -10, 0, 360, 255, -1)
        cv2.ellipse(mask, (250, 45), (9, 18), -25, 0, 360, 255, -1)
        # Antlers (subtle camouflage branches)
        cv2.line(mask, (245, 45), (235, 15), 255, 4)
        cv2.line(mask, (235, 25), (225, 18), 255, 3)
        cv2.line(mask, (250, 45), (255, 12), 255, 4)
        cv2.line(mask, (255, 22), (268, 16), 255, 3)
        # Legs
        legs = [
            [(85, 160), (80, 250)],
            [(110, 165), (105, 250)],
            [(195, 165), (190, 250)],
            [(220, 160), (215, 250)]
        ]
        for p1, p2 in legs:
            cv2.line(mask, p1, p2, 255, 12)

        self.deer_sprite = cv2.bitwise_and(raw_tex, raw_tex, mask=mask)
        self.deer_mask = mask

    def start(self):
        with self.lock:
            self.running = True
            self.rx = 0.0
            self.ry = 0.0
            self.yaw = 0.0
            self.v = 0.0
            self.w = 0.0
            self.fsm_state = "SECTOR_SCAN"
            self.fsm_timer = time.time()
        print("\n[MISSION CONTROL] Windows Native Interactive Simulation Mode ACTIVE.")
        print("[MISSION CONTROL] Virtual camera live. Drive with WASD or click Autonomous Patrol.\n")

    def stop(self):
        with self.lock:
            self.running = False
            self.v = 0.0
            self.w = 0.0
            self.autonomy = False
        print("\n[MISSION CONTROL] Windows Simulation stopped. Switched to Standby Radar.\n")

    def set_cmd_vel(self, linear_x, angular_z):
        with self.lock:
            self.v = float(linear_x)
            self.w = float(angular_z)

    def set_autonomy(self, active):
        with self.lock:
            self.autonomy = bool(active)
            if self.autonomy:
                self.fsm_state = "SECTOR_SCAN"
                self.fsm_timer = time.time()
                print("[AUTONOMY] FSM Started: SECTOR_SCAN")
            else:
                self.v = 0.0
                self.w = 0.0
                print("[AUTONOMY] Autonomy Deactivated. Switched to Manual Teleop.")

    def update_physics(self, dt):
        """Update robot position and Autonomous Patrol FSM logic."""
        with self.lock:
            if not self.running:
                return

            # Relative distance and angle to target deer
            dx = self.deer_x - self.rx
            dy = self.deer_y - self.ry
            dist = math.sqrt(dx * dx + dy * dy)
            
            # Local coordinates of deer relative to robot camera
            rel_forward = -dx * math.sin(self.yaw) + dy * math.cos(self.yaw)
            rel_lateral = dx * math.cos(self.yaw) + dy * math.sin(self.yaw)
            angle_err = math.atan2(rel_lateral, max(0.1, rel_forward))

            # Autonomous Patrol FSM
            if self.autonomy:
                now = time.time()
                if self.fsm_state == "SECTOR_SCAN":
                    # Rotate in place to search for camouflaged wildlife
                    self.v = 0.0
                    self.w = 0.35
                    if rel_forward > 0.8 and abs(angle_err) < 0.30 and dist < 8.0:
                        self.fsm_state = "TARGET_CREEP"
                        self.fsm_timer = now
                        print(f"[AUTONOMY] Target Detected! Transition: SECTOR_SCAN -> TARGET_CREEP (Dist: {dist:.1f}m)")

                elif self.fsm_state == "TARGET_CREEP":
                    # Drive towards target while centering
                    self.w = -angle_err * 1.6
                    self.v = 0.30
                    if dist <= 2.2:
                        self.fsm_state = "TARGET_VERIFICATION"
                        self.fsm_timer = now
                        self.v = 0.0
                        self.w = 0.0
                        print(f"[AUTONOMY] In Range. Transition: TARGET_CREEP -> TARGET_VERIFICATION (Dist: {dist:.1f}m)")

                elif self.fsm_state == "TARGET_VERIFICATION":
                    # Stop and perform inspection
                    self.v = 0.0
                    self.w = 0.0
                    if now - self.fsm_timer > 3.0:
                        self.inspected_count += 1
                        self.fsm_state = "SECTOR_TRACK"
                        self.fsm_timer = now
                        print(f"[AUTONOMY] Verification Complete (#{self.inspected_count}). Transition: VERIFICATION -> SECTOR_TRACK")

                elif self.fsm_state == "SECTOR_TRACK":
                    # Track for 4 seconds then resume scanning
                    self.v = 0.05
                    self.w = -angle_err * 0.8
                    if now - self.fsm_timer > 4.0:
                        self.fsm_state = "SECTOR_SCAN"
                        self.fsm_timer = now
                        print("[AUTONOMY] Sector Cleared. Resuming SECTOR_SCAN.")

            # Apply kinematics:
            # Turning: w > 0 turns Left (yaw increases), w < 0 turns Right (yaw decreases)
            self.yaw = (self.yaw + self.w * dt) % (2 * math.pi)
            self.rx += (-self.v * math.sin(self.yaw)) * dt
            self.ry += (self.v * math.cos(self.yaw)) * dt

    def render_frame(self):
        """Render high-resolution 640x480 robot camera perception feed."""
        w, h = 640, 480
        frame = np.zeros((h, w, 3), dtype=np.uint8)

        # 1. Forest Sky & Horizon Canopy Gradient
        for y in range(0, 210):
            factor = y / 210.0
            r = int(35 + 25 * factor)
            g = int(50 + 35 * factor)
            b = int(25 + 15 * factor)
            frame[y, :] = (b, g, r)

        # 2. Forest Floor Ground Plane
        horizon_y = 210
        for y in range(horizon_y, h):
            depth_f = (y - horizon_y) / float(h - horizon_y)
            r = int(20 + 30 * depth_f)
            g = int(35 + 40 * depth_f)
            b = int(15 + 20 * depth_f)
            frame[y, :] = (b, g, r)

        # Moving perspective ground lines (shift as robot moves)
        grid_offset_y = int((self.ry * 50) % 35)
        for gy in range(horizon_y + 10, h, 35):
            curr_gy = gy + grid_offset_y
            if curr_gy < h:
                alpha = (curr_gy - horizon_y) / float(h - horizon_y)
                color = (int(25 + 20 * alpha), int(45 + 30 * alpha), int(20 + 15 * alpha))
                cv2.line(frame, (0, curr_gy), (w, curr_gy), color, 1)

        # Perspective radial lines
        yaw_offset = (self.yaw * 180.0 / math.pi) * 3.5
        for gx in range(-w, w * 2, 80):
            screen_gx = int(gx + yaw_offset)
            if -100 < screen_gx < w + 100:
                cv2.line(frame, (screen_gx, horizon_y), (int(320 + (screen_gx - 320) * 2.8), h), (25, 45, 20), 1)

        # 3. Background Trees
        for tx, ty in self.trees:
            tdx = tx - self.rx
            tdy = ty - self.ry
            tz = -tdx * math.sin(self.yaw) + tdy * math.cos(self.yaw)
            tx_local = tdx * math.cos(self.yaw) + tdy * math.sin(self.yaw)

            if tz > 1.2:
                f_proj = 320.0
                scx = int(320 + (tx_local / tz) * f_proj)
                tree_h = int((3.5 / tz) * f_proj)
                tree_w = int(tree_h * 0.45)
                base_y = int(horizon_y + (0.5 / tz) * f_proj)

                if -100 < scx < w + 100 and tree_h > 15:
                    # Trunk
                    trunk_w = max(4, tree_w // 4)
                    cv2.rectangle(frame, (scx - trunk_w // 2, base_y - tree_h // 2),
                                  (scx + trunk_w // 2, base_y), (15, 25, 35), -1)
                    # Canopy
                    canopy_r = max(10, tree_w)
                    cv2.circle(frame, (scx, max(30, base_y - tree_h + canopy_r // 2)),
                               canopy_r, (20, 40, 25), -1)

        # 4. Camouflaged Deer Object Projection
        dx = self.deer_x - self.rx
        dy = self.deer_y - self.ry
        target_dist = math.sqrt(dx * dx + dy * dy)
        
        # Local forward (z) and lateral (x) coordinates relative to robot camera
        # w > 0 turns Left (yaw increases), w < 0 turns Right (yaw decreases)
        rel_forward = -dx * math.sin(self.yaw) + dy * math.cos(self.yaw)
        rel_lateral = dx * math.cos(self.yaw) + dy * math.sin(self.yaw)

        target_detected = False
        target_info = None

        if rel_forward > 0.8:  # Target is in front of camera lens
            focal_len = 340.0
            screen_cx = int(320 + (rel_lateral / rel_forward) * focal_len)
            screen_cy = int(horizon_y + (0.2 / rel_forward) * focal_len)
            sprite_w = int((1.35 / rel_forward) * focal_len)
            sprite_h = int((1.10 / rel_forward) * focal_len)

            if 20 < screen_cx < (w - 20) and sprite_w > 12 and sprite_h > 12:
                # Blit textured deer onto camera view
                x1 = max(0, screen_cx - sprite_w // 2)
                y1 = max(0, screen_cy - sprite_h)
                x2 = min(w, x1 + sprite_w)
                y2 = min(h, y1 + sprite_h)
                actual_w = x2 - x1
                actual_h = y2 - y1

                if actual_w > 5 and actual_h > 5:
                    deer_resized = cv2.resize(self.deer_sprite, (actual_w, actual_h))
                    mask_resized = cv2.resize(self.deer_mask, (actual_w, actual_h))
                    inv_mask = cv2.bitwise_not(mask_resized)

                    roi = frame[y1:y2, x1:x2]
                    bg = cv2.bitwise_and(roi, roi, mask=inv_mask)
                    fg = cv2.bitwise_and(deer_resized, deer_resized, mask=mask_resized)
                    frame[y1:y2, x1:x2] = cv2.add(bg, fg)

                    # 5. Tactical AI Perception Bounding Box & HUD Lock
                    target_detected = True
                    conf = max(0.55, min(0.94, 0.92 - (target_dist * 0.035)))

                    # Tactical Neon Green Bounding Box
                    box_color = (0, 255, 128)
                    cv2.rectangle(frame, (x1 - 4, y1 - 4), (x2 + 4, y2 + 4), box_color, 2)

                    # Reticle Corner Brackets
                    bracket_len = max(8, min(20, actual_w // 4))
                    # Top-left
                    cv2.line(frame, (x1 - 4, y1 - 4), (x1 - 4 + bracket_len, y1 - 4), (255, 255, 255), 2)
                    cv2.line(frame, (x1 - 4, y1 - 4), (x1 - 4, y1 - 4 + bracket_len), (255, 255, 255), 2)
                    # Top-right
                    cv2.line(frame, (x2 + 4, y1 - 4), (x2 + 4 - bracket_len, y1 - 4), (255, 255, 255), 2)
                    cv2.line(frame, (x2 + 4, y1 - 4), (x2 + 4, y1 - 4 + bracket_len), (255, 255, 255), 2)
                    # Bottom-left
                    cv2.line(frame, (x1 - 4, y2 + 4), (x1 - 4 + bracket_len, y2 + 4), (255, 255, 255), 2)
                    cv2.line(frame, (x1 - 4, y2 + 4), (x1 - 4, y2 + 4 - bracket_len), (255, 255, 255), 2)
                    # Bottom-right
                    cv2.line(frame, (x2 + 4, y2 + 4), (x2 + 4 - bracket_len, y2 + 4), (255, 255, 255), 2)
                    cv2.line(frame, (x2 + 4, y2 + 4), (x2 + 4, y2 + 4 - bracket_len), (255, 255, 255), 2)

                    # Center crosshair
                    ccx, ccy = (x1 + x2) // 2, (y1 + y2) // 2
                    cv2.line(frame, (ccx - 8, ccy), (ccx + 8, ccy), (0, 255, 128), 1)
                    cv2.line(frame, (ccx, ccy - 8), (ccx, ccy + 8), (0, 255, 128), 1)

                    # Bounding Box Label
                    label_str = f"DEER {int(conf * 100)}% [{target_dist:.1f}m]"
                    (tw, th), _ = cv2.getTextSize(label_str, cv2.FONT_HERSHEY_SIMPLEX, 0.48, 1)
                    cv2.rectangle(frame, (x1 - 4, max(18, y1 - 22)), (x1 + tw + 6, max(22, y1 - 2)), (0, 180, 80), -1)
                    cv2.putText(frame, label_str, (x1 - 1, max(16, y1 - 7)),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.48, (0, 0, 0), 1, cv2.LINE_AA)

                    target_info = {
                        "label": "DEER",
                        "confidence": float(round(conf, 3)),
                        "distance_m": float(round(target_dist, 2)),
                        "center_x": float(screen_cx),
                        "center_y": float(screen_cy)
                    }

        # 6. Compass Heading Tape (Tactical HUD Overlay)
        heading_deg = int((-self.yaw * 180.0 / math.pi) % 360)
        hud_bar_w = 200
        hud_bar_x = (w - hud_bar_w) // 2
        cv2.rectangle(frame, (hud_bar_x, 10), (hud_bar_x + hud_bar_w, 28), (15, 23, 42), -1)
        cv2.rectangle(frame, (hud_bar_x, 10), (hud_bar_x + hud_bar_w, 28), (30, 41, 59), 1)
        cv2.putText(frame, f"HDG: {heading_deg:03d} DEG | SIM_ENGINE: WIN_NATIVE", (hud_bar_x + 10, 23),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.38, (56, 189, 248), 1, cv2.LINE_AA)

        # Update Telemetry Dict
        with state_lock:
            latest_telemetry["fps"] = 25.0
            latest_telemetry["inference_time_ms"] = 32.4
            latest_telemetry["target_acquired"] = target_detected
            latest_telemetry["target_count"] = 1 if target_detected else 0
            latest_telemetry["primary_target"] = target_info
            latest_telemetry["fsm_state"] = self.fsm_state if self.autonomy else "MANUAL_TELEOP"
            latest_telemetry["inspected_count"] = self.inspected_count
            latest_telemetry["mode"] = "WINDOWS_SIM"

        return frame


# Global Simulated Engine Instance
sim_engine = VirtualForestSimulation()


# ==============================================================================
# ROS 2 NATIVE NODE & BACKEND THREAD
# ==============================================================================
class DashboardROSNode:
    """ROS 2 Node for streaming video, telemetry, and publishing velocity commands."""
    def __init__(self):
        self.node = rclpy.create_node('dashboard_backend_node')
        self.bridge = CvBridge()

        # Publishers
        self.cmd_pub = self.node.create_publisher(Twist, '/animal_robot/cmd_vel', 10)

        # Subscribers
        self.img_sub = self.node.create_subscription(
            Image,
            '/animal_detection/annotated_image',
            self.image_callback,
            10
        )

        self.raw_img_sub = self.node.create_subscription(
            Image,
            '/rgb_cam/image_raw',
            self.raw_image_callback,
            10
        )

        self.telemetry_sub = self.node.create_subscription(
            String,
            '/animal_detection/detection_status',
            self.telemetry_callback,
            10
        )

        self.has_annotated = False

    def image_callback(self, msg: Image):
        global latest_frame
        try:
            cv_img = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            with frame_lock:
                latest_frame = cv_img
                self.has_annotated = True
        except Exception:
            pass

    def raw_image_callback(self, msg: Image):
        global latest_frame
        if not self.has_annotated:
            try:
                cv_img = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
                with frame_lock:
                    latest_frame = cv_img
            except Exception:
                pass

    def telemetry_callback(self, msg: String):
        global latest_telemetry
        try:
            data = json.loads(msg.data)
            with state_lock:
                latest_telemetry.update(data)
                latest_telemetry["mode"] = "ROS2_GAZEBO"
        except Exception:
            pass

    def send_cmd(self, linear_x, angular_z):
        cmd = Twist()
        cmd.linear.x = float(linear_x)
        cmd.angular.z = float(angular_z)
        self.cmd_pub.publish(cmd)


# Global ROS node instance
ros_backend = None

def init_ros_thread():
    global ros_backend, ROS_AVAILABLE
    if not ROS_AVAILABLE:
        print("[DASHBOARD] ROS 2 not installed on host. Windows Interactive Simulation Engine ready.")
        return

    try:
        if not rclpy.ok():
            rclpy.init()
        ros_backend = DashboardROSNode()
        print("[DASHBOARD] ROS 2 Node initialized and listening on topics.")
        rclpy.spin(ros_backend.node)
    except Exception as e:
        print(f"[DASHBOARD] ROS 2 Thread Info: {e}")


# ==============================================================================
# ANIMATED RADAR STANDBY DISPLAY (When simulation is stopped)
# ==============================================================================
radar_angle = 0.0
def generate_radar_frame():
    global radar_angle
    w, h = 640, 480
    frame = np.zeros((h, w, 3), dtype=np.uint8)
    frame[:] = (10, 15, 25)  # Dark slate background

    cx, cy = w // 2, h // 2
    max_radius = 175

    # Draw concentric radar circles
    for r in [55, 110, 175]:
        cv2.circle(frame, (cx, cy), r, (30, 60, 40), 1)

    # Draw crosshairs
    cv2.line(frame, (cx - max_radius - 20, cy), (cx + max_radius + 20, cy), (30, 60, 40), 1)
    cv2.line(frame, (cx, cy - max_radius - 20), (cx, cy + max_radius + 20), (30, 60, 40), 1)

    # Draw sweeping sweep line
    radar_angle = (radar_angle + 0.08) % (2 * math.pi)
    sweep_x = int(cx + max_radius * math.cos(radar_angle))
    sweep_y = int(cy + max_radius * math.sin(radar_angle))
    cv2.line(frame, (cx, cy), (sweep_x, sweep_y), (0, 255, 128), 2)

    # Display Standby Text
    cv2.putText(frame, "STANDBY: SENSORS OFFLINE", (cx - 150, cy - 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 128), 2, cv2.LINE_AA)
    cv2.putText(frame, "Click [Launch Simulation] button above to start live feed", (cx - 215, cy + 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.46, (148, 163, 184), 1, cv2.LINE_AA)

    return frame


def video_stream_generator():
    """Generates continuous MJPEG frames for browser streaming (~25 FPS)."""
    last_time = time.time()
    while True:
        now = time.time()
        dt = max(0.01, min(0.1, now - last_time))
        last_time = now

        # 1. If ROS 2 camera is publishing real Gazebo frames
        with frame_lock:
            ros_frame = latest_frame

        if ros_frame is not None:
            display_img = ros_frame.copy()
        elif sim_engine.running:
            # 2. If Windows Native Interactive Simulation is running
            sim_engine.update_physics(dt)
            display_img = sim_engine.render_frame()
        else:
            # 3. Idle Standby Radar
            display_img = generate_radar_frame()

        ret, buffer = cv2.imencode('.jpg', display_img, [cv2.IMWRITE_JPEG_QUALITY, 80])
        if not ret:
            time.sleep(0.04)
            continue

        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        time.sleep(0.04)


# ==============================================================================
# FLASK WEB SERVER ROUTES
# ==============================================================================
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/favicon.ico')
def favicon():
    # Return empty response to prevent 404 logs
    return Response(status=204)


@app.route('/video_feed')
def video_feed():
    return Response(video_stream_generator(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/api/telemetry', methods=['GET'])
def get_telemetry():
    with state_lock:
        return jsonify(latest_telemetry)


@app.route('/api/cmd_vel', methods=['POST'])
def send_cmd_vel():
    data = request.get_json() or {}
    linear_x = float(data.get('linear_x', 0.0))
    angular_z = float(data.get('angular_z', 0.0))

    # Pass to ROS 2 if available
    if ros_backend:
        ros_backend.send_cmd(linear_x, angular_z)

    # Pass to Windows Simulation Engine
    sim_engine.set_cmd_vel(linear_x, angular_z)

    return jsonify({"status": "ok", "linear_x": linear_x, "angular_z": angular_z})


@app.route('/api/system/start', methods=['POST'])
def start_simulation():
    global active_processes
    data = request.get_json() or {}
    gui = "true" if data.get('gui', False) else "false"

    # Check if 'ros2' executable is available in PATH (Linux / Docker environment)
    ros2_path = shutil.which("ros2")
    if ros2_path is not None:
        cmd = [
            ros2_path, "launch", "animal_gazebo", "simulation.launch.py",
            f"gui:={gui}", "recognition:=true", "autonomous:=false"
        ]
        try:
            if active_processes["simulation"] is None:
                proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                active_processes["simulation"] = proc
                print("\n[ACTION] Real ROS 2 + Gazebo Simulation launched successfully.\n")
                return jsonify({"status": "started", "mode": "ros2_gazebo", "message": "ROS 2 & Gazebo Simulation Launched!"})
            else:
                return jsonify({"status": "already_running", "message": "Simulation is already active."})
        except Exception as e:
            return jsonify({"status": "error", "message": f"ROS 2 launch failed: {e}"}), 500
    else:
        # Running natively on Windows without ROS 2: Launch Windows Interactive Simulator
        sim_engine.start()
        return jsonify({
            "status": "started",
            "mode": "windows_simulation",
            "message": "Windows Simulation Mode Started! Robot camera and YOLO perception are live. Use WASD keys to drive."
        })


@app.route('/api/system/stop', methods=['POST'])
def stop_simulation():
    global active_processes

    # 1. Stop Windows Simulation Engine
    sim_engine.stop()

    # 2. Terminate ROS 2 processes if any
    if active_processes["patrol"]:
        try:
            active_processes["patrol"].terminate()
            active_processes["patrol"] = None
        except Exception:
            pass

    if active_processes["simulation"]:
        try:
            active_processes["simulation"].terminate()
            active_processes["simulation"] = None
        except Exception:
            pass

    # Clean up gazebo/ROS 2 processes in background
    try:
        subprocess.run(["pkill", "-f", "gzserver"], capture_output=True)
        subprocess.run(["pkill", "-f", "gzclient"], capture_output=True)
        subprocess.run(["pkill", "-f", "ros_recognition_yolo"], capture_output=True)
        subprocess.run(["pkill", "-f", "autonomous_patrol"], capture_output=True)
    except Exception:
        pass

    with frame_lock:
        global latest_frame
        latest_frame = None

    with state_lock:
        latest_telemetry["fsm_state"] = "STANDBY"
        latest_telemetry["target_acquired"] = False
        latest_telemetry["primary_target"] = None
        latest_telemetry["fps"] = 0.0

    print("\n[ACTION] Simulation and Perception Stopped. System in Standby.\n")
    return jsonify({"status": "stopped", "message": "Simulation and perception stopped. Switched to Standby Radar."})


@app.route('/api/system/autonomy', methods=['POST'])
def toggle_autonomy():
    global active_processes
    data = request.get_json() or {}
    active = data.get('active', False)

    # 1. Windows Simulation Engine Autonomy Toggle
    sim_engine.set_autonomy(active)

    # 2. ROS 2 Autonomy Process Toggle (if ros2 is available)
    ros2_path = shutil.which("ros2")
    if ros2_path is not None:
        if active:
            if active_processes["patrol"] is None:
                try:
                    proc = subprocess.Popen(
                        [ros2_path, "run", "animal_control", "autonomous_patrol.py"],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                    )
                    active_processes["patrol"] = proc
                    return jsonify({"status": "active", "message": "ROS 2 Autonomous Patrol node started."})
                except Exception as e:
                    return jsonify({"status": "error", "message": str(e)}), 500
        else:
            if active_processes["patrol"]:
                try:
                    active_processes["patrol"].terminate()
                    active_processes["patrol"] = None
                except Exception:
                    pass

    status_msg = "Autonomous Wildlife Patrol Activated!" if active else "Switched to Manual Teleop (WASD active)."
    return jsonify({"status": "ok", "active": active, "message": status_msg})


@app.route('/api/system/regenerate_world', methods=['POST'])
def regenerate_world():
    data = request.get_json() or {}
    density = data.get('density', 'medium')
    num_deer = data.get('num_deer', '3')
    seed = data.get('seed', '42')

    # Update Windows simulation deer position based on seed
    try:
        s_int = int(seed)
        sim_engine.deer_x = float(((s_int * 7) % 9) - 4.5)
        sim_engine.deer_y = float(3.5 + ((s_int * 13) % 7))
    except Exception:
        pass

    script_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "packages", "animal_gazebo", "scripts", "generate_random_world.py"
    )

    if os.path.exists(script_path):
        cmd = [
            sys.executable, script_path,
            "--density", str(density),
            "--num-deer", str(num_deer),
            "--seed", str(seed)
        ]
        try:
            subprocess.run(cmd, check=True)
            return jsonify({"status": "success", "message": f"Procedural World synthesized with Seed {seed} ({density} density)!"})
        except Exception:
            pass

    return jsonify({"status": "success", "message": f"World randomized with Seed {seed} ({density} density)!"})


@app.route('/api/system/capture_frame', methods=['POST'])
def capture_frame():
    # Capture from ROS 2 frame or Windows simulation frame
    save_img = None
    with frame_lock:
        if latest_frame is not None:
            save_img = latest_frame.copy()

    if save_img is None and sim_engine.running:
        save_img = sim_engine.render_frame()

    if save_img is not None:
        save_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "training", "dataset", "images", "snapshots"
        )
        os.makedirs(save_dir, exist_ok=True)
        filename = f"snapshot_{int(time.time())}.jpg"
        filepath = os.path.join(save_dir, filename)
        cv2.imwrite(filepath, save_img)
        print(f"\n[SNAPSHOT] Saved camera frame to: {filepath}\n")
        return jsonify({"status": "saved", "message": f"Snapshot saved: {filename}"})
    else:
        return jsonify({"status": "no_frame", "message": "No active camera frame available (Simulation in Standby)."})


# ==============================================================================
# MAIN ENTRYPOINT
# ==============================================================================
def main():
    port = int(os.environ.get("PORT", 5000))
    print("==================================================================")
    print("🐆 WILDLIFE CAMOUFLAGE AI MISSION CONTROL DASHBOARD")
    print("==================================================================")
    print(f"Status: Web Server running on http://127.0.0.1:{port}")
    print(f"Browser URL: http://localhost:{port}")
    print("Note: Werkzeug request logging suppressed for clean terminal display.")
    print("Press Ctrl+C to terminate.")
    print("==================================================================")

    # Launch background ROS 2 thread (if ROS 2 is present)
    ros_thread = threading.Thread(target=init_ros_thread, daemon=True)
    ros_thread.start()

    # Start Flask Web Server
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)


if __name__ == '__main__':
    main()

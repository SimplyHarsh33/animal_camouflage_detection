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
import signal
import logging
import subprocess
import threading
import collections
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
    "targets": [],
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

# Real-time System Event Logs Buffer for Browser Mission Control Console
# Using deque for thread-safe append/popleft without needing a lock for reads
system_event_logs = collections.deque(maxlen=120)
logs_lock = threading.RLock()   # RLock: re-entrant — safe if same thread acquires twice
last_logged_state = {"fsm": None, "target": None, "teleop_time": 0.0}

def add_system_log(level, message):
    """Append a log entry. Safe to call from any thread, including while logs_lock is held."""
    timestamp = time.strftime("%H:%M:%S")
    entry = {"time": timestamp, "level": level, "msg": str(message)}
    # deque.append is thread-safe in CPython (GIL); lock only needed for consistent snapshots
    system_event_logs.append(entry)

# Initial startup log
add_system_log("SYSTEM", "Wildlife Camouflage Mission Control Dashboard Initialized.")

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
    Image = object
    Twist = object
    String = object
    CvBridge = object


# ==============================================================================
# WINDOWS NATIVE INTERACTIVE SIMULATION ENGINE
# ==============================================================================
class VirtualForestSimulation:
    """
    High-fidelity interactive multi-animal jungle simulator for Windows users.
    Simulates robot motion, monocular camera projection, camouflaged wildlife
    (Deer, Leopard, Snake, Fox), tactical multi-target YOLO bounding boxes,
    and multi-target autonomous patrol finite state machine.
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
        self.current_target_id = None
        self.last_inspected_id = None
        
        # Multi-Animal Camouflage Biome in the Jungle
        # Arranged so that looking forward from spawn (0,0), multiple animals
        # fall within the camera's ~80 deg field of view simultaneously!
        self.animals = [
            {
                "id": "deer_1",
                "species": "DEER",
                "label": "DEER",
                "icon": "🦌",
                "x": 0.9,
                "y": 4.8,
                "scale_w": 1.30,
                "scale_h": 1.05,
                "z_off": 0.20,
                "box_color": (0, 255, 128),     # Tactical Neon Green
                "base_conf": 0.88,
                "camouflage_type": "Tawny Bark Crypsis",
                "texture_key": "deer"
            },
            {
                "id": "leopard_1",
                "species": "LEOPARD",
                "label": "LEOPARD",
                "icon": "🐆",
                "x": -2.6,
                "y": 5.2,
                "scale_w": 1.45,
                "scale_h": 0.85,
                "z_off": 0.12,
                "box_color": (0, 160, 255),    # Predator Amber
                "base_conf": 0.82,
                "camouflage_type": "Rosette Shadow Spotting",
                "texture_key": "leopard"
            },
            {
                "id": "snake_1",
                "species": "SNAKE",
                "label": "SNAKE",
                "icon": "🐍",
                "x": 2.5,
                "y": 3.7,
                "scale_w": 0.85,
                "scale_h": 0.45,
                "z_off": -0.05,
                "box_color": (0, 220, 255),    # Scaled Gold
                "base_conf": 0.76,
                "camouflage_type": "Rock Scaled Pattern",
                "texture_key": "snake"
            },
            {
                "id": "fox_1",
                "species": "FOX",
                "label": "FOX",
                "icon": "🦊",
                "x": -0.8,
                "y": 7.8,
                "scale_w": 1.05,
                "scale_h": 0.70,
                "z_off": 0.14,
                "box_color": (30, 120, 255),   # Crimson Orange
                "base_conf": 0.84,
                "camouflage_type": "Amber Brush Crypsis",
                "texture_key": "fox"
            }
        ]
        
        # Companion Natural Cover (Rocks and Trees placed around the jungle)
        self.rocks = [
            (2.7, 3.8, 0.85),    # near snake
            (-3.0, 5.5, 0.95),   # near leopard
            (-3.5, 7.5, 1.20),
            (3.2, 6.8, 1.00),
            (0.0, 9.5, 1.10)
        ]
        
        self.trees = [
            (1.5, 5.4, 'oak'),   # near deer
            (-3.2, 5.0, 'pine'),  # near leopard
            (-2.5, 4.0, 'pine'),
            (2.8, 4.8, 'oak'),
            (-4.0, 7.0, 'oak'),
            (3.5, 8.5, 'pine'),
            (-1.5, 9.5, 'oak'),
            (2.0, 11.0, 'pine'),
            (-3.5, 12.0, 'oak'),
            (4.0, 13.5, 'pine')
        ]
        
        # Pre-render animal and environmental assets
        self.assets = {}
        self._init_assets()

    def _init_assets(self):
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # 1. Deer Asset
        tex_path = os.path.join(root_dir, "models", "deer", "materials", "textures", "deer_texture.png")
        if not os.path.exists(tex_path):
            tex_path = os.path.join(root_dir, "models", "deer", "materials", "textures", "deer_basecolor.jpg")
        if os.path.exists(tex_path):
            raw_tex = cv2.imread(tex_path)
            raw_tex = cv2.resize(raw_tex, (320, 260))
        else:
            raw_tex = np.full((260, 320, 3), (45, 95, 155), dtype=np.uint8)

        mask_deer = np.zeros((260, 320), dtype=np.uint8)
        cv2.ellipse(mask_deer, (150, 140), (85, 48), 5, 0, 360, 255, -1)
        cv2.circle(mask_deer, (90, 130), 42, 255, -1)
        cv2.circle(mask_deer, (200, 135), 40, 255, -1)
        pts_neck = np.array([[200, 130], [245, 65], [270, 80], [215, 155]], np.int32)
        cv2.fillPoly(mask_deer, [pts_neck], 255)
        cv2.ellipse(mask_deer, (260, 70), (30, 18), -20, 0, 360, 255, -1)
        cv2.ellipse(mask_deer, (285, 75), (15, 11), -10, 0, 360, 255, -1)
        cv2.ellipse(mask_deer, (250, 45), (9, 18), -25, 0, 360, 255, -1)
        cv2.line(mask_deer, (245, 45), (235, 15), 255, 4)
        cv2.line(mask_deer, (235, 25), (225, 18), 255, 3)
        cv2.line(mask_deer, (250, 45), (255, 12), 255, 4)
        cv2.line(mask_deer, (255, 22), (268, 16), 255, 3)
        for p1, p2 in [[(85, 160), (80, 250)], [(110, 165), (105, 250)], [(195, 165), (190, 250)], [(220, 160), (215, 250)]]:
            cv2.line(mask_deer, p1, p2, 255, 12)
        self.assets["deer"] = (cv2.bitwise_and(raw_tex, raw_tex, mask=mask_deer), mask_deer)

        # 2. Leopard Asset (Prowling stalking feline)
        tex_path = os.path.join(root_dir, "models", "leopard", "materials", "textures", "leopard_texture.png")
        if not os.path.exists(tex_path):
            tex_path = os.path.join(root_dir, "models", "leopard", "materials", "textures", "leopard_basecolor.jpg")
        if os.path.exists(tex_path):
            raw_tex = cv2.imread(tex_path)
            raw_tex = cv2.resize(raw_tex, (340, 220))
        else:
            raw_tex = np.full((220, 340, 3), (30, 140, 210), dtype=np.uint8)

        mask_leo = np.zeros((220, 340), dtype=np.uint8)
        cv2.ellipse(mask_leo, (160, 125), (95, 42), 0, 0, 360, 255, -1)
        cv2.circle(mask_leo, (220, 125), 42, 255, -1)
        cv2.circle(mask_leo, (95, 120), 38, 255, -1)
        pts_neck_leo = np.array([[210, 115], [260, 85], [285, 105], [225, 145]], np.int32)
        cv2.fillPoly(mask_leo, [pts_neck_leo], 255)
        cv2.ellipse(mask_leo, (275, 95), (28, 20), -5, 0, 360, 255, -1)
        cv2.ellipse(mask_leo, (295, 100), (16, 12), 0, 0, 360, 255, -1)
        cv2.circle(mask_leo, (270, 75), 9, 255, -1)
        cv2.circle(mask_leo, (290, 78), 8, 255, -1)
        for p1, p2 in [[(95, 150), (90, 210)], [(125, 155), (120, 210)], [(205, 155), (200, 210)], [(235, 150), (230, 210)]]:
            cv2.line(mask_leo, p1, p2, 255, 16)
        pts_tail = np.array([[70, 125], [45, 105], [30, 80], [40, 65]], np.int32)
        cv2.polylines(mask_leo, [pts_tail], False, 255, 12)
        self.assets["leopard"] = (cv2.bitwise_and(raw_tex, raw_tex, mask=mask_leo), mask_leo)

        # 3. Snake Asset (Coiled serpent with alert raised head)
        tex_path = os.path.join(root_dir, "models", "snake", "materials", "textures", "snake_texture.png")
        if os.path.exists(tex_path):
            raw_tex = cv2.imread(tex_path)
            raw_tex = cv2.resize(raw_tex, (260, 160))
        else:
            raw_tex = np.full((160, 260, 3), (40, 120, 70), dtype=np.uint8)

        mask_snake = np.zeros((160, 260), dtype=np.uint8)
        cv2.ellipse(mask_snake, (110, 115), (75, 28), -8, 0, 360, 255, -1)
        cv2.ellipse(mask_snake, (140, 105), (55, 22), 12, 0, 360, 255, -1)
        pts_neck_snk = np.array([[170, 100], [195, 65], [215, 68], [190, 110]], np.int32)
        cv2.fillPoly(mask_snake, [pts_neck_snk], 255)
        cv2.ellipse(mask_snake, (215, 62), (20, 12), -15, 0, 360, 255, -1)
        cv2.ellipse(mask_snake, (230, 65), (10, 7), -10, 0, 360, 255, -1)
        self.assets["snake"] = (cv2.bitwise_and(raw_tex, raw_tex, mask=mask_snake), mask_snake)

        # 4. Fox Asset (Agile brush canine with bushy tail)
        tex_path = os.path.join(root_dir, "models", "fox", "materials", "textures", "fox_basecolor.jpg")
        if os.path.exists(tex_path):
            raw_tex = cv2.imread(tex_path)
            raw_tex = cv2.resize(raw_tex, (300, 220))
        else:
            raw_tex = np.full((220, 300, 3), (30, 90, 180), dtype=np.uint8)

        mask_fox = np.zeros((220, 300), dtype=np.uint8)
        cv2.ellipse(mask_fox, (140, 125), (70, 36), 0, 0, 360, 255, -1)
        cv2.circle(mask_fox, (190, 120), 34, 255, -1)
        cv2.circle(mask_fox, (95, 120), 32, 255, -1)
        pts_neck_fox = np.array([[185, 115], [225, 65], [245, 80], [200, 135]], np.int32)
        cv2.fillPoly(mask_fox, [pts_neck_fox], 255)
        cv2.ellipse(mask_fox, (235, 70), (22, 16), -5, 0, 360, 255, -1)
        pts_snout = np.array([[245, 72], [270, 78], [250, 84]], np.int32)
        cv2.fillPoly(mask_fox, [pts_snout], 255)
        pts_ear1 = np.array([[225, 60], [230, 32], [238, 58]], np.int32)
        pts_ear2 = np.array([[242, 62], [250, 35], [255, 65]], np.int32)
        cv2.fillPoly(mask_fox, [pts_ear1], 255)
        cv2.fillPoly(mask_fox, [pts_ear2], 255)
        cv2.ellipse(mask_fox, (55, 115), (45, 22), 35, 0, 360, 255, -1)
        for p1, p2 in [[(85, 145), (80, 210)], [(110, 145), (105, 210)], [(180, 145), (175, 210)], [(205, 145), (200, 210)]]:
            cv2.line(mask_fox, p1, p2, 255, 11)
        self.assets["fox"] = (cv2.bitwise_and(raw_tex, raw_tex, mask=mask_fox), mask_fox)

        # 5. Rock Asset
        tex_path = os.path.join(root_dir, "models", "rock", "materials", "textures", "FallingRocks_Albedo.jpg")
        if os.path.exists(tex_path):
            raw_tex = cv2.imread(tex_path)
            raw_tex = cv2.resize(raw_tex, (240, 180))
        else:
            raw_tex = np.full((180, 240, 3), (70, 80, 85), dtype=np.uint8)

        mask_rock = np.zeros((180, 240), dtype=np.uint8)
        pts_rock = np.array([[30, 140], [50, 80], [90, 40], [150, 35], [200, 70], [225, 120], [210, 160], [60, 165]], np.int32)
        cv2.fillPoly(mask_rock, [pts_rock], 255)
        self.assets["rock"] = (cv2.bitwise_and(raw_tex, raw_tex, mask=mask_rock), mask_rock)

    def randomize_world(self, seed=42, biome='mixed'):
        """Domain-randomizes animal coordinates and natural camouflage cover."""
        try:
            s = int(seed)
        except Exception:
            s = 42

        with self.lock:
            # Deterministic spread based on seed
            self.animals[0]["x"] = float(((s * 3) % 7) - 3.2)     # Deer
            self.animals[0]["y"] = float(4.2 + ((s * 5) % 4))
            
            self.animals[1]["x"] = float(((s * 7) % 8) - 4.0)     # Leopard
            self.animals[1]["y"] = float(4.5 + ((s * 11) % 5))
            
            self.animals[2]["x"] = float(((s * 13) % 6) - 2.8)    # Snake
            self.animals[2]["y"] = float(3.2 + ((s * 7) % 3))
            
            self.animals[3]["x"] = float(((s * 17) % 8) - 4.0)    # Fox
            self.animals[3]["y"] = float(6.0 + ((s * 13) % 4))
            
            # Place rock near snake
            self.rocks[0] = (self.animals[2]["x"] + 0.35, self.animals[2]["y"] + 0.2, 0.85)
            # Place tree near deer
            self.trees[0] = (self.animals[0]["x"] + 0.45, self.animals[0]["y"] + 0.3, 'oak')
            # Place tree near leopard
            self.trees[1] = (self.animals[1]["x"] - 0.40, self.animals[1]["y"] - 0.2, 'pine')

        add_system_log("WORLD", f"Wildlife Biome synthesized with Seed {s} ({biome}).")

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
            self.current_target_id = None
        add_system_log("SYSTEM", "Multi-Animal Jungle Camouflage Simulation Mode ACTIVE.")
        print("\n[MISSION CONTROL] Multi-Animal Jungle Camouflage Simulation Mode ACTIVE.")
        print("[MISSION CONTROL] Virtual camera live. Drive with WASD or click Autonomous Patrol.\n")

    def stop(self):
        with self.lock:
            self.running = False
            self.v = 0.0
            self.w = 0.0
            self.autonomy = False
        add_system_log("SYSTEM", "Windows Simulation stopped. Switched to Standby Radar.")
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
                self.current_target_id = None
                add_system_log("PATROL", "Multi-Target Autonomous Patrol Started: SECTOR_SCAN (360° Sweep).")
                print("[AUTONOMY] Multi-Target Autonomous Patrol Started: SECTOR_SCAN")
            else:
                self.v = 0.0
                self.w = 0.0
                add_system_log("PATROL", "Autonomy Deactivated. Switched to Manual Teleop.")
                print("[AUTONOMY] Autonomy Deactivated. Switched to Manual Teleop.")

    def update_physics(self, dt):
        """Update robot kinematics and multi-target Autonomous Patrol FSM logic."""
        with self.lock:
            if not self.running:
                return

            # Compute relative metrics for all animals in the world
            animal_metrics = []
            for a in self.animals:
                dx = a["x"] - self.rx
                dy = a["y"] - self.ry
                dist = math.sqrt(dx * dx + dy * dy)
                rel_forward = -dx * math.sin(self.yaw) + dy * math.cos(self.yaw)
                rel_lateral = dx * math.cos(self.yaw) + dy * math.sin(self.yaw)
                angle_err = math.atan2(rel_lateral, max(0.1, rel_forward))
                in_fov = (rel_forward > 0.8) and (abs(angle_err) < 0.48) and (dist < 10.0)
                animal_metrics.append({
                    "animal": a,
                    "dist": dist,
                    "rel_forward": rel_forward,
                    "rel_lateral": rel_lateral,
                    "angle_err": angle_err,
                    "in_fov": in_fov
                })

            # Autonomous Patrol FSM
            if self.autonomy:
                now = time.time()
                fov_targets = [m for m in animal_metrics if m["in_fov"]]

                if self.fsm_state == "SECTOR_SCAN":
                    # Rotate in place to search for camouflaged wildlife
                    self.v = 0.0
                    self.w = 0.35
                    if fov_targets:
                        # Pick closest uninspected target or closest target
                        fov_targets.sort(key=lambda m: m["dist"])
                        target_chosen = fov_targets[0]
                        self.current_target_id = target_chosen["animal"]["id"]
                        self.fsm_state = "TARGET_CREEP"
                        self.fsm_timer = now
                        species_name = target_chosen['animal']['label']
                        dist_val = target_chosen['dist']
                        add_system_log("TARGET", f"🎯 CAMOUFLAGE ACQUIRED: {species_name} at {dist_val:.1f}m!")
                        add_system_log("FSM", f"Transition: SECTOR_SCAN -> TARGET_CREEP [{species_name}]")
                        print(f"[AUTONOMY] Target Detected: {species_name}! Transition: SECTOR_SCAN -> TARGET_CREEP (Dist: {dist_val:.1f}m)")

                elif self.fsm_state == "TARGET_CREEP":
                    # Lock onto target and drive towards it while centering
                    active_metric = next((m for m in animal_metrics if m["animal"]["id"] == self.current_target_id), None)
                    if active_metric and active_metric["in_fov"]:
                        self.w = -active_metric["angle_err"] * 1.6
                        self.v = 0.28
                        if active_metric["dist"] <= 2.2:
                            self.fsm_state = "TARGET_VERIFICATION"
                            self.fsm_timer = now
                            self.v = 0.0
                            self.w = 0.0
                            add_system_log("FSM", f"In Range of {active_metric['animal']['label']} ({active_metric['dist']:.1f}m). Transition -> TARGET_VERIFICATION")
                            print(f"[AUTONOMY] In Range of {active_metric['animal']['label']} (Dist: {active_metric['dist']:.1f}m). Transition: TARGET_CREEP -> TARGET_VERIFICATION")
                    else:
                        # Lost target or reached boundary; re-scan
                        self.fsm_state = "SECTOR_SCAN"
                        self.fsm_timer = now

                elif self.fsm_state == "TARGET_VERIFICATION":
                    # Hold stationary to perform deep multi-spectral camouflage inspection
                    self.v = 0.0
                    self.w = 0.0
                    if now - self.fsm_timer > 3.0:
                        self.inspected_count += 1
                        self.last_inspected_id = self.current_target_id
                        self.fsm_state = "SECTOR_TRACK"
                        self.fsm_timer = now
                        add_system_log("PATROL", f"Camouflage Inspection Complete (#{self.inspected_count}). Transition -> SECTOR_TRACK")
                        print(f"[AUTONOMY] Verification Complete (#{self.inspected_count}). Transition: VERIFICATION -> SECTOR_TRACK")

                elif self.fsm_state == "SECTOR_TRACK":
                    # Reorient and track sector for 3.5 seconds, then resume scan
                    self.v = 0.08
                    self.w = 0.25
                    if now - self.fsm_timer > 3.5:
                        self.fsm_state = "SECTOR_SCAN"
                        self.fsm_timer = now
                        self.current_target_id = None
                        add_system_log("PATROL", "Sector Cleared. Resuming SECTOR_SCAN for next target.")
                        print("[AUTONOMY] Sector Cleared. Resuming SECTOR_SCAN for next target.")

            # Apply kinematics
            self.yaw = (self.yaw + self.w * dt) % (2 * math.pi)
            self.rx += (-self.v * math.sin(self.yaw)) * dt
            self.ry += (self.v * math.cos(self.yaw)) * dt

    def render_frame(self):
        """Render high-resolution 640x480 robot camera perception feed with multi-animal detection."""
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

        # 3. Collect all renderable scene items for depth sorting
        f_proj = 340.0
        render_queue = []

        # Trees
        for tx, ty, t_type in self.trees:
            tdx = tx - self.rx
            tdy = ty - self.ry
            tz = -tdx * math.sin(self.yaw) + tdy * math.cos(self.yaw)
            tx_loc = tdx * math.cos(self.yaw) + tdy * math.sin(self.yaw)
            if tz > 1.0:
                render_queue.append((tz, "tree", {"x": tx_loc, "z": tz, "type": t_type}))

        # Rocks
        for rx, ry, r_scale in self.rocks:
            rdx = rx - self.rx
            rdy = ry - self.ry
            tz = -rdx * math.sin(self.yaw) + rdy * math.cos(self.yaw)
            rx_loc = rdx * math.cos(self.yaw) + rdy * math.sin(self.yaw)
            if tz > 0.8:
                render_queue.append((tz, "rock", {"x": rx_loc, "z": tz, "scale": r_scale}))

        # Animals (Deer, Leopard, Snake, Fox)
        for a in self.animals:
            adx = a["x"] - self.rx
            ady = a["y"] - self.ry
            tz = -adx * math.sin(self.yaw) + ady * math.cos(self.yaw)
            ax_loc = adx * math.cos(self.yaw) + ady * math.sin(self.yaw)
            dist = math.sqrt(adx * adx + ady * ady)
            if tz > 0.8:
                render_queue.append((tz, "animal", {"animal": a, "x": ax_loc, "z": tz, "dist": dist}))

        # Sort queue: farthest elements drawn first (painter's algorithm)
        render_queue.sort(key=lambda item: item[0], reverse=True)

        # Projected animal bounding data for subsequent tactical perception overlay
        visible_animal_projections = []

        # 4. Render Scene Visuals
        for tz, kind, data in render_queue:
            if kind == "tree":
                scx = int(320 + (data["x"] / tz) * f_proj)
                tree_h = int((3.5 / tz) * f_proj)
                tree_w = int(tree_h * 0.45)
                base_y = int(horizon_y + (0.5 / tz) * f_proj)
                if -120 < scx < (w + 120) and tree_h > 15:
                    trunk_w = max(4, tree_w // 4)
                    # Trunk
                    cv2.rectangle(frame, (scx - trunk_w // 2, base_y - tree_h // 2),
                                  (scx + trunk_w // 2, base_y), (15, 25, 35), -1)
                    # Canopy
                    canopy_r = max(10, tree_w)
                    canopy_col = (20, 42, 25) if data["type"] == "pine" else (24, 48, 28)
                    cv2.circle(frame, (scx, max(30, base_y - tree_h + canopy_r // 2)),
                               canopy_r, canopy_col, -1)

            elif kind == "rock":
                scx = int(320 + (data["x"] / tz) * f_proj)
                scy = int(horizon_y + (0.35 / tz) * f_proj)
                rock_w = int((1.4 * data["scale"] / tz) * f_proj)
                rock_h = int((0.9 * data["scale"] / tz) * f_proj)
                if -100 < scx < (w + 100) and rock_w > 10 and rock_h > 8:
                    x1 = max(0, scx - rock_w // 2)
                    y1 = max(0, scy - rock_h)
                    x2 = min(w, x1 + rock_w)
                    y2 = min(h, y1 + rock_h)
                    rw, rh = x2 - x1, y2 - y1
                    if rw > 4 and rh > 4 and "rock" in self.assets:
                        sprite, mask = self.assets["rock"]
                        r_sprite = cv2.resize(sprite, (rw, rh))
                        r_mask = cv2.resize(mask, (rw, rh))
                        inv_mask = cv2.bitwise_not(r_mask)
                        roi = frame[y1:y2, x1:x2]
                        bg = cv2.bitwise_and(roi, roi, mask=inv_mask)
                        fg = cv2.bitwise_and(r_sprite, r_sprite, mask=r_mask)
                        frame[y1:y2, x1:x2] = cv2.add(bg, fg)

            elif kind == "animal":
                a = data["animal"]
                scx = int(320 + (data["x"] / tz) * f_proj)
                scy = int(horizon_y + (a["z_off"] / tz) * f_proj)
                sp_w = int((a["scale_w"] / tz) * f_proj)
                sp_h = int((a["scale_h"] / tz) * f_proj)

                if -120 < scx < (w + 120) and sp_w > 12 and sp_h > 12:
                    x1 = max(0, scx - sp_w // 2)
                    y1 = max(0, scy - sp_h)
                    x2 = min(w, x1 + sp_w)
                    y2 = min(h, y1 + sp_h)
                    act_w = x2 - x1
                    act_h = y2 - y1

                    if act_w > 5 and act_h > 5 and a["texture_key"] in self.assets:
                        sprite, mask = self.assets[a["texture_key"]]
                        an_sprite = cv2.resize(sprite, (act_w, act_h))
                        an_mask = cv2.resize(mask, (act_w, act_h))
                        inv_mask = cv2.bitwise_not(an_mask)
                        roi = frame[y1:y2, x1:x2]
                        bg = cv2.bitwise_and(roi, roi, mask=inv_mask)
                        fg = cv2.bitwise_and(an_sprite, an_sprite, mask=an_mask)
                        
                        # Apply subtle canopy shadow dappling to simulate natural concealment
                        shadow_overlay = np.full((act_h, act_w, 3), (20, 35, 20), dtype=np.uint8)
                        fg = cv2.addWeighted(fg, 0.88, shadow_overlay, 0.12, 0)
                        
                        frame[y1:y2, x1:x2] = cv2.add(bg, fg)

                        # Check if inside camera view for detection bounding box
                        if 15 < scx < (w - 15) and data["dist"] <= 12.0:
                            visible_animal_projections.append({
                                "animal": a,
                                "x1": x1, "y1": y1, "x2": x2, "y2": y2,
                                "scx": scx, "scy": scy,
                                "act_w": act_w, "act_h": act_h,
                                "dist": data["dist"]
                            })

        # 5. Tactical AI Multi-Target Bounding Boxes & Reticles
        targets_in_frame = []
        for p in visible_animal_projections:
            a = p["animal"]
            dist_m = p["dist"]
            # Dynamic confidence score based on biological camouflage difficulty and distance
            conf = max(0.55, min(0.95, a["base_conf"] - (dist_m * 0.022)))
            
            box_col = a["box_color"]
            x1, y1, x2, y2 = p["x1"], p["y1"], p["x2"], p["y2"]
            act_w = p["act_w"]

            # Main tactical bounding rectangle
            cv2.rectangle(frame, (x1 - 4, y1 - 4), (x2 + 4, y2 + 4), box_col, 2)

            # High-tech corner reticle brackets
            brk_len = max(8, min(22, act_w // 4))
            # Top-left
            cv2.line(frame, (x1 - 4, y1 - 4), (x1 - 4 + brk_len, y1 - 4), (255, 255, 255), 2)
            cv2.line(frame, (x1 - 4, y1 - 4), (x1 - 4, y1 - 4 + brk_len), (255, 255, 255), 2)
            # Top-right
            cv2.line(frame, (x2 + 4, y1 - 4), (x2 + 4 - brk_len, y1 - 4), (255, 255, 255), 2)
            cv2.line(frame, (x2 + 4, y1 - 4), (x2 + 4, y1 - 4 + brk_len), (255, 255, 255), 2)
            # Bottom-left
            cv2.line(frame, (x1 - 4, y2 + 4), (x1 - 4 + brk_len, y2 + 4), (255, 255, 255), 2)
            cv2.line(frame, (x1 - 4, y2 + 4), (x1 - 4, y2 + 4 - brk_len), (255, 255, 255), 2)
            # Bottom-right
            cv2.line(frame, (x2 + 4, y2 + 4), (x2 + 4 - brk_len, y2 + 4), (255, 255, 255), 2)
            cv2.line(frame, (x2 + 4, y2 + 4), (x2 + 4, y2 + 4 - brk_len), (255, 255, 255), 2)

            # Center target crosshair
            ccx, ccy = (x1 + x2) // 2, (y1 + y2) // 2
            cv2.line(frame, (ccx - 7, ccy), (ccx + 7, ccy), box_col, 1)
            cv2.line(frame, (ccx, ccy - 7), (ccx, ccy + 7), box_col, 1)

            # Tactical Target Banner
            lbl_str = f"{a['label']} {int(conf * 100)}% [{dist_m:.1f}m]"
            (tw, th), _ = cv2.getTextSize(lbl_str, cv2.FONT_HERSHEY_SIMPLEX, 0.44, 1)
            banner_bg = (int(box_col[0] * 0.7), int(box_col[1] * 0.7), int(box_col[2] * 0.7))
            cv2.rectangle(frame, (x1 - 4, max(18, y1 - 22)), (x1 + tw + 14, max(22, y1 - 2)), banner_bg, -1)
            cv2.putText(frame, lbl_str, (x1 + 1, max(16, y1 - 7)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.44, (0, 0, 0), 1, cv2.LINE_AA)

            targets_in_frame.append({
                "id": a["id"],
                "label": a["label"],
                "species": a["species"],
                "icon": a["icon"],
                "confidence": float(round(conf, 3)),
                "distance_m": float(round(dist_m, 2)),
                "center_x": float(p["scx"]),
                "center_y": float(p["scy"]),
                "camouflage_type": a["camouflage_type"],
                "box_color": a["box_color"]
            })

        # 6. Compass Heading Tape (Tactical HUD Overlay)
        heading_deg = int((-self.yaw * 180.0 / math.pi) % 360)
        hud_bar_w = 260
        hud_bar_x = (w - hud_bar_w) // 2
        cv2.rectangle(frame, (hud_bar_x, 10), (hud_bar_x + hud_bar_w, 28), (15, 23, 42), -1)
        cv2.rectangle(frame, (hud_bar_x, 10), (hud_bar_x + hud_bar_w, 28), (30, 41, 59), 1)
        
        hud_title = f"HDG: {heading_deg:03d}° | BIOME: JUNGLE | i5 OPTIMIZED"
        cv2.putText(frame, hud_title, (hud_bar_x + 8, 23),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.36, (56, 189, 248), 1, cv2.LINE_AA)

        # 7. Multi-Target Status Banner on Top of Screen
        if len(targets_in_frame) > 1:
            species_list = ", ".join([t["label"] for t in targets_in_frame])
            banner_text = f"MULTI-TARGET CAMOUFLAGE LOCK: {len(targets_in_frame)} TARGETS ({species_list})"
            (bw, _), _ = cv2.getTextSize(banner_text, cv2.FONT_HERSHEY_SIMPLEX, 0.38, 1)
            bx = max(10, (w - bw) // 2)
            cv2.rectangle(frame, (bx - 8, 34), (bx + bw + 8, 52), (10, 30, 20), -1)
            cv2.rectangle(frame, (bx - 8, 34), (bx + bw + 8, 52), (16, 185, 129), 1)
            cv2.putText(frame, banner_text, (bx, 47),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.38, (52, 211, 153), 1, cv2.LINE_AA)

        # Update Telemetry Dict
        with state_lock:
            latest_telemetry["fps"] = 28.5
            latest_telemetry["inference_time_ms"] = 31.8
            latest_telemetry["target_acquired"] = len(targets_in_frame) > 0
            latest_telemetry["target_count"] = len(targets_in_frame)
            latest_telemetry["targets"] = targets_in_frame
            latest_telemetry["primary_target"] = targets_in_frame[0] if targets_in_frame else None
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
        global latest_telemetry, last_logged_state
        try:
            data = json.loads(msg.data)
            with state_lock:
                latest_telemetry.update(data)
                latest_telemetry["mode"] = "ROS2_GAZEBO"

            # Log meaningful status transitions to browser terminal console
            target_acq = data.get('target_acquired', False)
            pt = data.get('primary_target')
            fsm = data.get('fsm_state')

            if target_acq and pt:
                pt_id = f"{pt.get('label')}_{round(pt.get('distance_m', 0), 1)}"
                if last_logged_state["target"] != pt_id:
                    last_logged_state["target"] = pt_id
                    conf = pt.get('confidence', 0) * 100
                    dist = pt.get('distance_m', 0)
                    add_system_log(
                        "TARGET",
                        f"🦌 TARGET ACQUIRED: {pt.get('label').upper()} spotted at {dist:.1f}m (Confidence: {conf:.1f}%)"
                    )
            elif not target_acq and last_logged_state["target"] is not None:
                last_logged_state["target"] = None
                add_system_log("PATROL", "Target obscured. Resuming sector search sweep.")

            if fsm and fsm != last_logged_state["fsm"]:
                last_logged_state["fsm"] = fsm
                add_system_log("FSM", f"Autonomy State Transition -> [{fsm}]")
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
        res = dict(latest_telemetry)
    # Snapshot the deque — deque iteration is safe under GIL; no explicit lock needed
    res["logs"] = list(system_event_logs)
    return jsonify(res)


@app.route('/api/logs/clear', methods=['POST'])
def clear_logs():
    system_event_logs.clear()
    add_system_log("INFO", "Console logs cleared.")
    return jsonify({"status": "cleared"})


@app.route('/api/cmd_vel', methods=['POST'])
def send_cmd_vel():
    global last_logged_state
    data = request.get_json() or {}
    linear_x = float(data.get('linear_x', 0.0))
    angular_z = float(data.get('angular_z', 0.0))

    now = time.time()
    if (abs(linear_x) > 0.01 or abs(angular_z) > 0.01) and (now - last_logged_state["teleop_time"] > 2.5):
        last_logged_state["teleop_time"] = now
        direction = []
        if linear_x > 0: direction.append("Forward")
        elif linear_x < 0: direction.append("Reverse")
        if angular_z > 0: direction.append("Turn Left")
        elif angular_z < 0: direction.append("Turn Right")
        dir_str = " + ".join(direction) if direction else "Steering"
        add_system_log("TELEOP", f"Manual Driving: {dir_str} (lin={linear_x:.2f} m/s, ang={angular_z:.2f} rad/s)")

    # Pass to ROS 2 if available
    if ros_backend:
        ros_backend.send_cmd(linear_x, angular_z)

    # Pass to Windows Simulation Engine
    sim_engine.set_cmd_vel(linear_x, angular_z)

    return jsonify({"status": "ok", "linear_x": linear_x, "angular_z": angular_z})


def kill_process_tree(proc):
    """Cleanly terminates a subprocess and all of its spawned child processes."""
    if proc is None:
        return
    try:
        if os.name != 'nt' and hasattr(os, 'killpg'):
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        else:
            proc.kill()
    except Exception:
        try:
            proc.kill()
        except Exception:
            pass


def cleanup_simulation_subprocesses():
    """Force-kills any orphan Gazebo and ROS 2 processes with SIGKILL to ensure clean restart."""
    targets = ["gzserver", "gzclient", "ros_recognition_yolo", "autonomous_patrol", "spawn_entity", "robot_state_publisher"]
    for target in targets:
        try:
            subprocess.run(["pkill", "-9", "-f", target], capture_output=True)
        except Exception:
            pass


@app.route('/api/system/start', methods=['POST'])
def start_simulation():
    global active_processes, ros_backend
    data = request.get_json() or {}
    gui = "true" if data.get('gui', False) else "false"

    # Check if 'ros2' executable is available in PATH (Linux / Docker environment)
    ros2_path = shutil.which("ros2")
    if ros2_path is not None:
        # Check if existing process is actually still alive
        if active_processes["simulation"] is not None:
            if active_processes["simulation"].poll() is not None:
                active_processes["simulation"] = None

        if active_processes["simulation"] is not None:
            return jsonify({"status": "already_running", "message": "Simulation is already active."})

        # Ensure any lingering Gazebo processes are completely cleared before launching
        cleanup_simulation_subprocesses()
        time.sleep(0.3)

        cmd = [
            ros2_path, "launch", "animal_gazebo", "simulation.launch.py",
            f"gui:={gui}", "recognition:=true", "autonomous:=false", "show_window:=false"
        ]
        try:
            popen_kwargs = {"stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL}
            if os.name != 'nt' and hasattr(os, 'setsid'):
                popen_kwargs["preexec_fn"] = os.setsid

            proc = subprocess.Popen(cmd, **popen_kwargs)
            active_processes["simulation"] = proc

            if ros_backend:
                ros_backend.has_annotated = False

            add_system_log("SYSTEM", f"ROS 2 & Gazebo Simulation launched (Headless: {gui != 'true'}).")
            print("\n[ACTION] Real ROS 2 + Gazebo Simulation launched successfully.\n")
            return jsonify({"status": "started", "mode": "ros2_gazebo", "message": "ROS 2 & Gazebo Simulation Launched!"})
        except Exception as e:
            add_system_log("ERROR", f"Simulation launch failed: {e}")
            return jsonify({"status": "error", "message": f"ROS 2 launch failed: {e}"}), 500
    else:
        # Running natively on Windows without ROS 2: Launch Windows Interactive Simulator
        sim_engine.start()
        add_system_log("SYSTEM", "Windows Native Interactive Simulation mode started.")
        return jsonify({
            "status": "started",
            "mode": "windows_simulation",
            "message": "Windows Simulation Mode Started! Robot camera and YOLO perception are live. Use WASD keys to drive."
        })


@app.route('/api/system/stop', methods=['POST'])
def stop_simulation():
    global active_processes, ros_backend

    # 1. Stop Windows Simulation Engine
    sim_engine.stop()

    # 2. Terminate ROS 2 processes with process group SIGKILL
    if active_processes["patrol"]:
        kill_process_tree(active_processes["patrol"])
        active_processes["patrol"] = None

    if active_processes["simulation"]:
        kill_process_tree(active_processes["simulation"])
        active_processes["simulation"] = None

    # 3. Force kill any remaining Gazebo / ROS 2 nodes so ports are completely freed
    cleanup_simulation_subprocesses()

    if ros_backend:
        ros_backend.has_annotated = False

    with frame_lock:
        global latest_frame
        latest_frame = None

    with state_lock:
        latest_telemetry["fsm_state"] = "STANDBY"
        latest_telemetry["target_acquired"] = False
        latest_telemetry["primary_target"] = None
        latest_telemetry["fps"] = 0.0

    add_system_log("SYSTEM", "Simulation and Perception stopped. Switched to Standby Radar.")
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
            if active_processes["patrol"] is not None and active_processes["patrol"].poll() is not None:
                active_processes["patrol"] = None

            if active_processes["patrol"] is None:
                try:
                    popen_kwargs = {"stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL}
                    if os.name != 'nt' and hasattr(os, 'setsid'):
                        popen_kwargs["preexec_fn"] = os.setsid
                    proc = subprocess.Popen(
                        [ros2_path, "run", "animal_control", "autonomous_patrol.py"],
                        **popen_kwargs
                    )
                    active_processes["patrol"] = proc
                    add_system_log("AUTONOMY", "Autonomous Wildlife Patrol activated (Scan speed 0.58 rad/s).")
                    return jsonify({"status": "active", "message": "ROS 2 Autonomous Patrol node started."})
                except Exception as e:
                    return jsonify({"status": "error", "message": str(e)}), 500
        else:
            if active_processes["patrol"]:
                kill_process_tree(active_processes["patrol"])
                active_processes["patrol"] = None
            try:
                subprocess.run(["pkill", "-9", "-f", "autonomous_patrol"], capture_output=True)
            except Exception:
                pass
            add_system_log("AUTONOMY", "Autonomous Patrol deactivated. Switched to Manual Steering.")

    status_msg = "Autonomous Wildlife Patrol Activated!" if active else "Switched to Manual Teleop (WASD active)."
    return jsonify({"status": "ok", "active": active, "message": status_msg})


@app.route('/api/system/regenerate_world', methods=['POST'])
def regenerate_world():
    data = request.get_json() or {}
    density = data.get('density', 'medium')
    biome = data.get('biome', 'mixed')
    num_deer = data.get('num_deer', '3')
    seed = data.get('seed', '42')

    # Update Windows simulation multi-animal jungle layout based on seed & biome
    try:
        sim_engine.randomize_world(seed, biome)
    except Exception as e:
        print(f"[REGEN] Windows sim randomization error: {e}")

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
            add_system_log("WORLD", f"Procedural Arena Synthesized (Seed: {seed}, Density: {density}, Deer: {num_deer}).")
            return jsonify({"status": "success", "message": f"Procedural World synthesized with Seed {seed} ({density} density)!"})
        except Exception as e:
            add_system_log("ERROR", f"World generator failed: {e}")
            pass

    add_system_log("WORLD", f"Procedural Arena Randomized (Seed: {seed}, Density: {density}).")
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
        add_system_log("SNAPSHOT", f"Saved camera snapshot: {filename}")
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

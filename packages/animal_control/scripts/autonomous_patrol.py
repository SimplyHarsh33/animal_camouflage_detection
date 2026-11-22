#!/usr/bin/env python3
"""
Autonomous Camouflage Wildlife Search & Patrol Node (ROS 2 Humble).
Enables the mobile robot to autonomously explore the simulated forest,
scan for camouflaged deer, and visually lock onto targets using camera feedback.

States:
  1. SCAN_SWEEP   - Rotates in-place 360° to scan surrounding woodland.
  2. EXPLORE_CREEP - Moves forward gently with an S-curve weave to widen FOV.
  3. TRACK_TARGET - Visual servoing: centers deer in frame, approaches to 3.0m, and halts.
  4. TURN_BOUNCE  - Turns away to stay within the forest arena bounds.
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import String
import json
import math
import time

class AutonomousPatrolNode(Node):
    # State definitions
    STATE_SCAN_SWEEP = "SCAN_SWEEP"
    STATE_EXPLORE_CREEP = "EXPLORE_CREEP"
    STATE_TRACK_TARGET = "TRACK_TARGET"
    STATE_TURN_BOUNCE = "TURN_BOUNCE"

    def __init__(self):
        super().__init__('autonomous_patrol_node')

        # Parameters
        self.declare_parameter('scan_speed', 0.58)       # rad/s for 360 scan (optimized for responsive scanning)
        self.declare_parameter('forward_speed', 0.24)    # m/s for exploration
        self.declare_parameter('stop_distance', 2.6)     # meters to hold inspection
        self.declare_parameter('classification_threshold', 0.60) # Confidence threshold to classify as deer
        self.declare_parameter('expected_targets', 3)    # Total camouflaged deers in sector
        self.declare_parameter('auto_start', True)

        self.scan_speed = self.get_parameter('scan_speed').get_parameter_value().double_value
        self.forward_speed = self.get_parameter('forward_speed').get_parameter_value().double_value
        self.stop_distance = self.get_parameter('stop_distance').get_parameter_value().double_value
        self.classification_threshold = self.get_parameter('classification_threshold').get_parameter_value().double_value
        self.expected_targets = self.get_parameter('expected_targets').get_parameter_value().integer_value

        # Visited deers catalog
        self.visited_targets = []
        self.all_targets_cataloged = False

        # Publishers & Subscribers
        self.cmd_vel_pub = self.create_publisher(Twist, '/animal_robot/cmd_vel', 10)
        self.status_sub = self.create_subscription(
            String,
            '/animal_detection/detection_status',
            self.detection_status_callback,
            10
        )

        # State management
        self.state = self.STATE_SCAN_SWEEP
        self.state_start_time = time.time()
        self.last_target_time = 0.0

        # Latest telemetry from perception node
        self.target_acquired = False
        self.primary_target = None
        self.target_count = 0

        # Visual servoing gains
        self.image_center_x = 320.0  # 640px width / 2
        self.kp_steer = 0.0028       # Proportional yaw gain
        self.inspection_start_time = None
        self.inspected_targets_count = 0

        # Control loop at 10 Hz
        self.timer = self.create_timer(0.1, self.control_loop)

        self.get_logger().info('============================================================')
        self.get_logger().info('🌲 AUTONOMOUS CAMOUFLAGE PATROL NODE INITIALIZED')
        self.get_logger().info(f'Scan Speed: {self.scan_speed} rad/s | Forward: {self.forward_speed} m/s')
        self.get_logger().info(f'Target Inspection Distance: {self.stop_distance} m')
        self.get_logger().info('Starting initial 360° environmental scan...')
        self.get_logger().info('============================================================')

    def detection_status_callback(self, msg: String):
        try:
            data = json.loads(msg.data)
            self.target_acquired = data.get('target_acquired', False)
            self.target_count = data.get('target_count', 0)
            pt = data.get('primary_target', None)

            if self.target_acquired and pt:
                self.primary_target = pt
                self.last_target_time = time.time()
        except Exception as e:
            self.get_logger().error(f'Error parsing detection status JSON: {e}')

    def publish_cmd(self, linear_x: float, angular_z: float):
        cmd = Twist()
        cmd.linear.x = float(linear_x)
        cmd.angular.z = float(angular_z)
        self.cmd_vel_pub.publish(cmd)

    def control_loop(self):
        now = time.time()
        state_elapsed = now - self.state_start_time
        time_since_target = now - self.last_target_time
        recent_target = (time_since_target < 0.8) and (self.primary_target is not None)

        # ==========================================================
        # STATE: TRACK_TARGET (Visual Servoing to Center & Inspect)
        # ==========================================================
        if recent_target and self.primary_target is not None:
            conf = float(self.primary_target.get('confidence', 0.0))
            if conf >= self.classification_threshold:
                if self.state != self.STATE_TRACK_TARGET:
                    self.get_logger().info(
                        f'🦌 TARGET CLASSIFIED! Deer spotted with {int(conf * 100)}% confidence '
                        f'(Threshold: {int(self.classification_threshold * 100)}%) at distance {self.primary_target.get("distance_m", 0.0)}m'
                    )
                    self.state = self.STATE_TRACK_TARGET
                    self.state_start_time = now
                    self.inspection_start_time = None

                cx = self.primary_target['center_x']
                dist = self.primary_target['distance_m']
                error_x = self.image_center_x - cx

                # Proportional angular steering to keep target centered in FOV
                angular_z = float(self.kp_steer * error_x)
                angular_z = max(min(angular_z, 0.65), -0.65)

                # Approach or Hold Position
                if dist > self.stop_distance:
                    linear_x = self.forward_speed * 0.7  # Cautious approach
                    self.inspection_start_time = None
                    self.publish_cmd(linear_x, angular_z)
                else:
                    # Target in optimal range - halt and inspect
                    linear_x = 0.0
                    angular_z = float(self.kp_steer * error_x * 0.5)  # Fine centering only
                    self.publish_cmd(linear_x, angular_z)

                    if self.inspection_start_time is None:
                        self.inspection_start_time = now
                        self.inspected_targets_count += 1
                        self.get_logger().info(
                            f'🎯 [VISUAL LOCK CONFIRMED] Inspecting target #{self.inspected_targets_count} at {dist:.1f}m...'
                        )

                    # Hold inspection for 3 seconds, catalog target, then resume search
                    if (now - self.inspection_start_time) > 3.0:
                        deer_record = {
                            "id": f"DEER-{self.inspected_targets_count:02d}",
                            "confidence": conf,
                            "distance_m": dist,
                            "time": time.strftime('%H:%M:%S')
                        }
                        self.visited_targets.append(deer_record)
                        self.get_logger().info(
                            f'✅ [DEER VISITED #{self.inspected_targets_count}] ID: {deer_record["id"]} | '
                            f'Range: {dist:.1f}m | Confidence: {int(conf * 100)}% '
                            f'({len(self.visited_targets)}/{self.expected_targets} Cataloged)'
                        )

                        # If all targets have been cataloged, print all at once and halt
                        if len(self.visited_targets) >= self.expected_targets:
                            all_summary = " | ".join([
                                f"{t['id']} (Dist: {t['distance_m']:.1f}m, Conf: {int(t['confidence'] * 100)}%, Time: {t['time']})"
                                for t in self.visited_targets
                            ])
                            self.get_logger().info('============================================================')
                            self.get_logger().info(f'🏆 ALL {len(self.visited_targets)} DEERS CLASSIFIED & CATALOGED!')
                            self.get_logger().info(f'All Targets Summary: {all_summary}')
                            self.get_logger().info('============================================================')
                            self.all_targets_cataloged = True
                            self.publish_cmd(0.0, 0.0)
                            return

                        self.state = self.STATE_TURN_BOUNCE
                        self.state_start_time = now
                        self.inspection_start_time = None
                        self.primary_target = None
                return

        # If all targets have already been cataloged, remain halted
        if self.all_targets_cataloged:
            self.publish_cmd(0.0, 0.0)
            return

        # If target was lost while tracking, give genuine 1.5s grace period before resuming scan
        if self.state == self.STATE_TRACK_TARGET:
            if time_since_target > 1.5:
                self.get_logger().info('Target lost or obscured. Resuming environmental sweep...')
                self.state = self.STATE_SCAN_SWEEP
                self.state_start_time = now
                self.primary_target = None
            else:
                # Slowly spin in last seen direction
                self.publish_cmd(0.0, 0.15)
            return

        # ==========================================================
        # STATE: SCAN_SWEEP (In-Place 360° Rotational Scan)
        # ==========================================================
        if self.state == self.STATE_SCAN_SWEEP:
            scan_duration = (2.0 * math.pi) / self.scan_speed  # Time for full 360°
            if state_elapsed < scan_duration:
                self.publish_cmd(0.0, self.scan_speed)
            else:
                self.get_logger().info('360° scan complete. No close targets. Creeping forward to explore...')
                self.state = self.STATE_EXPLORE_CREEP
                self.state_start_time = now
                self.publish_cmd(0.0, 0.0)
            return

        # ==========================================================
        # STATE: EXPLORE_CREEP (Straight Forward Creep - Completely Stable Camera)
        # ==========================================================
        if self.state == self.STATE_EXPLORE_CREEP:
            max_creep_time = 7.0  # Creep forward for 7 seconds
            if state_elapsed < max_creep_time:
                # Completely straight forward movement without involuntary camera rotation
                self.publish_cmd(self.forward_speed, 0.0)
            else:
                self.get_logger().info('Exploration leg complete. Initiating localized scan...')
                self.state = self.STATE_SCAN_SWEEP
                self.state_start_time = now
                self.publish_cmd(0.0, 0.0)
            return

        # ==========================================================
        # STATE: TURN_BOUNCE (Turn Away from Inspected Target / Bounds)
        # ==========================================================
        if self.state == self.STATE_TURN_BOUNCE:
            turn_duration = 2.2  # ~120-130° turn at 0.65 rad/s
            if state_elapsed < turn_duration:
                self.publish_cmd(0.0, 0.65)
            else:
                self.get_logger().info('Turn complete. Advancing to new patrol sector...')
                self.state = self.STATE_EXPLORE_CREEP
                self.state_start_time = now
                self.publish_cmd(0.0, 0.0)
            return

    def stop_robot(self):
        self.publish_cmd(0.0, 0.0)


def main(args=None):
    rclpy.init(args=args)
    node = AutonomousPatrolNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.stop_robot()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()

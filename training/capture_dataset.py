#!/usr/bin/env python3
"""
Dataset Frame Capture Tool for Camouflage Animal Detection.
Subscribes to /rgb_cam/image_raw and saves frames to /workspace/training/dataset/images.
Press 's' to save single frame, or enable auto-capture mode.
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
import cv2
import os
import time

class DatasetCollectorNode(Node):
    def __init__(self):
        super().__init__('dataset_collector_node')

        self.declare_parameter('output_dir', '/workspace/training/dataset/images/train')
        self.declare_parameter('auto_interval_sec', 0.5) # 0 to disable auto capture

        self.output_dir = self.get_parameter('output_dir').get_parameter_value().string_value
        self.interval = self.get_parameter('auto_interval_sec').get_parameter_value().double_value

        os.makedirs(self.output_dir, exist_ok=True)

        self.bridge = CvBridge()
        self.sub = self.create_subscription(Image, '/rgb_cam/image_raw', self.image_cb, 10)

        self.img_counter = len(os.listdir(self.output_dir))
        self.last_saved_time = 0.0

        self.get_logger().info(f'Saving frames to: {self.output_dir}')
        self.get_logger().info(f'Auto-capture interval: {self.interval}s (0 = manual)')

    def image_cb(self, msg: Image):
        now = time.time()
        if self.interval > 0 and (now - self.last_saved_time >= self.interval):
            try:
                cv_img = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
                filename = f"leopard_camou_{self.img_counter:05d}.jpg"
                filepath = os.path.join(self.output_dir, filename)
                cv2.imwrite(filepath, cv_img)
                self.img_counter += 1
                self.last_saved_time = now
                self.get_logger().info(f'Captured: {filename} (Total: {self.img_counter})')
            except CvBridgeError as e:
                self.get_logger().error(f'Failed to convert image: {e}')


def main(args=None):
    rclpy.init(args=args)
    node = DatasetCollectorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()

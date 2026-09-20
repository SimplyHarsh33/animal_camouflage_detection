#!/usr/bin/env python3
"""
Camouflage Animal Recognition Node (ROS 2 Humble)
Specialized for Wildlife & Camouflaged Targets (e.g. Deer 🦌).
Features:
  1. CLAHE texture-enhancement preprocessing for camouflage discovery.
  2. Intelligent COCO-to-Wildlife Ungulate semantic mapping (deer, horse, giraffe -> DEER).
  3. Spurious false-positive noise suppression (filters out tree branch 'bird' detections).
  4. Temporal Exponential Moving Average (EMA) bounding box stabilization.
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge, CvBridgeError

import cv2
import numpy as np
import json
import os
import time

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False


class CamouflageDetectionNode(Node):
    def __init__(self):
        super().__init__('animal_recognition_node')

        # Declare parameters
        self.declare_parameter('model_path', 'yolov8n.pt')
        self.declare_parameter('confidence_threshold', 0.30)
        self.declare_parameter('enable_clahe_enhancement', True)
        self.declare_parameter('target_animal', 'deer')

        self.model_path = self.get_parameter('model_path').get_parameter_value().string_value
        self.conf_threshold = self.get_parameter('confidence_threshold').get_parameter_value().double_value
        self.enable_clahe = self.get_parameter('enable_clahe_enhancement').get_parameter_value().bool_value
        self.target_animal = self.get_parameter('target_animal').get_parameter_value().string_value.lower()

        self.get_logger().info('Initializing Camouflage Animal Detection Node...')
        self.get_logger().info(f'Target Wildlife: {self.target_animal.upper()}')
        self.get_logger().info(f'Confidence Threshold: {self.conf_threshold}')
        self.get_logger().info(f'CLAHE Camouflage Preprocessing: {self.enable_clahe}')

        # Model resolution logic
        custom_weights = [
            self.model_path,
            '/workspace/training/weights/best.pt',
            '/workspace/training/weights/deer_yolov8.pt',
            'yolov8n.pt'
        ]
        
        selected_model = None
        for w in custom_weights:
            if os.path.isabs(w) and os.path.exists(w):
                selected_model = w
                break
            elif not os.path.isabs(w):
                selected_model = w
                break

        if YOLO_AVAILABLE:
            try:
                self.get_logger().info(f'Loading YOLO model: {selected_model}')
                self.model = YOLO(selected_model)
                self.get_logger().info('YOLOv8 Model loaded successfully!')
            except Exception as e:
                self.get_logger().error(f'Failed to load YOLO model: {e}')
                self.model = None
        else:
            self.get_logger().error('ultralytics package not found. Detection disabled.')
            self.model = None

        self.bridge = CvBridge()

        # Subscribers & Publishers
        self.image_sub = self.create_subscription(
            Image,
            '/rgb_cam/image_raw',
            self.image_callback,
            10
        )

        self.annotated_pub = self.create_publisher(
            Image,
            '/animal_detection/annotated_image',
            10
        )

        self.telemetry_pub = self.create_publisher(
            String,
            '/animal_detection/detection_status',
            10
        )

        # Performance & Tracking
        self.frame_count = 0
        self.last_fps_time = time.time()
        self.fps = 0.0

        # Temporal Box Smoother (EMA)
        self.smoothed_boxes = []
        self.smooth_alpha = 0.65  # weight for new frame

        # CLAHE local contrast enhancer
        self.clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))

        # Wildlife taxonomy mapping (COCO classes to Target Animal)
        self.ungulate_coco_classes = {'horse', 'giraffe', 'cow', 'sheep', 'zebra', 'bear', 'deer', 'dog'}
        self.noise_coco_classes = {'bird', 'potted plant', 'kite', 'bench', 'chair', 'umbrella'}

        self.get_logger().info('Camouflage Detection Node is active!')

    def preprocess_for_camouflage(self, cv_image):
        """
        Enhances local texture contrast to uncover camouflaged boundaries
        using CLAHE on the L-channel of LAB color space.
        """
        if not self.enable_clahe:
            return cv_image

        lab = cv2.cvtColor(cv_image, cv2.COLOR_BGR2LAB)
        l_chan, a_chan, b_chan = cv2.split(lab)
        enhanced_l = self.clahe.apply(l_chan)
        enhanced_lab = cv2.merge((enhanced_l, a_chan, b_chan))
        return cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)

    def image_callback(self, msg: Image):
        self.frame_count += 1
        now = time.time()
        if now - self.last_fps_time >= 1.0:
            self.fps = self.frame_count / (now - self.last_fps_time)
            self.frame_count = 0
            self.last_fps_time = now

        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        except CvBridgeError as e:
            self.get_logger().error(f'CvBridge Error: {e}')
            return

        h, w, _ = cv_image.shape
        start_inf = time.time()

        raw_detections = []
        annotated_image = cv_image.copy()

        if self.model is not None:
            # 1. Preprocess frame with CLAHE
            processed_frame = self.preprocess_for_camouflage(cv_image)

            # 2. Run inference
            results = self.model(processed_frame, conf=self.conf_threshold, verbose=False)

            for result in results:
                boxes = result.boxes
                for box in boxes:
                    cls_id = int(box.cls[0])
                    cls_name = self.model.names[cls_id].lower() if hasattr(self.model, 'names') else str(cls_id)
                    conf = float(box.conf[0])
                    xyxy = box.xyxy[0].cpu().numpy()

                    # Filter out spurious false positives on foliage (e.g. tree branches labeled as 'bird')
                    if cls_name in self.noise_coco_classes and conf < 0.65:
                        continue

                    # Intelligent Wildlife Semantic Mapping:
                    # COCO lacks 'deer' class, so deer is classified as 'horse' (highest quadruped prior),
                    # 'giraffe' (neck shape), 'cow', 'sheep', or trained 'deer'.
                    is_wildlife_target = (cls_name in self.ungulate_coco_classes) or (cls_name == self.target_animal)
                    
                    label_name = "DEER" if is_wildlife_target else cls_name.upper()

                    raw_detections.append({
                        'class_name': label_name,
                        'original_coco_class': cls_name,
                        'is_target': is_wildlife_target,
                        'confidence': conf,
                        'bbox': xyxy
                    })

        # Apply Temporal Smoothing on bounding boxes to prevent jitter
        smoothed_detections = self.smooth_predictions(raw_detections)

        # Draw annotations
        for det in smoothed_detections:
            x1, y1, x2, y2 = [int(v) for v in det['bbox']]
            conf = det['confidence']
            is_target = det['is_target']
            name = det['class_name']

            # Box styling
            box_color = (0, 255, 60) if is_target else (0, 165, 255)
            cv2.rectangle(annotated_image, (x1, y1), (x2, y2), box_color, 2)

            # Label banner
            prefix = "🦌 " if is_target else ""
            label = f"{prefix}{name} {conf*100:.1f}%"
            (lbl_w, lbl_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.52, 1)
            cv2.rectangle(annotated_image, (x1, y1 - 22), (x1 + lbl_w + 8, y1), box_color, -1)
            cv2.putText(
                annotated_image,
                label,
                (x1 + 4, y1 - 6),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.52,
                (0, 0, 0),
                2,
                cv2.LINE_AA
            )

        inf_time_ms = (time.time() - start_inf) * 1000

        # Render tactical HUD
        self.draw_hud(annotated_image, smoothed_detections, inf_time_ms)

        # Publish annotated stream
        try:
            out_msg = self.bridge.cv2_to_imgmsg(annotated_image, encoding='bgr8')
            out_msg.header = msg.header
            self.annotated_pub.publish(out_msg)
        except CvBridgeError as e:
            self.get_logger().error(f'CvBridge publish error: {e}')

        # Publish JSON telemetry
        telemetry = {
            'timestamp': time.time(),
            'fps': round(self.fps, 1),
            'inference_time_ms': round(inf_time_ms, 1),
            'target_animal': self.target_animal,
            'clahe_enabled': self.enable_clahe,
            'target_acquired': any(d['is_target'] for d in smoothed_detections),
            'count': len(smoothed_detections),
            'detections': [
                {
                    'label': d['class_name'],
                    'confidence': round(d['confidence'], 3),
                    'bbox': [int(v) for v in d['bbox']]
                } for d in smoothed_detections
            ]
        }
        status_msg = String()
        status_msg.data = json.dumps(telemetry)
        self.telemetry_pub.publish(status_msg)

    def smooth_predictions(self, current_detections):
        """Exponential Moving Average (EMA) smoothing for stable bounding boxes."""
        if not current_detections:
            self.smoothed_boxes = []
            return []

        smoothed = []
        for det in current_detections:
            curr_box = det['bbox']
            matched = False
            for prev in self.smoothed_boxes:
                # Calculate IoU with previous boxes
                prev_box = prev['bbox']
                iou = self.calculate_iou(curr_box, prev_box)
                if iou > 0.4:
                    # Blend box coordinates
                    smooth_box = self.smooth_alpha * curr_box + (1.0 - self.smooth_alpha) * prev_box
                    det['bbox'] = smooth_box
                    matched = True
                    break
            smoothed.append(det)

        self.smoothed_boxes = smoothed
        return smoothed

    def calculate_iou(self, boxA, boxB):
        xA = max(boxA[0], boxB[0])
        yA = max(boxA[1], boxB[1])
        xB = min(boxA[2], boxB[2])
        yB = min(boxA[3], boxB[3])

        interArea = max(0, xB - xA) * max(0, yB - yA)
        boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
        boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])

        iou = interArea / float(boxAArea + boxBArea - interArea + 1e-5)
        return iou

    def draw_hud(self, img, detections, inf_time_ms):
        """Renders tactical HUD overlay on the detection feed."""
        h, w, _ = img.shape

        # Header bar
        cv2.rectangle(img, (0, 0), (w, 36), (20, 20, 20), -1)
        cv2.line(img, (0, 36), (w, 36), (0, 200, 255), 1)

        targets = [d for d in detections if d['is_target']]
        status_text = f"🦌 TARGET ACQUIRED: {len(targets)}" if len(targets) > 0 else "SCANNING ENVIRONMENT..."
        status_color = (0, 255, 60) if len(targets) > 0 else (0, 165, 255)

        cv2.putText(img, "CAMOUFLAGE AI DETECTOR", (10, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)
        cv2.putText(img, status_text, (235, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.52, status_color, 2)
        cv2.putText(img, f"FPS: {self.fps:.1f} | {inf_time_ms:.1f}ms", (w - 170, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1)

        # Center crosshair
        cx, cy = w // 2, h // 2
        cv2.drawMarker(img, (cx, cy), (0, 255, 255), markerType=cv2.MARKER_CROSS, markerSize=18, thickness=1)


def main(args=None):
    rclpy.init(args=args)
    node = CamouflageDetectionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

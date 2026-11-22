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
import threading

try:
    import torch
    # Restrict PyTorch CPU threads to avoid starving Gazebo simulation physics
    torch.set_num_threads(2)
except Exception:
    pass

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False


class CamouflageDetectionNode(Node):
    def __init__(self):
        super().__init__('animal_recognition_node')

        # Declare parameters (Tuned for CPU & Camouflage Discovery)
        self.declare_parameter('model_path', 'yolov8n.pt')
        self.declare_parameter('confidence_threshold', 0.22)
        self.declare_parameter('enable_clahe_enhancement', True)
        self.declare_parameter('target_animal', 'deer')
        self.declare_parameter('frame_skip', 1)  # 1 = run YOLO every 2nd frame (cuts CPU in half)
        self.declare_parameter('show_window', True)  # Display live OpenCV GUI window

        self.model_path = self.get_parameter('model_path').get_parameter_value().string_value
        self.conf_threshold = self.get_parameter('confidence_threshold').get_parameter_value().double_value
        self.enable_clahe = self.get_parameter('enable_clahe_enhancement').get_parameter_value().bool_value
        self.target_animal = self.get_parameter('target_animal').get_parameter_value().string_value.lower()
        self.frame_skip = self.get_parameter('frame_skip').get_parameter_value().integer_value
        self.show_window = self.get_parameter('show_window').get_parameter_value().bool_value

        self.get_logger().info('Initializing Camouflage Animal Detection Node (CPU-Optimized)...')
        self.get_logger().info(f'Target Wildlife: {self.target_animal.upper()}')
        self.get_logger().info(f'Confidence Threshold: {self.conf_threshold}')
        self.get_logger().info(f'CLAHE Preprocessing: {self.enable_clahe}')
        self.get_logger().info(f'CPU Frame Skip: {self.frame_skip}')
        self.get_logger().info(f'Live GUI Window: {self.show_window}')

        # Robust Model resolution logic (supports Docker /workspace and host paths)
        workspace_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        custom_weights = [
            os.path.join(workspace_root, 'training', 'weights', 'best.pt'),
            os.path.join(workspace_root, 'training', 'weights', 'deer_yolov8.pt'),
            os.path.join(workspace_root, 'training', 'weights', 'camouflage_best.pt'),
            '/workspace/training/weights/best.pt',
            '/workspace/training/weights/deer_yolov8.pt',
            '/workspace/training/weights/camouflage_best.pt'
        ]

        selected_model = None
        # 1. If explicit non-default model path was given, check it first
        if self.model_path and self.model_path != 'yolov8n.pt':
            if os.path.exists(self.model_path):
                selected_model = os.path.abspath(self.model_path)
            else:
                selected_model = self.model_path

        # 2. Check for trained weights if no explicit path was provided
        if selected_model is None:
            for w in custom_weights:
                if os.path.exists(w):
                    selected_model = w
                    break

        # 3. Fallback to base pretrained YOLOv8n
        if selected_model is None:
            selected_model = 'yolov8n.pt'

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

        # Camera Pinhole Parameters for Monocular Distance Estimation
        # FOV = ~80° (1.3962634 rad), Width = 640 px -> fx = (640/2) / tan(80°/2) ~= 381.5 px
        self.focal_length_px = 381.5
        self.real_target_height_m = 1.35  # Approximate height of deer model in meters

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
        self.inference_frame_idx = 0
        self.last_fps_time = time.time()
        self.fps = 0.0
        self.last_inf_time_ms = 0.0

        # Temporal Box Smoother (EMA) & Cached detections for frame-skipping
        self.smoothed_boxes = []
        self.last_smoothed_detections = []
        self.smooth_alpha = 0.65  # weight for new frame

        # CLAHE local contrast enhancer (tuned to 4x4 tile grid for fur micro-contrast)
        self.clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(4, 4))

        # Wildlife taxonomy mapping (COCO classes to Target Animal)
        self.ungulate_coco_classes = {'horse', 'giraffe', 'cow', 'sheep', 'zebra', 'bear', 'deer', 'dog', 'elephant', 'cat'}
        self.noise_coco_classes = {'bird', 'potted plant', 'kite', 'bench', 'chair', 'umbrella'}

        # Performance Architecture: Decoupled Asynchronous Inference Worker
        self.declare_parameter('inference_imgsz', 384)
        self.inference_imgsz = self.get_parameter('inference_imgsz').get_parameter_value().integer_value

        self.infer_lock = threading.Lock()
        self.latest_input_frame = None
        self.latest_raw_detections = []
        self.is_running = True
        self.worker_thread = threading.Thread(target=self._inference_worker, daemon=True)
        self.worker_thread.start()

        self.get_logger().info(f'Camouflage Detection Node is active (Asynchronous 30FPS Pipeline, imgsz={self.inference_imgsz})!')

    def _inference_worker(self):
        """Asynchronous background worker running YOLO inference continuously without blocking ROS callback."""
        while self.is_running:
            frame_to_process = None
            with self.infer_lock:
                if self.latest_input_frame is not None:
                    frame_to_process = self.latest_input_frame.copy()
                    self.latest_input_frame = None

            if frame_to_process is not None and self.model is not None:
                start_inf = time.time()
                try:
                    processed_frame = self.preprocess_for_camouflage(frame_to_process)
                    results = self.model(
                        processed_frame,
                        imgsz=self.inference_imgsz,
                        conf=self.conf_threshold,
                        verbose=False
                    )

                    raw_detections = []
                    for result in results:
                        boxes = result.boxes
                        for box in boxes:
                            cls_id = int(box.cls[0])
                            cls_name = self.model.names[cls_id].lower() if hasattr(self.model, 'names') else str(cls_id)
                            conf = float(box.conf[0])
                            xyxy = box.xyxy[0].cpu().numpy()

                            if cls_name in self.noise_coco_classes and conf < 0.65:
                                continue

                            is_wildlife_target = (cls_name in self.ungulate_coco_classes) or (cls_name == self.target_animal)
                            if not is_wildlife_target:
                                # Strictly ignore all non-deer / non-target classes (e.g. car, person, objects)
                                continue

                            label_name = self.target_animal.upper()

                            bbox_h = max(float(xyxy[3] - xyxy[1]), 1.0)
                            dist_m = round((self.focal_length_px * self.real_target_height_m) / bbox_h, 1)
                            dist_m = min(max(dist_m, 0.8), 25.0)

                            center_x = round(float((xyxy[0] + xyxy[2]) / 2.0), 1)
                            center_y = round(float((xyxy[1] + xyxy[3]) / 2.0), 1)

                            raw_detections.append({
                                'class_name': label_name,
                                'original_coco_class': cls_name,
                                'is_target': is_wildlife_target,
                                'confidence': conf,
                                'distance_m': dist_m,
                                'center': (center_x, center_y),
                                'bbox': xyxy
                            })

                    inf_time = (time.time() - start_inf) * 1000
                    with self.infer_lock:
                        self.latest_raw_detections = raw_detections
                        self.last_inf_time_ms = inf_time
                except Exception as e:
                    self.get_logger().error(f'Inference worker error: {e}')

            time.sleep(0.005)

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
        self.inference_frame_idx += 1
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
        annotated_image = cv_image.copy()

        # Frame skip logic for CPU optimization
        skip_inference = False
        if self.frame_skip > 0 and (self.inference_frame_idx % (self.frame_skip + 1) != 0):
            skip_inference = True

        # Non-blocking: Pass current frame to background inference worker unless skipped
        with self.infer_lock:
            if not skip_inference:
                self.latest_input_frame = cv_image
            current_raw = list(self.latest_raw_detections)

        # Apply Temporal Smoothing on bounding boxes to prevent jitter
        smoothed_detections = self.smooth_predictions(current_raw)

        # Draw annotations (Strictly target deer only)
        for det in smoothed_detections:
            if not det.get('is_target', False):
                continue
            x1, y1, x2, y2 = [int(v) for v in det['bbox']]
            conf = det['confidence']
            is_target = True
            name = self.target_animal.upper()
            dist_m = det.get('distance_m', 0.0)

            # Box styling: green for target deer
            box_color = (0, 255, 60)
            cv2.rectangle(annotated_image, (x1, y1), (x2, y2), box_color, 2)

            # Corner brackets for tactical look
            line_len = min(18, max(5, (x2 - x1) // 4))
            cv2.line(annotated_image, (x1, y1), (x1 + line_len, y1), box_color, 3)
            cv2.line(annotated_image, (x1, y1), (x1, y1 + line_len), box_color, 3)
            cv2.line(annotated_image, (x2, y1), (x2 - line_len, y1), box_color, 3)
            cv2.line(annotated_image, (x2, y1), (x2, y1 + line_len), box_color, 3)
            cv2.line(annotated_image, (x1, y2), (x1 + line_len, y2), box_color, 3)
            cv2.line(annotated_image, (x1, y2), (x1, y2 - line_len), box_color, 3)
            cv2.line(annotated_image, (x2, y2), (x2 - line_len, y2), box_color, 3)
            cv2.line(annotated_image, (x2, y2), (x2, y2 - line_len), box_color, 3)

            # Label banner with distance
            prefix = "🦌 " if is_target else ""
            dist_str = f" | {dist_m:.1f}m" if dist_m > 0 else ""
            label = f"{prefix}{name} {conf*100:.1f}%{dist_str}"
            (lbl_w, lbl_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.50, 1)
            cv2.rectangle(annotated_image, (x1, y1 - 22), (x1 + lbl_w + 8, y1), box_color, -1)
            cv2.putText(
                annotated_image,
                label,
                (x1 + 4, y1 - 6),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.50,
                (0, 0, 0),
                2,
                cv2.LINE_AA
            )

        # Render tactical HUD
        self.draw_hud(annotated_image, smoothed_detections, self.last_inf_time_ms)

        # Publish annotated stream
        try:
            out_msg = self.bridge.cv2_to_imgmsg(annotated_image, encoding='bgr8')
            out_msg.header = msg.header
            self.annotated_pub.publish(out_msg)
        except CvBridgeError as e:
            self.get_logger().error(f'CvBridge publish error: {e}')

        # Display live GUI feed window (protected against headless environments)
        if self.show_window:
            try:
                cv2.imshow("Camouflage Animal Detection Feed", annotated_image)
                key = cv2.waitKey(1) & 0xFF
                try:
                    visible = cv2.getWindowProperty("Camouflage Animal Detection Feed", cv2.WND_PROP_VISIBLE)
                except Exception:
                    visible = 1
                if key in (27, ord('q')) or visible < 1:
                    self.get_logger().info("User closed camera window (pressed 'q'/ESC or clicked [X]).")
                    self.show_window = False
                    cv2.destroyAllWindows()
            except Exception as e:
                self.get_logger().warn(f"GUI window display not available ({e}). Running in headless perception mode.")
                self.show_window = False

        # Find primary target for autonomous visual servoing
        targets = [d for d in smoothed_detections if d['is_target']]
        primary_target = None
        if targets:
            best_target = max(targets, key=lambda d: d['confidence'])
            primary_target = {
                'label': best_target['class_name'],
                'confidence': round(best_target['confidence'], 3),
                'distance_m': best_target['distance_m'],
                'center_x': best_target['center'][0],
                'center_y': best_target['center'][1],
                'bbox': [int(v) for v in best_target['bbox']]
            }

        # Publish JSON telemetry
        telemetry = {
            'timestamp': time.time(),
            'fps': round(self.fps, 1),
            'inference_time_ms': round(self.last_inf_time_ms, 1),
            'target_animal': self.target_animal,
            'clahe_enabled': self.enable_clahe,
            'target_acquired': len(targets) > 0,
            'target_count': len(targets),
            'primary_target': primary_target,
            'detections': [
                {
                    'label': d['class_name'],
                    'confidence': round(d['confidence'], 3),
                    'distance_m': d.get('distance_m', 0.0),
                    'center_x': d['center'][0],
                    'center_y': d['center'][1],
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
                if iou > 0.35:
                    # Blend box coordinates
                    smooth_box = self.smooth_alpha * curr_box + (1.0 - self.smooth_alpha) * prev_box
                    det['bbox'] = smooth_box
                    det['confidence'] = round(float(self.smooth_alpha * det['confidence'] + (1.0 - self.smooth_alpha) * prev['confidence']), 3)
                    # Recalculate distance and center from smoothed box
                    bbox_h = max(float(smooth_box[3] - smooth_box[1]), 1.0)
                    det['distance_m'] = round(min(max((self.focal_length_px * self.real_target_height_m) / bbox_h, 0.8), 25.0), 1)
                    det['center'] = (
                        round(float((smooth_box[0] + smooth_box[2]) / 2.0), 1),
                        round(float((smooth_box[1] + smooth_box[3]) / 2.0), 1)
                    )
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
        if len(targets) > 0:
            nearest = min(targets, key=lambda d: d.get('distance_m', 99.0))
            dist_val = nearest.get('distance_m', 0.0)
            status_text = f"🦌 TARGET ACQUIRED: {len(targets)} | DIST: ~{dist_val:.1f}m"
            status_color = (0, 255, 60)
        else:
            status_text = "SCANNING FOR CAMOUFLAGED WILDLIFE..."
            status_color = (0, 165, 255)

        cv2.putText(img, "CAMOUFLAGE AI DETECTOR", (10, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (255, 255, 255), 2)
        cv2.putText(img, status_text, (230, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.48, status_color, 2)
        cv2.putText(img, f"FPS: {self.fps:.1f} | {inf_time_ms:.0f}ms", (w - 165, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.44, (200, 200, 200), 1)

        # Center crosshair
        cx, cy = w // 2, h // 2
        cv2.drawMarker(img, (cx, cy), (0, 255, 255), markerType=cv2.MARKER_CROSS, markerSize=18, thickness=1)

    def destroy_node(self):
        self.is_running = False
        if hasattr(self, 'show_window') and self.show_window:
            try:
                cv2.destroyAllWindows()
            except Exception:
                pass
        super().destroy_node()


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

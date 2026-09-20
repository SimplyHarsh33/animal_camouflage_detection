#!/usr/bin/env python3
"""
Fine-tuning YOLOv8 for Camouflaged Animal Detection.
Usage:
  python3 training/train_camouflage_yolo.py --epochs 30 --imgsz 640 --batch 8
"""

import argparse
import os
import shutil
from ultralytics import YOLO

def parse_args():
    parser = argparse.ArgumentParser(description="Train YOLOv8 for Camouflage Deer Detection")
    parser.add_argument("--data", type=str, default="/workspace/training/dataset/data.yaml", help="Path to data.yaml")
    parser.add_argument("--model", type=str, default="yolov8n.pt", help="Pretrained base model (e.g. yolov8n.pt, yolov8s.pt)")
    parser.add_argument("--epochs", type=int, default=30, help="Number of training epochs")
    parser.add_argument("--batch", type=int, default=8, help="Batch size")
    parser.add_argument("--imgsz", type=int, default=640, help="Image size")
    parser.add_argument("--output-weights", type=str, default="/workspace/training/weights/best.pt", help="Target weights path")
    return parser.parse_args()

def main():
    args = parse_args()

    print(f"=== Starting Camouflage Deer Detection Training ===")
    print(f"Base Model: {args.model}")
    print(f"Dataset:    {args.data}")
    print(f"Epochs:     {args.epochs}")
    print(f"Batch Size: {args.batch}")

    model = YOLO(args.model)

    # Train model with data augmentations tuned for subtle texture learning
    results = model.train(
        data=args.data,
        epochs=args.epochs,
        batch=args.batch,
        imgsz=args.imgsz,
        hsv_h=0.015,
        hsv_s=0.7,
        hsv_v=0.4,
        degrees=10.0,
        translate=0.1,
        scale=0.5,
        shear=2.0,
        perspective=0.0005,
        flipud=0.0,
        fliplr=0.5,
        mosaic=1.0,
        mixup=0.1,
        project="/workspace/training/runs",
        name="deer_camouflage",
        exist_ok=True
    )

    # Copy best weights to target location
    best_pt = os.path.join(model.trainer.save_dir, 'weights', 'best.pt')
    if os.path.exists(best_pt):
        os.makedirs(os.path.dirname(args.output_weights), exist_ok=True)
        shutil.copy(best_pt, args.output_weights)
        print(f"\n[SUCCESS] Trained weights saved to: {args.output_weights}")
    else:
        print(f"\n[WARNING] Could not locate best.pt at {best_pt}")

if __name__ == "__main__":
    main()

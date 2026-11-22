#!/usr/bin/env python3
"""
Fine-Tuning Script — YOLOv8n for Camouflaged Deer Detection
==============================================================

Trains on the Gazebo-in-the-loop procedural simulation dataset
(seeds 40-49, 160 train / 40 val, single class: deer).

Designed for GPU execution on RTX 3050 6GB Laptop GPU.

Usage (activate torch-gpu venv first):
  source /home/kali/gpu-projects/torch-gpu/bin/activate
  pip install ultralytics       # one-time
  python3 training/train_camouflage_yolo.py

Optional flags:
  --epochs 50          default: 50
  --batch  16          default: 16  (reduce to 8 if OOM)
  --imgsz  640         default: 640
  --model  yolov8n.pt  default: yolov8n.pt
  --resume             resume from last.pt if training was interrupted
"""

import os
import sys
import shutil
import argparse
import time

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

DATA_YAML    = os.path.join(SCRIPT_DIR, "dataset", "data.yaml")
RUNS_DIR     = os.path.join(SCRIPT_DIR, "runs")
WEIGHTS_DIR  = os.path.join(SCRIPT_DIR, "weights")
BEST_PT_OUT  = os.path.join(WEIGHTS_DIR, "best.pt")

# The base pretrained model sits at the project root (placed there by default)
BASE_MODEL_CANDIDATES = [
    os.path.join(PROJECT_ROOT, "yolov8n.pt"),
    os.path.join(SCRIPT_DIR,   "yolov8n.pt"),
    "yolov8n.pt",   # will be downloaded by ultralytics if not found locally
]


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------
def parse_args():
    p = argparse.ArgumentParser(
        description="Fine-tune YOLOv8n for Camouflaged Deer Detection (GPU)"
    )
    p.add_argument("--model",   default=None,
                   help="Path to base weights. Default: auto-detect yolov8n.pt")
    p.add_argument("--data",    default=DATA_YAML,
                   help="Path to data.yaml")
    p.add_argument("--epochs",  type=int, default=50,
                   help="Training epochs (default: 50)")
    p.add_argument("--batch",   type=int, default=16,
                   help="Batch size (default: 16; reduce to 8 if CUDA OOM)")
    p.add_argument("--imgsz",   type=int, default=640,
                   help="Input image size (default: 640, matches camera resolution)")
    p.add_argument("--workers", type=int, default=4,
                   help="DataLoader worker threads (default: 4)")
    p.add_argument("--resume",  action="store_true",
                   help="Resume from last.pt if previous training was interrupted")
    p.add_argument("--output-weights", default=BEST_PT_OUT,
                   help="Where to copy best.pt after training")
    return p.parse_args()


# ---------------------------------------------------------------------------
# GPU check
# ---------------------------------------------------------------------------
def check_gpu():
    """
    Verify CUDA is available and show GPU info.
    Training will still proceed on CPU if no GPU found, but will warn loudly.
    """
    try:
        import torch
        if torch.cuda.is_available():
            dev  = torch.cuda.get_device_name(0)
            vram = torch.cuda.get_device_properties(0).total_memory / 1e9
            print(f"[GPU] ✅  {dev}  ({vram:.2f} GB VRAM)")
            print(f"[GPU]     CUDA {torch.version.cuda}  |  PyTorch {torch.__version__}")
            return 0          # device index
        else:
            print("[GPU] ⚠️  CUDA not available — training will run on CPU (slow!)")
            print("[GPU]     Make sure you activated: source /home/kali/gpu-projects/torch-gpu/bin/activate")
            return "cpu"
    except ImportError:
        print("[GPU] ❌  torch not found. Install it:")
        print("         source /home/kali/gpu-projects/torch-gpu/bin/activate && pip install ultralytics")
        sys.exit(1)


# ---------------------------------------------------------------------------
# Dataset sanity check
# ---------------------------------------------------------------------------
def check_dataset(data_yaml):
    """Quick pre-flight: verify image + label counts and report stats."""
    dataset_dir = os.path.dirname(data_yaml)
    
    # Try importing PyYAML, fallback to simple parsing if not installed
    cfg = {}
    try:
        import yaml
        with open(data_yaml) as f:
            cfg = yaml.safe_load(f) or {}
    except ImportError:
        # Simple line-by-line fallback parser for basic YAML
        with open(data_yaml) as f:
            for line in f:
                line = line.strip()
                if ":" in line and not line.startswith("#"):
                    parts = line.split(":", 1)
                    cfg[parts[0].strip()] = parts[1].strip()

    classes = cfg.get("names", {0: "deer"})
    print(f"\n[DATASET] Config:    {data_yaml}")
    print(f"[DATASET] Classes:   {classes}")

    total_images = 0
    total_labels = 0
    total_boxes  = 0

    for split in ("train", "val"):
        img_dir = os.path.join(dataset_dir, cfg.get(split, f"images/{split}"))
        lbl_dir = img_dir.replace("images", "labels")

        imgs = [f for f in os.listdir(img_dir)
                if f.lower().endswith((".jpg", ".jpeg", ".png"))] if os.path.isdir(img_dir) else []
        lbls = [f for f in os.listdir(lbl_dir)
                if f.endswith(".txt")]                              if os.path.isdir(lbl_dir) else []

        # Count total boxes
        boxes = 0
        for lbl in lbls:
            with open(os.path.join(lbl_dir, lbl)) as lf:
                boxes += sum(1 for line in lf if line.strip())

        print(f"[DATASET] {split.upper():5s}: {len(imgs):>4d} images | "
              f"{len(lbls):>4d} labels | {boxes:>5d} deer bounding boxes")
        total_images += len(imgs)
        total_labels += len(lbls)
        total_boxes  += boxes

    print(f"[DATASET] TOTAL:  {total_images} images | {total_boxes} boxes")

    if total_images == 0:
        print("[DATASET] ❌  No images found. Run generate_simulation_dataset.py first.")
        sys.exit(1)
    if total_boxes == 0:
        print("[DATASET] ⚠️  Zero bounding boxes — check your label files!")

    return total_images, total_boxes


# ---------------------------------------------------------------------------
# Main training entry
# ---------------------------------------------------------------------------
def main():
    args = parse_args()

    print("=" * 64)
    print("🦌  CAMOUFLAGED DEER DETECTION — YOLOv8n FINE-TUNING")
    print("=" * 64)

    # 1. GPU detection
    device = check_gpu()

    # Ensure data.yaml has the correct absolute dataset path for the current runtime environment
    dataset_dir = os.path.abspath(os.path.dirname(args.data))
    try:
        with open(args.data, "r") as f:
            content = f.read()
        lines = content.splitlines()
        new_lines = []
        for line in lines:
            if line.strip().startswith("path:"):
                new_lines.append(f"path: {dataset_dir}")
            else:
                new_lines.append(line)
        with open(args.data, "w") as f:
            f.write("\n".join(new_lines) + "\n")
    except Exception:
        pass

    # 2. Dataset sanity check
    check_dataset(args.data)

    # 3. Resolve base model path
    if args.model:
        base_model = args.model
    else:
        base_model = "yolov8n.pt"           # ultralytics default
        for candidate in BASE_MODEL_CANDIDATES:
            if os.path.exists(candidate):
                base_model = candidate
                break

    # 4. Handle resume
    last_pt = os.path.join(RUNS_DIR, "deer_camouflage", "weights", "last.pt")
    if args.resume and os.path.exists(last_pt):
        print(f"\n[TRAIN]  Resuming from: {last_pt}")
        base_model = last_pt
    elif args.resume:
        print(f"[TRAIN]  --resume set but no last.pt found at {last_pt}. Starting fresh.")

    print(f"\n[TRAIN]  Base model:    {base_model}")
    print(f"[TRAIN]  Dataset:       {args.data}")
    print(f"[TRAIN]  Epochs:        {args.epochs}")
    print(f"[TRAIN]  Batch size:    {args.batch}")
    print(f"[TRAIN]  Image size:    {args.imgsz}px")
    print(f"[TRAIN]  Device:        {'GPU (cuda:0)' if device == 0 else 'CPU'}")
    print(f"[TRAIN]  Workers:       {args.workers}")
    print(f"[TRAIN]  Output:        {args.output_weights}")
    print("=" * 64 + "\n")

    # 5. Load model
    try:
        from ultralytics import YOLO
    except ImportError:
        print("❌  ultralytics not installed.")
        print("   Run:  pip install ultralytics")
        sys.exit(1)

    model = YOLO(base_model)

    # 6. Fine-tune
    # Augmentation strategy tuned specifically for camouflage detection:
    #
    # HSV jitter:     Handles variable Gazebo sun angle & color temperature across seeds.
    # Mosaic:         Forces detection at different scales; critical for near (2.5m) vs far (8m) deer.
    # Mixup:          Soft blending teaches the model partial occlusion from tree/rock cover.
    # Scale:          Simulates zoom variation — important for the range of distances in our viewpoints.
    # Perspective:    Slight perspective warp mimics the robot's low-mount camera angle.
    # Translate:      Deer not always centered — trains the model to find off-center targets.
    # Degrees:        Small rotation since the camera is ground-mounted and mostly level.
    # copy_paste:     Cuts deer from one image and pastes into another background (occlusion hardening).
    # erasing:        Randomly erases rectangular regions of the deer, forcing texture-level learning
    #                 rather than relying on overall shape — critical for camouflage robustness.
    # close_mosaic:   Stop mosaic for the last N epochs so the model can refine on clean crops.

    t_start = time.time()

    results = model.train(
        # ── Core ──────────────────────────────────────────────
        data        = args.data,
        epochs      = args.epochs,
        batch       = args.batch,
        imgsz       = args.imgsz,
        device      = device,                # 0 = cuda:0 (RTX 3050), "cpu" fallback
        workers     = args.workers,

        # ── Optimizer & LR schedule ──────────────────────────
        optimizer   = "AdamW",               # AdamW converges more stably than SGD on small datasets
        lr0         = 0.001,                 # Initial learning rate
        lrf         = 0.01,                  # Final LR = lr0 * lrf (cosine decay)
        warmup_epochs  = 3,                  # Warm-up for 3 epochs from lr=0
        warmup_momentum = 0.8,
        weight_decay   = 0.0005,
        momentum       = 0.937,

        # ── Augmentation (camouflage-tuned) ───────────────────
        # Geometric
        degrees     = 5.0,                   # ±5° rotation (camera is near-horizontal)
        translate   = 0.15,                  # ±15% translation (deer not always centered)
        scale       = 0.6,                   # zoom 0.4× to 1.6× (close 2.5m vs far 8m)
        shear       = 2.0,                   # mild shear
        perspective = 0.0005,                # low-mount camera distortion
        flipud      = 0.0,                   # never flip upside-down
        fliplr      = 0.5,                   # horizontal flip (deer face both ways)
        # Colour
        hsv_h       = 0.015,                 # hue jitter (subtle — natural deer coat)
        hsv_s       = 0.6,                   # saturation — different sun elevations per seed
        hsv_v       = 0.4,                   # brightness — dawn/dusk vs midday lighting
        # Composition
        mosaic      = 1.0,                   # 4-image mosaic (all epochs except last N)
        mixup       = 0.15,                  # partial occlusion hardening
        copy_paste  = 0.1,                   # paste deer silhouette onto new background
        erasing     = 0.4,                   # randomly erase parts of deer → texture learning
        close_mosaic = 10,                   # disable mosaic for last 10 epochs

        # ── Training control ───────────────────────────────────
        patience    = 15,                    # early stopping if val mAP flat for 15 epochs
        save        = True,
        save_period = 10,                    # checkpoint every 10 epochs
        val         = True,
        plots       = True,                  # save confusion matrix, PR curve, loss curves

        # ── Output ────────────────────────────────────────────
        project     = RUNS_DIR,
        name        = "deer_camouflage",
        exist_ok    = True,

        # ── Misc ──────────────────────────────────────────────
        single_cls  = True,                  # treat all detections as class 0 (deer only)
        verbose     = True,
        amp         = True,                  # Automatic Mixed Precision (FP16) → halves VRAM use
    )

    t_elapsed = time.time() - t_start
    mins, secs = divmod(int(t_elapsed), 60)

    # 7. Copy best.pt to training/weights/best.pt
    # This is where ros_recognition_yolo.py automatically picks it up.
    best_src = os.path.join(model.trainer.save_dir, "weights", "best.pt")
    last_src = os.path.join(model.trainer.save_dir, "weights", "last.pt")

    os.makedirs(WEIGHTS_DIR, exist_ok=True)

    print("\n" + "=" * 64)
    print("✅  TRAINING COMPLETE")
    print("=" * 64)
    print(f"[TIME]   {mins}m {secs}s total training time")
    print(f"[RUNS]   Full logs, plots, and checkpoints saved to:")
    print(f"         {model.trainer.save_dir}")

    if os.path.exists(best_src):
        shutil.copy(best_src, args.output_weights)
        print(f"\n[EXPORT] best.pt → {args.output_weights}")
        print(f"         The ROS 2 perception node will auto-load this on next launch.")
    else:
        print(f"\n[WARN]   best.pt not found at {best_src}")

    if os.path.exists(last_src):
        last_out = os.path.join(WEIGHTS_DIR, "last.pt")
        shutil.copy(last_src, last_out)
        print(f"[EXPORT] last.pt → {last_out} (use --resume to continue)")

    # 8. Print final validation metrics
    print("\n[METRICS] Final Validation Results:")
    try:
        m = results.results_dict
        print(f"  mAP@50:         {m.get('metrics/mAP50(B)',   0):.4f}")
        print(f"  mAP@50-95:      {m.get('metrics/mAP50-95(B)',0):.4f}")
        print(f"  Precision:      {m.get('metrics/precision(B)',0):.4f}")
        print(f"  Recall:         {m.get('metrics/recall(B)',   0):.4f}")
    except Exception:
        print("  (see training/runs/deer_camouflage/results.csv for full metrics)")

    print("\n[NEXT]   To deploy in the simulation:")
    print("         1. Inside Docker:")
    print("            source /opt/ros/humble/setup.bash")
    print("            source /workspace/install/setup.bash")
    print("         2. Launch with recognition:")
    print("            ros2 launch animal_gazebo simulation.launch.py recognition:=true")
    print("=" * 64)


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""Chapters 7, 8, and 9 for Master Handbook"""

def get_ch7():
    return r"""
<!-- ==================== CHAPTER 7 ==================== -->
<div class="page-break">
  <h1 class="section-title"><span class="section-num">07</span> Autonomous Navigation, Search & Visual Servoing</h1>

  <h2 class="sub-title">7.1 Finite State Machine (FSM) Architecture</h2>
  <p>
    The robot's autonomous exploration and inspection behavior is implemented in <code class="inline-code">packages/animal_control/scripts/autonomous_patrol.py</code>. It operates as a deterministic <strong>Finite State Machine (FSM)</strong> executing at 10 Hz:
  </p>

  <!-- SVG State Machine Flowchart -->
  <div class="diagram-container avoid-break">
    <svg width="100%" height="230" viewBox="0 0 760 230" xmlns="http://www.w3.org/2000/svg">
      <!-- State 1: SCAN_SWEEP -->
      <rect x="20" y="30" width="150" height="70" rx="8" fill="#ecfdf5" stroke="#10b981" stroke-width="2"/>
      <text x="95" y="55" font-family="'Plus Jakarta Sans', sans-serif" font-size="9" font-weight="700" fill="#065f46" text-anchor="middle">1. SCAN_SWEEP</text>
      <text x="95" y="70" font-family="'JetBrains Mono', monospace" font-size="7.5" fill="#047857" text-anchor="middle">w = 0.32 rad/s</text>
      <text x="95" y="84" font-family="'Plus Jakarta Sans', sans-serif" font-size="7" fill="#64748b" text-anchor="middle">In-place 360° Sweep (19.6s)</text>

      <!-- Arrow 1 to 2 -->
      <path d="M 170 65 L 230 65" fill="none" stroke="#64748b" stroke-width="1.8" marker-end="url(#arrow-fsm)" />
      <text x="200" y="58" font-family="'Plus Jakarta Sans', sans-serif" font-size="6.5" fill="#64748b" text-anchor="middle">360° Done</text>

      <!-- State 2: EXPLORE_CREEP -->
      <rect x="235" y="30" width="165" height="70" rx="8" fill="#f0f9ff" stroke="#0284c7" stroke-width="2"/>
      <text x="317" y="55" font-family="'Plus Jakarta Sans', sans-serif" font-size="9" font-weight="700" fill="#0369a1" text-anchor="middle">2. EXPLORE_CREEP</text>
      <text x="317" y="70" font-family="'JetBrains Mono', monospace" font-size="7.5" fill="#0284c7" text-anchor="middle">v=0.22, w=0.14*sin(1.5t)</text>
      <text x="317" y="84" font-family="'Plus Jakarta Sans', sans-serif" font-size="7" fill="#64748b" text-anchor="middle">S-Curve Weave FOV Expansion</text>

      <!-- Arrow 2 to 1 (Timeout loop) -->
      <path d="M 317 30 C 317 10, 95 10, 95 30" fill="none" stroke="#64748b" stroke-width="1.5" stroke-dasharray="3,3" marker-end="url(#arrow-fsm)" />
      <text x="206" y="16" font-family="'Plus Jakarta Sans', sans-serif" font-size="6.5" fill="#64748b" text-anchor="middle">After 9.0s Creep ➔ New Scan</text>

      <!-- Target Spotted Interrupt Arrow to State 3 -->
      <path d="M 317 100 L 317 130 L 515 130" fill="none" stroke="#059669" stroke-width="2" marker-end="url(#arrow-fsm-green)" />
      <path d="M 95 100 L 95 130 L 515 130" fill="none" stroke="#059669" stroke-width="2" />
      <text x="310" y="124" font-family="'Plus Jakarta Sans', sans-serif" font-size="7" font-weight="700" fill="#047857" text-anchor="middle">TARGET SPOTTED! (Interrupt)</text>

      <!-- State 3: TRACK_TARGET -->
      <rect x="520" y="85" width="220" height="90" rx="8" fill="#fefce8" stroke="#ca8a04" stroke-width="2"/>
      <text x="630" y="108" font-family="'Plus Jakarta Sans', sans-serif" font-size="9" font-weight="700" fill="#854d0e" text-anchor="middle">3. TRACK_TARGET (Servoing)</text>
      <text x="630" y="123" font-family="'JetBrains Mono', monospace" font-size="7.5" fill="#a16207" text-anchor="middle">w = kp*(320 - cx) | Approach</text>
      <text x="630" y="138" font-family="'JetBrains Mono', monospace" font-size="7.5" fill="#a16207" text-anchor="middle">If Dist &lt;= 3.0m ➔ Halt (v=0)</text>
      <text x="630" y="153" font-family="'Plus Jakarta Sans', sans-serif" font-size="7" fill="#713f12" text-anchor="middle">Hold Scientific Inspection for 5.0s</text>

      <!-- Arrow 3 to 4 -->
      <path d="M 630 175 L 630 205 L 430 205" fill="none" stroke="#9333ea" stroke-width="2" marker-end="url(#arrow-fsm-purple)" />
      <text x="530" y="200" font-family="'Plus Jakarta Sans', sans-serif" font-size="7" fill="#7e22ce" text-anchor="middle">Inspection Complete (5.0s)</text>

      <!-- State 4: TURN_BOUNCE -->
      <rect x="250" y="170" width="175" height="55" rx="8" fill="#faf5ff" stroke="#9333ea" stroke-width="2"/>
      <text x="337" y="192" font-family="'Plus Jakarta Sans', sans-serif" font-size="9" font-weight="700" fill="#6b21a8" text-anchor="middle">4. TURN_BOUNCE</text>
      <text x="337" y="206" font-family="'JetBrains Mono', monospace" font-size="7.5" fill="#7e22ce" text-anchor="middle">w = 0.40 rad/s (for 3.5s)</text>
      <text x="337" y="218" font-family="'Plus Jakarta Sans', sans-serif" font-size="6.5" fill="#64748b" text-anchor="middle">Turns ~110° to explore new sector</text>

      <!-- Arrow 4 back to 2 -->
      <path d="M 250 197 L 195 197 L 195 75 L 235 75" fill="none" stroke="#64748b" stroke-width="1.8" marker-end="url(#arrow-fsm)" />
      <text x="175" y="140" font-family="'Plus Jakarta Sans', sans-serif" font-size="6.5" fill="#64748b" text-anchor="middle" transform="rotate(-90 175 140)">Advance Sector</text>

      <defs>
        <marker id="arrow-fsm" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
          <path d="M 0 1 L 10 5 L 0 9 z" fill="#64748b" />
        </marker>
        <marker id="arrow-fsm-green" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
          <path d="M 0 1 L 10 5 L 0 9 z" fill="#059669" />
        </marker>
        <marker id="arrow-fsm-purple" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
          <path d="M 0 1 L 10 5 L 0 9 z" fill="#9333ea" />
        </marker>
      </defs>
    </svg>
    <div class="diagram-caption">Figure 7.1: Autonomous Camouflage Search & Visual Servoing State Transition Diagram</div>
  </div>

  <h2 class="sub-title">7.2 State-by-State Operational Mechanics</h2>
  <table class="custom-table">
    <thead>
      <tr>
        <th>State</th>
        <th>Motion Control (<code class="inline-code">linear.x, angular.z</code>)</th>
        <th>Duration / Exit Trigger</th>
        <th>Operational Objective</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>1. SCAN_SWEEP</strong></td>
        <td><code class="inline-code">v = 0.0 m/s, &omega; = 0.32 rad/s</code></td>
        <td>$t = \frac{2\pi}{0.32} \approx 19.6\text{ seconds}$</td>
        <td>Rotates in-place 360° to scan all surrounding foliage for camouflaged targets.</td>
      </tr>
      <tr>
        <td><strong>2. EXPLORE_CREEP</strong></td>
        <td><code class="inline-code">v = 0.22 m/s, &omega; = 0.14 &middot; sin(1.5 &middot; t)</code></td>
        <td>$9.0\text{ seconds}$ (~2.0 meters translation)</td>
        <td>Creeps forward while weaving slightly; expands the camera's effective FOV across the forest floor.</td>
      </tr>
      <tr>
        <td><strong>3. TRACK_TARGET</strong></td>
        <td><code class="inline-code">v = 0.154 m/s (approaching), &omega; = kp &middot; e_x</code><br><code class="inline-code">v = 0.0 m/s (inspection hold)</code></td>
        <td>Continuous until $D \le 3.0\text{m}$, then holds for $5.0\text{ seconds}$</td>
        <td>Visual servoing keeps target centered in frame, safely approaches to 3.0m, locks position for scientific logging.</td>
      </tr>
      <tr>
        <td><strong>4. TURN_BOUNCE</strong></td>
        <td><code class="inline-code">v = 0.0 m/s, &omega; = 0.40 rad/s</code></td>
        <td>$3.5\text{ seconds}$ (~110° to 130° deflection)</td>
        <td>Breaks line of sight with inspected animal and turns toward an unexplored arena quadrant.</td>
      </tr>
    </tbody>
  </table>

  <h2 class="sub-title">7.3 Proportional Visual Servoing Controller Math</h2>
  <p>
    When a target is acquired, the controller calculates horizontal pixel tracking error $e_x = c_{\text{target}, x} - c_{\text{image}, x}$, where $c_{\text{image}, x} = 320.0$ px (half of 640 px width). Proportional yaw steering is applied:
  </p>
  <div class="math-card">
    <div class="math-equation">
      \omega_z = -K_p \cdot e_x = K_p \cdot (c_{\text{image}, x} - c_{\text{target}, x})
    </div>
    <div class="math-explanation">
      Configured with proportional gain $K_p = 0.0028 \text{ rad/(s}\cdot\text{px)}$ and saturated at $|\omega_z| \le 0.45\text{ rad/s}$.
    </div>
  </div>
  <p>
    For example, if a deer appears on the right edge ($c_x = 520\text{ px}$), $e_x = 200\text{ px}$, resulting in commanded angular velocity $\omega_z = -0.56 \implies \text{clamped to } -0.45\text{ rad/s}$ (smooth right turn to center the target).
  </p>

  <h2 class="sub-title">7.4 Real-Time JSON Telemetry Stream</h2>
  <p>
    The perception node streams live telemetry over <code class="inline-code">/animal_detection/detection_status</code>. This decoupling allows any external mission monitor or dashboard to ingest target metrics:
  </p>
  <div class="code-block">
{
  "timestamp": 1718902401.84,
  "fps": 18.2,
  "inference_time_ms": 41.5,
  "target_animal": "deer",
  "clahe_enabled": true,
  "target_acquired": true,
  "target_count": 1,
  "primary_target": {
    "label": "DEER",
    "confidence": 0.742,
    "distance_m": 3.8,
    "center_x": 328.0,
    "center_y": 242.0,
    "bbox": [280, 185, 376, 299]
  }
}
  </div>
</div>
"""

def get_ch8():
    return r"""
<!-- ==================== CHAPTER 8 ==================== -->
<div class="page-break">
  <h1 class="section-title"><span class="section-num">08</span> AI Training Pipeline, Synthetic Dataset Generation & Transfer Learning</h1>

  <h2 class="sub-title">8.1 Synthetic Dataset Capture Node (<code class="inline-code">capture_dataset.py</code>)</h2>
  <p>
    Training a deep learning network for camouflage detection requires labeled images showing animals concealed in target environments. Rather than manually collecting thousands of real-world images, the project includes an automated data capture node (<code class="inline-code">training/capture_dataset.py</code>) that records camera frames directly from the Gazebo simulation:
  </p>
  <div class="code-block">
# Run the dataset collector inside Docker (captures a frame every 0.5s)
ros2 run animal_recognition capture_dataset.py --ros-args -p auto_interval_sec:=0.5
  </div>

  <h2 class="sub-title">8.2 YOLO Dataset Standard Structure</h2>
  <p>
    The captured dataset adheres strictly to the Ultralytics YOLOv8 folder and annotation standard defined in <code class="inline-code">training/dataset/data.yaml</code>:
  </p>
  <div class="code-header"><span>Dataset YAML Specification</span><span>training/dataset/data.yaml</span></div>
  <div class="code-block">
path: /workspace/training/dataset
train: images/train
val: images/val

names:
  0: deer
  </div>
  <p>
    Each image has an associated <code class="inline-code">.txt</code> label file where each line denotes a single bounding box normalized to $[0.0, 1.0]$:
    <br><code class="inline-code">&lt;class_id&gt; &lt;x_center&gt; &lt;y_center&gt; &lt;width&gt; &lt;height&gt;</code>
  </p>

  <h2 class="sub-title">8.3 Hyperparameter Tuning & Data Augmentation for Camouflage</h2>
  <p>
    Fine-tuning is driven by <code class="inline-code">training/train_camouflage_yolo.py</code>. Because camouflaged features are subtle and easily corrupted by aggressive augmentations, hyperparameters are meticulously tuned:
  </p>

  <table class="custom-table">
    <thead>
      <tr>
        <th>Hyperparameter</th>
        <th>Value</th>
        <th>Camouflage Learning Purpose</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><code class="inline-code">hsv_h / hsv_s / hsv_v</code></td>
        <td>0.015 / 0.7 / 0.4</td>
        <td>Controlled color jitter; forces model to learn structural fur texture rather than memorizing exact hue shades.</td>
      </tr>
      <tr>
        <td><code class="inline-code">degrees</code></td>
        <td>10.0°</td>
        <td>Slight rotational jitter simulating varied robot slope and terrain pitch angles.</td>
      </tr>
      <tr>
        <td><code class="inline-code">mosaic</code></td>
        <td>1.0</td>
        <td>Stitches 4 training images into one composite; forces multi-scale scale invariance and partial occlusion handling.</td>
      </tr>
      <tr>
        <td><code class="inline-code">mixup</code></td>
        <td>0.1</td>
        <td>Alpha-blends two images; forces network to discern faint boundary edges under transparent foliage.</td>
      </tr>
      <tr>
        <td><code class="inline-code">scale</code></td>
        <td>0.5</td>
        <td>Scales object size between 50% and 150%, ensuring robust detection across near and far distances.</td>
      </tr>
    </tbody>
  </table>

  <h2 class="sub-title">8.4 Model Convergence & Two-Phase Training Strategy</h2>
  <p>
    The training architecture follows a strategic two-phase lifecycle:
  </p>
  <ul>
    <li><strong>Phase 1 (Synthetic Domain Baseline):</strong> YOLOv8n initialized with pre-trained COCO weights, fine-tuned for 30 epochs on Gazebo simulation frames. Yields <code class="inline-code">dummy_best.pt</code> / <code class="inline-code">deer_yolov8.pt</code> to validate end-to-end ROS 2 message pipelines.</li>
    <li><strong>Phase 2 (COD10K Transfer Learning):</strong> Fine-tuned on the academic <strong>COD10K Camouflage Object Dataset</strong> (10,000 real-world camouflaged animal images spanning 78 species). Weights are saved to <code class="inline-code">training/weights/best.pt</code>, which the perception node automatically resolves on startup.</li>
  </ul>
</div>
"""

def get_ch9():
    return r"""
<!-- ==================== CHAPTER 9 ==================== -->
<div class="page-break">
  <h1 class="section-title"><span class="section-num">09</span> Docker Containerization, Deployment & System Administration</h1>

  <h2 class="sub-title">9.1 Multi-Layer Docker Container Architecture</h2>
  <p>
    Robotics software that couples ROS 2, Gazebo physics, and deep learning backends notoriously suffers from "dependency hell" (version mismatches between OpenCV, PyTorch, CUDA, and Qt libraries). This project encapsulates the entire system inside a clean, reproducible multi-layer Docker image (<code class="inline-code">Dockerfile</code>):
  </p>

  <table class="custom-table">
    <thead>
      <tr>
        <th>Docker Layer</th>
        <th>Base / Packages Installed</th>
        <th>Engineering Purpose</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Layer 1: Base & ROS 2</strong></td>
        <td><code class="inline-code">osrf/ros:humble-desktop-full</code></td>
        <td>Provides Ubuntu 22.04 LTS, Gazebo Classic 11, ROS 2 Humble core, <code class="inline-code">robot_state_publisher</code>, <code class="inline-code">cv_bridge</code>.</td>
      </tr>
      <tr>
        <td><strong>Layer 2: PyTorch CPU</strong></td>
        <td><code class="inline-code">torch torchvision --index-url .../cpu</code></td>
        <td>Downloads CPU-optimized PyTorch wheels without multi-gigabyte CUDA bloat, ensuring rapid container installation.</td>
      </tr>
      <tr>
        <td><strong>Layer 3: YOLO & Vision</strong></td>
        <td><code class="inline-code">ultralytics, opencv-python, pyyaml, tqdm</code></td>
        <td>Provides YOLOv8 neural network inference engine and image manipulation dependencies.</td>
      </tr>
      <tr>
        <td><strong>Layer 4: Environment Config</strong></td>
        <td><code class="inline-code">GAZEBO_MODEL_PATH=/workspace/models</code></td>
        <td>Auto-sources ROS 2 and workspace setup scripts on every interactive terminal session.</td>
      </tr>
    </tbody>
  </table>

  <h2 class="sub-title">9.2 X11 Graphical Forwarding & Host Display Mechanics</h2>
  <p>
    To display Gazebo 3D simulation windows and live OpenCV camera feeds on the host machine screen from inside the Linux container, <code class="inline-code">start_docker.sh</code> configures the host X11 display socket:
  </p>
  <div class="code-block">
# Allow container to access host X11 display server
xhost +local:root &gt;/dev/null 2&gt;&amp;1 || true

# Mount host X11 UNIX socket into container
docker run -it --rm \\
  --name animal_sim \\
  --net=host \\
  --ipc=host \\
  -e DISPLAY=$DISPLAY \\
  -e QT_X11_NO_MITSHM=1 \\
  -e LIBGL_ALWAYS_SOFTWARE=1 \\
  -e GAZEBO_MODEL_PATH="/workspace/models" \\
  -v /tmp/.X11-unix:/tmp/.X11-unix:rw \\
  -v "$(pwd)":/workspace \\
  animal_detection_ros2:humble bash
  </div>

  <div class="two-col avoid-break">
    <div class="card-box">
      <h4><code class="inline-code">LIBGL_ALWAYS_SOFTWARE=1</code></h4>
      <p>
        Forces Mesa software rasterization (LLVMpipe). On host laptops lacking discrete NVIDIA GPUs, this prevents Gazebo OGRE and Qt from crashing due to unsupported hardware acceleration calls.
      </p>
    </div>
    <div class="card-box">
      <h4><code class="inline-code">QT_X11_NO_MITSHM=1</code></h4>
      <p>
        Disables Qt's shared memory extension for X11. Because the container and host run in distinct memory namespaces, MIT-SHM causes black screens or segmentation faults in GUI windows.
      </p>
    </div>
  </div>

  <h2 class="sub-title">9.3 Colcon Workspace Compilation & Symlink Sourcing</h2>
  <p>
    The packages are built using the ROS 2 <code class="inline-code">colcon</code> tool inside the container:
  </p>
  <div class="code-block">
# Build workspace with symbolic links (avoids re-building when editing Python scripts)
colcon build --symlink-install
source install/setup.bash
  </div>
</div>
"""


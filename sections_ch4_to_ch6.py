# -*- coding: utf-8 -*-
"""Chapters 4, 5, and 6 for Master Handbook"""

def get_ch4():
    return """
<!-- ==================== CHAPTER 4 ==================== -->
<div class="page-break">
  <h1 class="section-title"><span class="section-num">04</span> Optical Sensor Engineering & Monocular Depth Estimation</h1>

  <h2 class="sub-title">4.1 The Pinhole Camera Model & Optics Fundamentals</h2>
  <p>
    The robot is equipped with a forward-facing virtual monocular camera simulated via the Gazebo ROS camera plugin (<code class="inline-code">libgazebo_ros_camera.so</code>). The sensor follows the classic <strong>pinhole camera perspective projection model</strong>, which maps 3D Euclidean coordinates in the camera coordinate frame $(X_c, Y_c, Z_c)$ onto a 2D digital image sensor plane $(u, v)$ in pixel coordinates:
  </p>

  <div class="math-card">
    <div class="math-equation">
      s \\begin{bmatrix} u \\\\ v \\\\ 1 \\end{bmatrix} = \\mathbf{K} \\begin{bmatrix} X_c \\\\ Y_c \\\\ Z_c \\end{bmatrix} = \\begin{bmatrix} f_x & 0 & c_x \\\\ 0 & f_y & c_y \\\\ 0 & 0 & 1 \\end{bmatrix} \\begin{bmatrix} X_c \\\\ Y_c \\\\ Z_c \\end{bmatrix}
    </div>
    <div class="math-explanation">
      <strong>Camera Intrinsic Calibration Matrix ($K$):</strong> $f_x, f_y$ represent focal lengths in pixels, and $(c_x, c_y)$ is the principal point (optical center).
    </div>
  </div>

  <h2 class="sub-title">4.2 Gazebo Camera Sensor Configuration</h2>
  <p>The sensor is defined in <code class="inline-code">animal_robot.urdf</code> inside a <code class="inline-code">&lt;gazebo&gt;</code> reference tag binding to the <code class="inline-code">rgb_cam_camera_link_frame</code>:</p>
  <div class="code-header"><span>Optical Sensor Plugin Definition</span><span>animal_robot.urdf</span></div>
  <div class="code-block">
&lt;sensor type="camera" name="rgb_cam"&gt;
  &lt;always_on&gt;1&lt;/always_on&gt;
  &lt;update_rate&gt;15.0&lt;/update_rate&gt;
  &lt;camera name="rgb_cam"&gt;
    &lt;horizontal_fov&gt;1.3962634&lt;/horizontal_fov&gt; &lt;!-- 80 degrees in radians --&gt;
    &lt;image&gt;
      &lt;width&gt;640&lt;/width&gt;
      &lt;height&gt;480&lt;/height&gt;
      &lt;format&gt;R8G8B8&lt;/format&gt;
    &lt;/image&gt;
    &lt;clip&gt;
      &lt;near&gt;0.05&lt;/near&gt;
      &lt;far&gt;25.0&lt;/far&gt;
    &lt;/clip&gt;
  &lt;/camera&gt;
  &lt;plugin name="camera_controller" filename="libgazebo_ros_camera.so"&gt;
    &lt;ros&gt;
      &lt;remapping&gt;image_raw:=/rgb_cam/image_raw&lt;/remapping&gt;
      &lt;remapping&gt;camera_info:=/rgb_cam/camera_info&lt;/remapping&gt;
    &lt;/ros&gt;
    &lt;camera_name&gt;rgb_cam&lt;/camera_name&gt;
    &lt;frame_name&gt;rgb_cam_camera_link_frame&lt;/frame_name&gt;
    &lt;hack_baseline&gt;0.07&lt;/hack_baseline&gt;
  &lt;/plugin&gt;
&lt;/sensor&gt;
  </div>

  <h2 class="sub-title">4.3 Mathematical Derivation of Monocular Distance Estimation</h2>
  <p>
    Unlike expensive stereo cameras or LiDAR units, our mobile robot estimates physical distance to camouflaged targets using only a <strong>single monocular 2D bounding box</strong>. The derivation proceeds from first geometric principles:
  </p>
  <p>
    <strong>Step 1: Calculate Effective Focal Length in Pixels ($f_x$):</strong><br>
    The Horizontal Field of View ($\text{HFOV}$) is configured as $\text{HFOV} = 1.3962634\text{ rad} \approx 80.0^\circ$. For an image sensor width $W = 640\text{ pixels}$:
  </p>
  <div class="math-card">
    <div class="math-equation">
      \\tan\\left(\\frac{\\text{HFOV}}{2}\\right) = \\frac{W / 2}{f_x} \\implies f_x = \\frac{W}{2 \\cdot \\tan\\left(\\frac{\\text{HFOV}}{2}\\right)} = \\frac{320}{\\tan(40.0^\circ)} = \\frac{320}{0.8390996} \\approx 381.36 \\text{ pixels}
    </div>
    <div class="math-explanation">
      In the perception node, this is rounded to <code class="inline-code">self.focal_length_px = 381.5</code>.
    </div>
  </div>

  <p>
    <strong>Step 2: Similar Triangles Projection:</strong><br>
    Let $H_{\text{real}}$ be the known physical vertical height of an adult deer ($H_{\text{real}} = 1.35\text{ meters}$). When projected onto the camera sensor, this height spans $h_{\text{pixel}} = (y_2 - y_1)$ pixels in the bounding box:
  </p>
  <div class="math-card">
    <div class="math-equation">
      \\frac{h_{\\text{pixel}}}{f_x} = \\frac{H_{\\text{real}}}{D} \\implies D = \\frac{f_x \\cdot H_{\\text{real}}}{h_{\\text{pixel}}} = \\frac{381.5 \\cdot 1.35}{h_{\\text{pixel}}} = \\frac{515.025}{h_{\\text{pixel}}} \\text{ meters}
    </div>
    <div class="math-explanation">
      Physical distance $D$ is strictly inversely proportional to bounding box height $h_{\text{pixel}}$.
    </div>
  </div>

  <h2 class="sub-title">4.4 Numerical Verification & Error Sensitivity Analysis</h2>
  <p>
    Evaluating the sensitivity derivative $\frac{\partial D}{\partial h} = -\frac{f_x \cdot H_{\text{real}}}{h_{\text{pixel}}^2}$ reveals the spatial resolution characteristics across distances:
  </p>
  <table class="custom-table">
    <thead>
      <tr>
        <th>True Distance ($D$)</th>
        <th>Expected Bounding Box Height ($h_{\text{pixel}}$)</th>
        <th>Pixel Sensitivity ($\Delta D$ per 1 px change)</th>
        <th>Operational Zone</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>2.0 m</strong></td>
        <td>257.5 px</td>
        <td>&plusmn; 0.008 m / px (Sub-centimeter accuracy)</td>
        <td>Close Inspection Zone</td>
      </tr>
      <tr>
        <td><strong>3.0 m (Standoff)</strong></td>
        <td>171.7 px</td>
        <td>&plusmn; 0.017 m / px (Highly accurate)</td>
        <td>Optimal Target Holding Distance</td>
      </tr>
      <tr>
        <td><strong>5.0 m</strong></td>
        <td>103.0 px</td>
        <td>&plusmn; 0.048 m / px</td>
        <td>Medium Concealment Range</td>
      </tr>
      <tr>
        <td><strong>8.0 m</strong></td>
        <td>64.4 px</td>
        <td>&plusmn; 0.124 m / px</td>
        <td>Long-range Discovery Zone</td>
      </tr>
      <tr>
        <td><strong>12.0 m</strong></td>
        <td>42.9 px</td>
        <td>&plusmn; 0.280 m / px</td>
        <td>Far Boundary Detection</td>
      </tr>
    </tbody>
  </table>
  <div class="callout callout-info">
    <div class="callout-title">💡 Why Vertical Height ($h$) is Used Over Width ($w$)</div>
    Animals turn and face different directions (head-on, profile, three-quarter view), causing apparent bounding box <em>width</em> to vary by over 300%. However, their vertical <em>standing height</em> remains virtually constant regardless of azimuth orientation. Using vertical height $h_{\text{pixel}}$ guarantees orientation-invariant distance estimation!
  </div>
</div>
"""

def get_ch5():
    return """
<!-- ==================== CHAPTER 5 ==================== -->
<div class="page-break">
  <h1 class="section-title"><span class="section-num">05</span> Gazebo Simulation Environment & Procedural World Generation</h1>

  <h2 class="sub-title">5.1 Simulation Engine Architecture (SDF 1.6 vs URDF)</h2>
  <p>
    In the ROS 2 / Gazebo simulation paradigm, two distinct description formats are used in concert:
  </p>
  <ul>
    <li><strong>URDF (Unified Robot Description Format):</strong> Used exclusively for the robot. It models kinematic trees, coordinate frames (TF2), and sensor plugin bindings.</li>
    <li><strong>SDF (Simulation Description Format 1.6):</strong> Used for the static world environment, ground planes, sunlight sources, and 3D wildlife models. Unlike URDF, SDF natively supports multiple decoupled models, static non-movable physics flags, complex OGRE material scripts, and global environment lighting parameters.</li>
  </ul>

  <h2 class="sub-title">5.2 3D Model Assets & Texture Shading Architecture</h2>
  <p>
    The project maintains a realistic library of 3D wildlife and nature models in <code class="inline-code">models/</code>:
  </p>
  <ul>
    <li><strong>Camouflaged Targets:</strong> <code class="inline-code">deer</code> (high-poly textured mesh, Webots base color), <code class="inline-code">leopard</code> (scaled feline with rosette camouflage pattern), <code class="inline-code">fox</code>, and <code class="inline-code">snake</code> (multi-segment cylindrical body model).</li>
    <li><strong>Environmental Clutter:</strong> <code class="inline-code">oak_tree</code> (OSRF textured bark and branch leaf planes), <code class="inline-code">pine_tree</code> (coniferous evergreen foliage), and <code class="inline-code">rock</code> (falling rock mesh from Gazebo Fuel with high-roughness diffuse textures).</li>
  </ul>

  <div class="callout callout-warning">
    <div class="callout-title">⚡ Physics Decoupling: Collision vs Visual Meshes</div>
    Simulating ODE physics collisions directly against high-polygon 3D meshes (such as 15,000-vertex animal OBJ files) causes catastrophic CPU slowdowns. In our models, the visual mesh (<code class="inline-code">&lt;visual&gt;</code>) renders the photorealistic textured mesh, while the collision element (<code class="inline-code">&lt;collision&gt;</code>) is modeled as a simplified bounding box or cylinder. This reduces contact physics computations from $O(N \cdot M)$ down to $O(1)$ constant time!
  </div>

  <h2 class="sub-title">5.3 Procedural Wildlife World Generator (Domain Randomization)</h2>
  <p>
    To evaluate whether the perception system truly recognizes camouflage rather than overfitting to fixed animal coordinates, the project features a procedural world generator: <code class="inline-code">packages/animal_gazebo/scripts/generate_random_world.py</code>.
  </p>

  <div class="two-col avoid-break">
    <div class="card-box">
      <h4>Procedural Placement Algorithm</h4>
      <ul>
        <li><strong>Spawn Safety Zone:</strong> Guarantees a 2.0m obstacle-free circle around $(0, 0)$ so the robot spawns safely.</li>
        <li><strong>Poisson-Disc Collision Checking:</strong> Before placing any object, calculates Euclidean distance against all existing objects:
          <br><code class="inline-code">dist(p1, p2) &ge; r1 + r2</code>
        </li>
        <li><strong>Perimeter Enclosure:</strong> Organically surrounds the 22m &times; 22m arena with oak and pine trees to prevent the robot from escaping.</li>
      </ul>
    </div>
    <div class="card-box">
      <h4>Camouflage Concealment Tiers</h4>
      <ul>
        <li><strong>Tier 1: Close (2.8m – 4.2m)</strong> — Light concealment; primary baseline.</li>
        <li><strong>Tier 2: Medium (4.8m – 6.8m)</strong> — Moderate brush & tree trunk cover.</li>
        <li><strong>Tier 3: Far (7.2m – 9.5m)</strong> — Heavy camouflage; tests distance limits.</li>
        <li><strong>Tier 4: Flank (5.0m – 8.0m)</strong> — Deep shrub and boulder cover.</li>
        <li><strong>Companion Cover:</strong> Spawns a tree or boulder within 0.6m–1.2m of each deer to disrupt silhouette contours!</li>
      </ul>
    </div>
  </div>

  <h2 class="sub-title">5.4 Solar Lighting Domain Randomization</h2>
  <p>
    Natural camouflage varies dramatically under shifting sunlight angles. The generator randomizes the directional solar vector across azimuth $\phi \in [0, 2\pi]$ and elevation $\theta \in [35^\circ, 70^\circ]$:
  </p>
  <div class="math-card">
    <div class="math-equation">
      \\vec{d}_{sun} = \\begin{bmatrix} -\\cos\\phi \\cos\\theta \\\\ -\\sin\\phi \\cos\\theta \\\\ -\\sin\\theta \\end{bmatrix}
    </div>
    <div class="math-explanation">
      Coupled with subtle golden-hour warmth shifts in diffuse color ($R: 0.85\text{--}0.95, G: 0.82\text{--}0.90, B: 0.75\text{--}0.85$), this exposes the AI to diverse natural lighting scenarios.
    </div>
  </div>

  <h2 class="sub-title">5.5 Seed Reproducibility for Academic Benchmarking</h2>
  <p>
    Any procedurally generated world can be precisely recreated by passing a seed parameter:
  </p>
  <div class="code-block">
# Launch reproducible benchmark forest world with Seed 42
ros2 launch animal_gazebo simulation.launch.py gui:=true recognition:=true autonomous:=true random_world:=true seed:=42 density:=medium
  </div>
</div>
"""

def get_ch6():
    return """
<!-- ==================== CHAPTER 6 ==================== -->
<div class="page-break">
  <h1 class="section-title"><span class="section-num">06</span> Computer Vision Perception Engine & YOLOv8 Architecture</h1>

  <h2 class="sub-title">6.1 The Camouflage Detection Paradox</h2>
  <p>
    Standard object detection backbones extract spatial gradients using convolutional kernels. When a deer stands against dried bark or grassland, chromatic difference is virtually zero ($\Delta E_{ab} < 5$), and silhouette edges are scrambled by dappled tree shadows. Standard models produce confidence scores well below default thresholds ($< 0.25$), resulting in total detection failure. The <code class="inline-code">animal_recognition</code> package resolves this through a four-stage perception pipeline.
  </p>

  <h2 class="sub-title">6.2 CIELAB Contrast Limited Adaptive Histogram Equalization (CLAHE)</h2>
  <p>
    Standard RGB histogram equalization causes severe color clipping and unnatural artifacts. Our system converts the image into the <strong>CIELAB (L*a*b*) color space</strong>, which decouples luminance ($L^*$, perceived lightness) from chromaticity ($a^*$: green-red axis, $b^*$: blue-yellow axis).
  </p>
  <div class="code-header"><span>CIELAB CLAHE Micro-Texture Filter</span><span>ros_recognition_yolo.py</span></div>
  <div class="code-block">
def preprocess_for_camouflage(self, cv_image):
    if not self.enable_clahe:
        return cv_image
    # Convert BGR to CIELAB space
    lab = cv2.cvtColor(cv_image, cv2.COLOR_BGR2LAB)
    l_chan, a_chan, b_chan = cv2.split(lab)
    # Apply CLAHE strictly to the L (Luminance) channel
    enhanced_l = self.clahe.apply(l_chan)
    # Re-merge channels and convert back to BGR
    enhanced_lab = cv2.merge((enhanced_l, a_chan, b_chan))
    return cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
  </div>

  <div class="two-col avoid-break">
    <div class="card-box">
      <h4>Mathematical Clip Limit (3.0)</h4>
      <p>
        Adaptive histogram equalization redistributes local pixel intensities across a contextual tile. If a tile has uniform color, noise is heavily amplified. The <strong>clip limit (3.0)</strong> sets a ceiling on histogram peaks. Excess pixels above the threshold are clipped and distributed uniformly across all bins before calculating the Cumulative Distribution Function (CDF).
      </p>
    </div>
    <div class="card-box">
      <h4>Contextual Tile Grid (4 &times; 4)</h4>
      <p>
        The frame ($640 \times 480$) is partitioned into a $4 \times 4$ grid of 16 sub-regions ($160 \times 120$ px each). This matches the physical visual footprint of animal fur patterns against tree trunks, extracting micro-texture contrast while bilinear interpolation eliminates artificial tile boundary borders.
      </p>
    </div>
  </div>

  <h2 class="sub-title">6.3 Deep Learning Architecture: Ultralytics YOLOv8n</h2>
  <p>
    The system deploys <strong>YOLOv8n (Nano)</strong> as its core neural network. YOLOv8 introduces major structural advances over previous generations (YOLOv5, YOLOv7):
  </p>
  <ul>
    <li><strong>Backbone:</strong> Modified CSPDarknet53 utilizing <strong>C2f modules</strong> (Cross-Stage Partial with two convolutions). C2f combines high-level semantic abstractions with rich gradient flow branches, boosting multi-scale feature retention for low-contrast textures.</li>
    <li><strong>Neck:</strong> Path Aggregation Network (PAN-Net) + Feature Pyramid Network (FPN), fusing high-resolution spatial details from early layers with semantic context from deeper layers.</li>
    <li><strong>Decoupled Head:</strong> Replaces coupled heads by splitting bounding box regression and object classification into separate task branches.</li>
    <li><strong>Anchor-Free Design:</strong> Directly predicts distances from bounding box centers rather than relying on predefined anchor box aspect ratios, significantly improving generalization for non-standard animal poses.</li>
    <li><strong>Loss Functions:</strong> Combines <strong>Distribution Focal Loss (DFL)</strong> and Complete IoU (CIoU) loss for spatial localization, paired with Binary Cross Entropy (BCE) for multi-class classification.</li>
  </ul>

  <h2 class="sub-title">6.4 Ungulate Taxonomic Semantic Prior Mapping</h2>
  <p>
    A critical challenge in modern robotics is the <em>Vocabulary Gap</em>: the pre-trained MS COCO dataset (80 categories) contains classes for <code class="inline-code">horse</code>, <code class="inline-code">sheep</code>, <code class="inline-code">cow</code>, <code class="inline-code">zebra</code>, and <code class="inline-code">giraffe</code>, but <strong>does not contain an explicit 'deer' class!</strong>
  </p>
  <p>
    When exposed to a camouflaged deer in Gazebo, a standard neural network detects the morphological quadruped features (four legs, horizontal torso, elongated neck) and fires activations for closely related ungulate priors with moderate confidence ($0.25 - 0.55$). Our perception node implements an <strong>intelligent taxonomic mapping layer</strong>:
  </p>
  <div class="code-block">
self.ungulate_coco_classes = {'horse', 'giraffe', 'cow', 'sheep', 'zebra', 'bear', 'deer', 'dog', 'elephant', 'cat'}
self.noise_coco_classes = {'bird', 'potted plant', 'kite', 'bench', 'chair', 'umbrella'}

# Filter out foliage false-positives
if cls_name in self.noise_coco_classes and conf < 0.65:
    continue

# Taxonomic Ungulate Prior Mapping
is_wildlife_target = (cls_name in self.ungulate_coco_classes) or (cls_name == self.target_animal)
label_name = "DEER" if is_wildlife_target else cls_name.upper()
  </div>

  <h2 class="sub-title">6.5 Temporal Exponential Moving Average (EMA) Box Stabilization</h2>
  <p>
    In simulation and real-world feeds, bounding box boundaries can jitter slightly from frame to frame due to sensor noise. The node incorporates an <strong>EMA temporal smoother</strong>:
  </p>
  <div class="math-card">
    <div class="math-equation">
      B_t = \alpha \cdot B_{\text{new}} + (1 - \alpha) \cdot B_{t-1} \quad \text{for } \text{IoU}(B_{\text{new}}, B_{t-1}) > 0.35
    </div>
    <div class="math-explanation">
      With smoothing weight $\alpha = 0.65$, spatial bounding box coordinates and confidence scores transition smoothly, eliminating high-frequency jitter before telemetry is passed to the visual servoing controller.
    </div>
  </div>
</div>
"""


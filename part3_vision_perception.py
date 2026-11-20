# -*- coding: utf-8 -*-
"""Part 3: CIELAB CLAHE Micro-Contrast & YOLOv8 Camouflage Perception"""

def get_part3():
    return """
<!-- ==================== PART 3 ==================== -->
<div class="page-break">
  <div class="part-header-card border-amber">
    <div class="part-badge badge-amber">MODULE 3 OF 4</div>
    <h1 class="part-title">Part 3: CIELAB CLAHE Micro-Contrast & YOLOv8 Camouflage Perception</h1>
    <p class="part-subtitle">
      Comprehensive technical handbook covering the computer vision perception engine, theory of biological crypsis, CIELAB color space transformation, adaptive histogram equalization (CLAHE), YOLOv8 neural network architecture, ungulate taxonomic semantic prior mapping, and monocular pinhole distance estimation.
    </p>
  </div>

  <h2 class="sub-title">3.1 Subsystem Role Distribution & Core Ownership</h2>
  <table class="custom-table">
    <thead>
      <tr>
        <th style="width: 25%;">Engineering Role</th>
        <th style="width: 25%;">Primary Subsystem</th>
        <th style="width: 32%;">Specific Technical Responsibilities</th>
        <th style="width: 18%;">Core Viva Focus</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Camouflage Theory & CLAHE Lead</strong></td>
        <td><strong>Color Spaces & Micro-Texture Preprocessing</strong></td>
        <td>
          &bull; Formulating the difference between COD and generic object detection.<br>
          &bull; Converting raw frames from BGR to CIELAB color space.<br>
          &bull; Applying CLAHE exclusively on Luminance channel (L*).<br>
          &bull; Tuning the 4&times;4 tile grid and 3.0 clip limit parameters.
        </td>
        <td>COD vs Generic OD, color space physics, CLAHE mathematics, clip limit purpose.</td>
      </tr>
      <tr>
        <td><strong>Deep Learning Architecture Lead</strong></td>
        <td><strong>YOLOv8 Neural Network & Inference</strong></td>
        <td>
          &bull; Ingesting PyTorch YOLOv8n deep model inside ROS 2 node.<br>
          &bull; Understanding C2f multi-path gradient modules and PAN-Net neck.<br>
          &bull; Decoupled anchor-free detection head and loss mechanics.<br>
          &bull; Implementing CPU inference throttling (<code class="inline-code">frame_skip = 1</code>).
        </td>
        <td>YOLOv8 vs YOLOv5, C2f modules, anchor-free heads, DFL/CIoU loss functions.</td>
      </tr>
      <tr>
        <td><strong>Taxonomic Mapping & Depth Lead</strong></td>
        <td><strong>Taxonomic Priors, Depth Math & HUD</strong></td>
        <td>
          &bull; Resolving the COCO Vocabulary Gap via Ungulate Prior Mapping.<br>
          &bull; Filtering false-positive foliage noise (confidence threshold 0.65).<br>
          &bull; Formulating monocular pinhole distance estimation formula.<br>
          &bull; Temporal box smoothing and tactical OpenCV HUD overlay.
        </td>
        <td>Pinhole distance math, similar triangles, taxonomic mapping, box smoothing.</td>
      </tr>
    </tbody>
  </table>

  <h2 class="sub-title">3.2 The Biological Camouflage Detection Challenge</h2>
  <p>
    In terrestrial ecosystems, animals have evolved four primary visual concealment strategies:
  </p>
  <ul>
    <li><strong>Background Matching:</strong> The animal's coat color, texture, and luminance match the background substrate almost identically (e.g., deer fur against dried oak bark). The color difference between animal and background is minimal, making simple color thresholding impossible.</li>
    <li><strong>Disruptive Coloration:</strong> High-contrast patterns (such as leopard rosettes or snake bands) create visual false edges that break up the animal's continuous body outline.</li>
    <li><strong>Counter-Shading:</strong> Darker pigmentation on the upper surface and lighter pigmentation on the underside counteracts the natural shadow cast by sunlight, rendering the animal visually flat.</li>
    <li><strong>Shadow & Foliage Blending:</strong> Animals position themselves under tree canopies where dappled sunlight casts chaotic shadows that mimic body contours.</li>
  </ul>

  <p>
    Standard convolutional neural networks rely heavily on <em>sharp edge borders</em> and <em>distinct color contrast</em>. When applied to camouflaged animals, standard models fail, generating confidence scores well below default detection thresholds (below 20%). The perception pipeline resolves this challenge through an integrated multi-stage approach.
  </p>

  <h2 class="sub-title">3.3 CIELAB Contrast Limited Adaptive Histogram Equalization (CLAHE)</h2>
  <p>
    Applying standard histogram equalization directly to an RGB image alters the relative balance between Red, Green, and Blue channels, producing extreme color distortion, unnatural saturation, and severe noise amplification.
  </p>
  <p>
    To overcome this, the perception node (<code class="inline-code">ros_recognition_yolo.py</code>) converts the incoming video frame into the <strong>CIELAB (L*a*b*) color space</strong>:
  </p>
  <ul>
    <li><strong>L* Channel (Luminance):</strong> Represents perceived human lightness (from 0 = complete black to 100 = pure white).</li>
    <li><strong>a* Channel (Green to Red):</strong> Represents color along the green-red axis.</li>
    <li><strong>b* Channel (Blue to Yellow):</strong> Represents color along the blue-yellow axis.</li>
  </ul>

  <p>
    By isolating the <strong>L* channel</strong>, our filter modifies local contrast without touching color information (a*, b*).
  </p>

  <div class="code-header"><span>CIELAB CLAHE Preprocessing Function</span><span>ros_recognition_yolo.py</span></div>
  <div class="code-block">
def preprocess_for_camouflage(self, cv_image):
    if not self.enable_clahe:
        return cv_image

    # 1. Convert BGR image to CIELAB space
    lab = cv2.cvtColor(cv_image, cv2.COLOR_BGR2LAB)
    l_chan, a_chan, b_chan = cv2.split(lab)

    # 2. Apply CLAHE strictly to the L (Luminance) channel
    enhanced_l = self.clahe.apply(l_chan)

    # 3. Re-merge channels and convert back to BGR
    enhanced_lab = cv2.merge((enhanced_l, a_chan, b_chan))
    return cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
  </div>

  <div class="two-col avoid-break">
    <div class="card-box">
      <h4>Clip Limit (3.0): Preventing Noise Amplification</h4>
      <p>
        In basic adaptive equalization, if an image region is flat and uniform (such as smooth grass), noise is heavily amplified. The <strong>clip limit (3.0)</strong> sets a ceiling on histogram peaks. Excess pixels above the threshold are clipped and distributed uniformly across all bins, enhancing fur micro-textures without amplifying background noise.
      </p>
    </div>
    <div class="card-box">
      <h4>Contextual Tile Grid (4 &times; 4)</h4>
      <p>
        The 640&times;480 frame is divided into a 4&times;4 grid of 16 contextual tiles (160&times;120 pixels each). This spatial scale perfectly matches the physical visual footprint of animal fur patterns against tree trunks. Smooth blending between tiles eliminates visible borders.
      </p>
    </div>
  </div>

  <h2 class="sub-title">3.4 Ultralytics YOLOv8 Deep Learning Architecture</h2>
  <p>
    The system deploys <strong>YOLOv8n (Nano)</strong>, which incorporates modern deep learning computer vision advances:
  </p>
  <ul>
    <li><strong>Backbone:</strong> Modified CSPDarknet53 utilizing <strong>C2f modules</strong> (Cross-Stage Partial with two convolutions). C2f incorporates multi-branch split connections, preserving gradient flow across deep layers. This enables the network to retain faint micro-texture representations that earlier architectures discarded.</li>
    <li><strong>Neck:</strong> Path Aggregation Network (PAN-Net) coupled with a Feature Pyramid Network (FPN). High-resolution spatial feature maps from early layers are combined with deep semantic feature maps, enabling multi-scale detection across varying animal distances.</li>
    <li><strong>Anchor-Free Decoupled Head:</strong> In older models (YOLOv3, YOLOv5), classification and bounding box regression shared common layers and relied on pre-defined anchor boxes. YOLOv8 decouples these tasks into independent branches and regresses box centers directly, dramatically improving detection of non-standard animal poses.</li>
    <li><strong>Loss Formulations:</strong> Bounding box regression utilizes a combination of <strong>Complete IoU (CIoU) Loss</strong> (accounting for overlap, aspect ratio, and center distance) and <strong>Distribution Focal Loss (DFL)</strong> (which models box boundaries as continuous probability distributions to handle blurred edges). Classification is trained via <strong>Binary Cross-Entropy (BCE)</strong>.</li>
  </ul>

  <h2 class="sub-title">3.5 Ungulate Taxonomic Semantic Prior Mapping</h2>
  <p>
    A critical technical obstacle is the <strong>Vocabulary Gap</strong> of pre-trained models: the Microsoft COCO dataset (80 categories) contains <code class="inline-code">horse</code>, <code class="inline-code">sheep</code>, <code class="inline-code">cow</code>, <code class="inline-code">zebra</code>, and <code class="inline-code">giraffe</code>, but <strong>has no 'deer' class!</strong>
  </p>
  <p>
    When exposed to a camouflaged deer in Gazebo, a standard neural network detects universal quadruped morphological features (horizontal torso, four legs, elongated neck) and fires moderate activations for related ungulate categories (0.22 to 0.55 confidence). 
    The perception node exploits this biological relationship through an intelligent <strong>taxonomic semantic mapping layer</strong>:
  </p>

  <div class="code-header"><span>Taxonomic Semantic Mapping & Noise Gating</span><span>ros_recognition_yolo.py</span></div>
  <div class="code-block">
# Ungulate Quadruped Prior Classes in COCO
self.ungulate_coco_classes = {'horse', 'giraffe', 'cow', 'sheep', 'zebra', 'bear', 'deer', 'dog', 'elephant', 'cat'}
self.noise_coco_classes = {'bird', 'potted plant', 'kite', 'bench', 'chair', 'umbrella'}

# Filter out false-positive foliage noise on tree branches
if cls_name in self.noise_coco_classes and conf < 0.65:
    continue

# Taxonomic Ungulate Prior Mapping:
is_wildlife_target = (cls_name in self.ungulate_coco_classes) or (cls_name == self.target_animal)
label_name = "DEER" if is_wildlife_target else cls_name.upper()
  </div>

  <h2 class="sub-title">3.6 Monocular Depth Estimation Formulations</h2>
  <p>
    Our system eliminates the need for expensive, power-hungry LiDAR sensors by deriving distance mathematically from a <strong>single 2D camera bounding box</strong> using the pinhole perspective model:
  </p>

  <!-- Formula 1: Focal Length -->
  <div class="formula-box">
    <div class="formula-title">Step 1: Compute Camera Focal Length in Pixels (f)</div>
    <div class="formula-main">
      Focal Length (f) = (Image Sensor Width / 2) &divide; tan(Horizontal Field of View / 2)
    </div>
    <div class="formula-details">
      With Image Width = 640 pixels and Field of View = 80° (40° half-angle):
      <br><strong>f = 320 &divide; tan(40°) = 320 &divide; 0.8391 = 381.5 pixels</strong>
    </div>
    <div class="formula-explanation">
      <strong>What this means in plain words:</strong> This converts the camera's physical 80-degree optical viewing angle into equivalent pixel coordinates, which is required to calculate real-world distances from 2D photos.
    </div>
  </div>

  <!-- Formula 2: Depth Distance -->
  <div class="formula-box">
    <div class="formula-title">Step 2: Target Distance Estimation Formula (Depth D)</div>
    <div class="formula-main">
      Estimated Distance (D) = (Focal Length &times; Real Animal Height) &divide; Bounding Box Height in Pixels
    </div>
    <div class="formula-details">
      Using our camera focal length (381.5 px) and standing deer height (1.35 meters):
      <br><strong>Distance (D) = (381.5 &times; 1.35) &divide; Box Height = 515.025 &divide; Box Height (meters)</strong>
    </div>
    <div class="formula-explanation">
      <strong>What this means in plain words:</strong> Things that are farther away appear smaller on screen. Since we know a real adult deer is approximately 1.35 meters tall, we simply count how many pixels tall its bounding box is. 
      <br>&bull; If the box is <strong>172 pixels tall</strong> &rarr; Distance = 515.025 / 172 = <strong>3.0 meters away</strong> (Optimal inspection standoff).
      <br>&bull; If the box is <strong>103 pixels tall</strong> &rarr; Distance = 515.025 / 103 = <strong>5.0 meters away</strong>.
      <br>&bull; If the box is <strong>52 pixels tall</strong> &rarr; Distance = 515.025 / 52 = <strong>9.9 meters away</strong>.
    </div>
  </div>

  <div class="callout callout-info">
    <div class="callout-title">💡 Why Vertical Height is Invariant to Animal Heading</div>
    When an animal turns from a side profile view to a head-on view, its bounding box <em>width</em> changes drastically by over 300%. In contrast, its vertical <em>standing height</em> remains virtually unchanged regardless of which way the animal faces. Using vertical pixel height guarantees reliable, orientation-independent distance estimates!
  </div>

  <h2 class="sub-title">3.7 Temporal Bounding Box Smoothing & Tactical HUD</h2>
  <p>
    To eliminate frame-to-frame bounding box coordinate jitter, the node applies an <strong>Exponential Moving Average (EMA)</strong> smoother:
  </p>

  <div class="formula-box">
    <div class="formula-title">Smooth Bounding Box Formula (Exponential Moving Average)</div>
    <div class="formula-main">
      Smoothed Box Coordinate = 0.65 &times; (New Frame Box) + 0.35 &times; (Previous Frame Box)
    </div>
    <div class="formula-explanation">
      <strong>What this means in plain words:</strong> Bounding boxes detected by neural networks can flicker or jump slightly from frame to frame due to video noise. By blending 65% of the new box with 35% of the previous box, the box glides smoothly on screen without jitter.
    </div>
  </div>

  <p>
    The node renders a tactical Heads-Up Display (HUD) directly on the annotated video stream:
  </p>
  <ul>
    <li><strong>Tactical Corner Brackets:</strong> High-visibility green brackets drawn at bounding box corners.</li>
    <li><strong>Target Distance Banners:</strong> Displays <code class="inline-code">🦌 DEER 74.2% | 3.8m</code>.</li>
    <li><strong>Center Crosshair & Performance Overlay:</strong> Center targeting marker, real-time FPS counter, and neural inference latency in milliseconds.</li>
  </ul>

  <h2 class="sub-title">3.8 Part 3 Dedicated Viva & Oral Exam Defense Guide</h2>

  <div class="viva-card">
    <div class="viva-q"><span class="viva-badge">Q3.1</span> Why did you apply CLAHE strictly on the L* channel of CIELAB instead of RGB?</div>
    <div class="viva-concept">Topic Focus: CIELAB Color Space & Contrast Enhancement</div>
    <div class="viva-ans">
      <strong>Model Answer:</strong>
      In the RGB color space, luminance and chromaticity are deeply coupled across all three channels. Equalizing RGB channels independently distorts the color balance, shifts the natural hue of vegetation, and produces extreme pixel saturation.
      <br><br>
      In <strong>CIELAB (L*a*b*)</strong>, lightness (L*, perceived human luminance) is cleanly decoupled from color information (a*, green-red; b*, blue-yellow). Applying CLAHE exclusively to the L* channel sharpens the subtle micro-textures of animal fur and muscle contours against tree bark without introducing any chromatic distortion or artificial color shifts.
    </div>
  </div>

  <div class="viva-card">
    <div class="viva-q"><span class="viva-badge">Q3.2</span> What is the mathematical purpose of the clip limit in CLAHE?</div>
    <div class="viva-concept">Topic Focus: Contrast Limited Adaptive Equalization</div>
    <div class="viva-ans">
      <strong>Model Answer:</strong>
      Standard Adaptive Histogram Equalization (AHE) tends to over-amplify noise in homogeneous, uniform image regions (such as flat terrain or overcast sky). The <strong>clip limit (3.0)</strong> sets an upper boundary. The pixel count exceeding the clip threshold is clipped and redistributed uniformly across all histogram bins before computing the Cumulative Distribution Function (CDF). This guarantees contrast enhancement without amplifying background sensor noise.
    </div>
  </div>

  <div class="viva-card">
    <div class="viva-q"><span class="viva-badge">Q3.3</span> How does YOLOv8's C2f module differ from YOLOv5's C3 module?</div>
    <div class="viva-concept">Topic Focus: Deep Learning Backbone Architecture</div>
    <div class="viva-ans">
      <strong>Model Answer:</strong>
      YOLOv5 used the C3 (Cross-Stage Partial with 3 Convolutions) block, which passed feature maps through standard bottleneck layers sequentially. 
      <br><br>
      YOLOv8 introduces the <strong>C2f module</strong>, inspired by ELAN (Efficient Layer Aggregation Network). C2f splits the input feature map and passes it through multiple parallel bottleneck branches, concatenating intermediate outputs at every stage. This preserves rich, multi-path gradient flow during backpropagation and retains faint, multi-scale texture details that are critical for recognizing camouflaged animals.
    </div>
  </div>

  <div class="viva-card">
    <div class="viva-q"><span class="viva-badge">Q3.4</span> Explain how you solved the problem of COCO having no 'deer' class.</div>
    <div class="viva-concept">Topic Focus: Taxonomic Semantic Prior Mapping</div>
    <div class="viva-ans">
      <strong>Model Answer:</strong>
      The MS COCO dataset (80 categories) does not contain a 'deer' class. When an un-fine-tuned YOLO network sees a deer, its convolutional layers detect the quadruped morphology (four legs, torso, elongated neck) and fire activations for related ungulate classes: <code class="inline-code">horse</code>, <code class="inline-code">sheep</code>, <code class="inline-code">cow</code>, <code class="inline-code">zebra</code>, or <code class="inline-code">giraffe</code> at confidence scores between 0.22 and 0.55.
      <br><br>
      Our perception node captures these quadruped priors and maps them systematically to the target wildlife class:
      <br><code class="inline-code">is_target = (cls_name in ungulate_coco_classes) or (cls_name == 'deer')</code>
      <br>This allows instant, reliable camouflage deer detection before initiating fine-tuning!
    </div>
  </div>

  <div class="viva-card">
    <div class="viva-q"><span class="viva-badge">Q3.5</span> Derive the monocular depth estimation equation from first principles.</div>
    <div class="viva-concept">Topic Focus: Monocular Depth & Pinhole Optics</div>
    <div class="viva-ans">
      <strong>Model Answer:</strong>
      From pinhole camera geometry:
      <ol>
        <li>Given horizontal FOV (80°) and sensor width (640 pixels):
          <br>Focal Length = (640 / 2) / tan(40°) = 320 / 0.8391 = 381.5 pixels.
        </li>
        <li>By similar triangles, the ratio of apparent bounding box height to focal length equals the ratio of real physical height (1.35 meters) to real-world distance D:
          <br>Box Height / Focal Length = Real Height / Distance
          <br>Distance = (Focal Length &times; Real Height) / Box Height = (381.5 &times; 1.35) / Box Height = 515.025 / Box Height.
        </li>
      </ol>
      This enables passive, real-time depth calculation without needing an active LiDAR sensor.
    </div>
  </div>
</div>
"""

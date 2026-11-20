# -*- coding: utf-8 -*-
"""Chapters 1, 2, and 3 for Master Handbook"""

def get_ch1():
    return """
<!-- ==================== CHAPTER 1 ==================== -->
<div class="page-break">
  <h1 class="section-title"><span class="section-num">01</span> Executive Summary, Project Vision & Foundations</h1>
  
  <h2 class="sub-title">1.1 Project Purpose & Problem Formulation</h2>
  <p>
    The <strong>Autonomous Camouflage Animal Detection System</strong> is a high-performance cyber-physical robotics simulation and perception framework engineered to address one of the most formidable challenges in autonomous visual computing: <strong>Camouflaged Object Detection (COD)</strong> in natural, unstructured ecosystems. 
  </p>
  <p>
    In real-world wildlife monitoring, ecological survey operations, anti-poaching patrols, and search-and-rescue (SAR) missions, biological targets have evolved over millennia to blend seamlessly into their surroundings through <em>crypsis</em>, disruptive coloration, background matching, and counter-shading. Traditional computer vision and generic object detection models (such as vanilla YOLO, Faster R-CNN, or SSD trained on the Microsoft COCO dataset) consistently fail in these scenarios because they rely heavily on salient edge gradients, chromatic contrast, and distinctive object-to-background boundaries.
  </p>
  <p>
    This project constructs a complete end-to-end, reproducible solution combining:
  </p>
  <ul>
    <li><strong>Robotic Simulation Middleware:</strong> ROS 2 Humble Hawksbill running inside an isolated Linux container, orchestrating inter-process communications via high-throughput DDS pub/sub.</li>
    <li><strong>Physics & Synthetic Ecology Simulation:</strong> Gazebo Classic 11 with the Open Dynamics Engine (ODE), hosting realistic 3D textured wildlife models (deer, leopards, foxes, snakes) amidst procedurally generated woodlands.</li>
    <li><strong>Micro-Texture Contrast Perception:</strong> An optimized computer vision pipeline applying Contrast Limited Adaptive Histogram Equalization (CLAHE) in the CIELAB color space, coupled with an Ultralytics YOLOv8 neural network fine-tuned to uncover cryptic ungulate features.</li>
    <li><strong>Closed-Loop Autonomous Navigation:</strong> A 4-state Finite State Machine (FSM) executing environmental sweeping, sinusoidal field-of-view (FOV) exploration, and real-time visual servoing to center and inspect detected animals at safe standoff distances.</li>
  </ul>

  <div class="callout callout-info">
    <div class="callout-title">🎯 Core Project Mission</div>
    To demonstrate that an agile, differential-drive mobile robot equipped with only a single monocular RGB camera can autonomously traverse an unpredictable forest environment, detect heavily camouflaged animals in real time, calculate their 3D physical distance, and execute scientific inspection maneuvers without requiring expensive LiDAR sensors or high-end discrete GPUs.
  </div>

  <h2 class="sub-title">1.2 Theoretical Comparison: COD vs SOD vs Generic Object Detection</h2>
  <p>Understanding the fundamental distinction between detection paradigms is essential for academic evaluation and defense:</p>

  <table class="custom-table">
    <thead>
      <tr>
        <th style="width: 20%;">Attribute</th>
        <th style="width: 25%;">Generic Object Detection (OD)</th>
        <th style="width: 25%;">Salient Object Detection (SOD)</th>
        <th style="width: 30%;">Camouflaged Object Detection (COD)</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Visual Contrast</strong></td>
        <td>Moderate to High; distinct foreground/background separation.</td>
        <td>Extremely High; foreground actively captures human eye attention.</td>
        <td><strong>Extremely Low;</strong> target texture matches background almost identically.</td>
      </tr>
      <tr>
        <td><strong>Edge & Boundary</strong></td>
        <td>Clear spatial edge gradients along object contours.</td>
        <td>Sharp, unambiguous perimeter lines.</td>
        <td><strong>Disrupted boundaries;</strong> dappled shading breaks continuity.</td>
      </tr>
      <tr>
        <td><strong>Feature Representation</strong></td>
        <td>Global semantic abstractions (e.g., car wheels, dog ears).</td>
        <td>High-activation heatmaps in early CNN feature layers.</td>
        <td><strong>Subtle micro-textures;</strong> minute differences in hair/fur vs oak bark.</td>
      </tr>
      <tr>
        <td><strong>Failure Modes</strong></td>
        <td>Occasional occlusion or extreme scale variation.</td>
        <td>Low illumination or cluttered backgrounds.</td>
        <td><strong>Severe false negatives;</strong> targets treated as background noise.</td>
      </tr>
      <tr>
        <td><strong>Solution in This Project</strong></td>
        <td>Baseline YOLO bounding box regression.</td>
        <td>Standard saliency filters (insufficient for camouflage).</td>
        <td><strong>CIELAB CLAHE micro-contrast + Ungulate taxonomic priors + EMA smoothing.</strong></td>
      </tr>
    </tbody>
  </table>

  <h2 class="sub-title">1.3 Technical Specifications Matrix</h2>
  <table class="custom-table">
    <thead>
      <tr>
        <th>Subsystem</th>
        <th>Component</th>
        <th>Specification / Configuration</th>
        <th>Design Justification</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>OS / Environment</strong></td>
        <td>Host / Container</td>
        <td>Ubuntu 22.04 LTS within Docker (X11 GUI Passthrough)</td>
        <td>Cross-platform portability; eliminates host library conflicts.</td>
      </tr>
      <tr>
        <td><strong>Middleware</strong></td>
        <td>ROS 2</td>
        <td>Humble Hawksbill (Desktop-Full)</td>
        <td>LTS stability, modern Python 3 / rclpy API, zero ROS 1 roscore master bottleneck.</td>
      </tr>
      <tr>
        <td><strong>Simulator</strong></td>
        <td>Gazebo</td>
        <td>Gazebo Classic 11.10.2 (ODE Physics Engine)</td>
        <td>Native ROS 2 gazebo_ros integration, SDF 1.6 support, stable sensor plugins.</td>
      </tr>
      <tr>
        <td><strong>Robot Platform</strong></td>
        <td>Differential Drive</td>
        <td>2 Actuated Wheels (r=0.035m, L=0.12m) + 1 Caster Sphere</td>
        <td>High indoor/outdoor agility; zero-radius in-place rotation capability.</td>
      </tr>
      <tr>
        <td><strong>Vision Sensor</strong></td>
        <td>RGB Camera Plugin</td>
        <td>640x480 @ 15 FPS, HFOV 1.396 rad (80°), Range 0.05m–25m</td>
        <td>Matches realistic embedded camera modules; lightweight on CPU frame rates.</td>
      </tr>
      <tr>
        <td><strong>AI Perception</strong></td>
        <td>YOLOv8n (Nano)</td>
        <td>Ultralytics PyTorch CPU, Confidence Thresh: 0.22, Frame Skip: 1</td>
        <td>Fastest inference (~40ms on i5 CPU); high sensitivity for cryptic textures.</td>
      </tr>
      <tr>
        <td><strong>Image Filter</strong></td>
        <td>CLAHE</td>
        <td>CIELAB L-channel, Clip Limit: 3.0, Tile Grid: 4x4</td>
        <td>Separates chromaticity from luminance; magnifies fur texture against trees.</td>
      </tr>
    </tbody>
  </table>

  <h2 class="sub-title">1.4 Complete Codebase Architecture & File Matrix</h2>
  <p>The repository is organized following standard ROS 2 ament_cmake workspace standards, cleanly dividing simulation, robot description, vision perception, control, and training:</p>

  <table class="custom-table">
    <thead>
      <tr>
        <th>Directory / Path</th>
        <th>Type</th>
        <th>Primary Responsibility</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><code class="inline-code">packages/animal_description/</code></td>
        <td>ROS 2 Package</td>
        <td>Contains the robot kinematic definition (<code class="inline-code">animal_robot.urdf</code>) and spawn launch scripts (<code class="inline-code">spawn_robot.launch.py</code>).</td>
      </tr>
      <tr>
        <td><code class="inline-code">packages/animal_gazebo/</code></td>
        <td>ROS 2 Package</td>
        <td>World launch files (<code class="inline-code">simulation.launch.py</code>), default world (<code class="inline-code">animal_world.world</code>), and procedural forest generator (<code class="inline-code">generate_random_world.py</code>).</td>
      </tr>
      <tr>
        <td><code class="inline-code">packages/animal_recognition/</code></td>
        <td>ROS 2 Package</td>
        <td>The primary perception engine (<code class="inline-code">ros_recognition_yolo.py</code>), CLAHE enhancement, taxonomic mapping, monocular distance estimation, and tactical HUD.</td>
      </tr>
      <tr>
        <td><code class="inline-code">packages/animal_control/</code></td>
        <td>ROS 2 Package</td>
        <td>Autonomous patrol state machine (<code class="inline-code">autonomous_patrol.py</code>) and joystick/keyboard teleop bridges (<code class="inline-code">robot_control.py</code>).</td>
      </tr>
      <tr>
        <td><code class="inline-code">models/</code></td>
        <td>Gazebo SDF Models</td>
        <td>SDF models, textures, materials, and 3D OBJ/DAE meshes for deer, leopard, fox, snake, oak trees, pine trees, and rocks.</td>
      </tr>
      <tr>
        <td><code class="inline-code">training/</code></td>
        <td>Deep Learning Pipeline</td>
        <td>Simulation frame collector (<code class="inline-code">capture_dataset.py</code>), YOLOv8 fine-tuner (<code class="inline-code">train_camouflage_yolo.py</code>), and dataset config (<code class="inline-code">data.yaml</code>).</td>
      </tr>
      <tr>
        <td><code class="inline-code">Dockerfile, start_docker.sh</code></td>
        <td>DevOps Infrastructure</td>
        <td>Containerized Linux build environment with X11 display socket forwarding and software GL rendering flags.</td>
      </tr>
    </tbody>
  </table>
</div>
"""

def get_ch2():
    return """
<!-- ==================== CHAPTER 2 ==================== -->
<div class="page-break">
  <h1 class="section-title"><span class="section-num">02</span> End-to-End System Architecture & Computational Dataflow</h1>

  <h2 class="sub-title">2.1 System Architectural Topology</h2>
  <p>
    The system follows a reactive, decoupled publisher-subscriber architecture. The simulation environment acts as the physical ground truth, producing optical sensor telemetry. The perception node analyzes this telemetry to derive semantic and spatial situational awareness, which is ingested by the autonomous controller to issue motion commands back to the simulator.
  </p>

  <!-- SVG Architecture Flowchart -->
  <div class="diagram-container avoid-break">
    <svg width="100%" height="220" viewBox="0 0 760 220" xmlns="http://www.w3.org/2000/svg">
      <!-- Background Box Gazebo -->
      <rect x="10" y="20" width="170" height="180" rx="10" fill="#f1f5f9" stroke="#94a3b8" stroke-width="1.5" />
      <text x="95" y="42" font-family="'Plus Jakarta Sans', sans-serif" font-size="10" font-weight="700" fill="#0f172a" text-anchor="middle">GAZEBO CLASSIC 11</text>
      
      <rect x="25" y="60" width="140" height="38" rx="6" fill="#e2e8f0" stroke="#cbd5e1" />
      <text x="95" y="78" font-family="'JetBrains Mono', monospace" font-size="8" fill="#334155" text-anchor="middle">ODE Physics Engine</text>
      <text x="95" y="90" font-family="'Plus Jakarta Sans', sans-serif" font-size="7.5" fill="#64748b" text-anchor="middle">50 Hz Dynamics Update</text>

      <rect x="25" y="115" width="140" height="42" rx="6" fill="#ecfdf5" stroke="#10b981" />
      <text x="95" y="133" font-family="'JetBrains Mono', monospace" font-size="8" font-weight="700" fill="#065f46" text-anchor="middle">gazebo_ros_camera</text>
      <text x="95" y="147" font-family="'Plus Jakarta Sans', sans-serif" font-size="7.5" fill="#047857" text-anchor="middle">Virtual Pinhole Sensor</text>

      <!-- Arrow 1: Camera raw image -->
      <path d="M 170 135 L 235 135" fill="none" stroke="#059669" stroke-width="2.5" marker-end="url(#arrow-green)" />
      <text x="202" y="125" font-family="'JetBrains Mono', monospace" font-size="7.5" fill="#047857" text-anchor="middle">/rgb_cam/image_raw</text>
      <text x="202" y="148" font-family="'Plus Jakarta Sans', sans-serif" font-size="6.5" fill="#64748b" text-anchor="middle">sensor_msgs/Image (15Hz)</text>

      <!-- Perception Node Box -->
      <rect x="240" y="20" width="220" height="180" rx="10" fill="#f0fdf4" stroke="#10b981" stroke-width="2" />
      <text x="350" y="42" font-family="'Plus Jakarta Sans', sans-serif" font-size="10" font-weight="700" fill="#065f46" text-anchor="middle">ANIMAL_RECOGNITION NODE</text>

      <rect x="255" y="55" width="190" height="30" rx="6" fill="#ffffff" stroke="#cbd5e1" />
      <text x="350" y="73" font-family="'JetBrains Mono', monospace" font-size="8" fill="#0f172a" text-anchor="middle">cv_bridge: ROS ➔ OpenCV BGR8</text>

      <rect x="255" y="92" width="190" height="30" rx="6" fill="#ffffff" stroke="#cbd5e1" />
      <text x="350" y="110" font-family="'JetBrains Mono', monospace" font-size="8" fill="#0f172a" text-anchor="middle">CIELAB CLAHE Micro-Contrast</text>

      <rect x="255" y="129" width="190" height="30" rx="6" fill="#ffffff" stroke="#cbd5e1" />
      <text x="350" y="147" font-family="'JetBrains Mono', monospace" font-size="8" font-weight="600" fill="#059669" text-anchor="middle">YOLOv8n Inference (CPU)</text>

      <rect x="255" y="165" width="190" height="26" rx="6" fill="#ffffff" stroke="#cbd5e1" />
      <text x="350" y="181" font-family="'JetBrains Mono', monospace" font-size="7.5" fill="#334155" text-anchor="middle">EMA Box Smoothing & Depth Math</text>

      <!-- Arrow 2: Detection Status Telemetry -->
      <path d="M 460 135 L 525 135" fill="none" stroke="#0284c7" stroke-width="2.5" marker-end="url(#arrow-blue)" />
      <text x="492" y="125" font-family="'JetBrains Mono', monospace" font-size="7.5" fill="#0369a1" text-anchor="middle">/detection_status</text>
      <text x="492" y="148" font-family="'Plus Jakarta Sans', sans-serif" font-size="6.5" fill="#64748b" text-anchor="middle">std_msgs/String (JSON)</text>

      <!-- Control Node Box -->
      <rect x="530" y="20" width="215" height="180" rx="10" fill="#f0f9ff" stroke="#0284c7" stroke-width="2" />
      <text x="637" y="42" font-family="'Plus Jakarta Sans', sans-serif" font-size="10" font-weight="700" fill="#0369a1" text-anchor="middle">AUTONOMOUS_PATROL NODE</text>

      <rect x="545" y="60" width="185" height="42" rx="6" fill="#ffffff" stroke="#cbd5e1" />
      <text x="637" y="78" font-family="'JetBrains Mono', monospace" font-size="8" font-weight="700" fill="#0f172a" text-anchor="middle">4-State Finite State Machine</text>
      <text x="637" y="92" font-family="'Plus Jakarta Sans', sans-serif" font-size="7" fill="#64748b" text-anchor="middle">SCAN ➔ CREEP ➔ TRACK ➔ BOUNCE</text>

      <rect x="545" y="115" width="185" height="42" rx="6" fill="#ffffff" stroke="#cbd5e1" />
      <text x="637" y="133" font-family="'JetBrains Mono', monospace" font-size="8" font-weight="700" fill="#0284c7" text-anchor="middle">Proportional Visual Servoing</text>
      <text x="637" y="147" font-family="'Plus Jakarta Sans', sans-serif" font-size="7" fill="#64748b" text-anchor="middle">kp_steer = 0.0028 | stop_dist = 3.0m</text>

      <!-- Feedback Arrow: cmd_vel from Patrol to Gazebo Diff Drive -->
      <path d="M 637 205 L 637 215 L 95 215 L 95 185" fill="none" stroke="#ef4444" stroke-width="2" stroke-dasharray="4,3" marker-end="url(#arrow-red)" />
      <text x="365" y="212" font-family="'JetBrains Mono', monospace" font-size="7.5" fill="#dc2626" text-anchor="middle">/animal_robot/cmd_vel (geometry_msgs/Twist) ➔ libgazebo_ros_diff_drive.so</text>

      <defs>
        <marker id="arrow-green" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M 0 1 L 10 5 L 0 9 z" fill="#059669" />
        </marker>
        <marker id="arrow-blue" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M 0 1 L 10 5 L 0 9 z" fill="#0284c7" />
        </marker>
        <marker id="arrow-red" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M 0 1 L 10 5 L 0 9 z" fill="#ef4444" />
        </marker>
      </defs>
    </svg>
    <div class="diagram-caption">Figure 2.1: Closed-Loop Computational Architecture & ROS 2 Middleware Graph</div>
  </div>

  <h2 class="sub-title">2.2 ROS 2 Topic & Interface Specifications</h2>
  <table class="custom-table">
    <thead>
      <tr>
        <th>Topic Name</th>
        <th>Message Type</th>
        <th>Publisher Node</th>
        <th>Subscriber Node</th>
        <th>Frequency</th>
        <th>Data Payload & Purpose</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><code class="inline-code">/rgb_cam/image_raw</code></td>
        <td><span class="table-badge badge-blue">sensor_msgs/Image</span></td>
        <td><code class="inline-code">gazebo_ros_camera</code></td>
        <td><code class="inline-code">animal_recognition_node</code></td>
        <td>15 Hz</td>
        <td>Raw 640x480 RGB8 sensor frames from virtual pinhole camera.</td>
      </tr>
      <tr>
        <td><code class="inline-code">/rgb_cam/camera_info</code></td>
        <td><span class="table-badge badge-gray">sensor_msgs/CameraInfo</span></td>
        <td><code class="inline-code">gazebo_ros_camera</code></td>
        <td>ROS 2 standard nodes</td>
        <td>15 Hz</td>
        <td>Camera intrinsic matrix K, distortion coefficients, optical frame ID.</td>
      </tr>
      <tr>
        <td><code class="inline-code">/animal_detection/annotated_image</code></td>
        <td><span class="table-badge badge-blue">sensor_msgs/Image</span></td>
        <td><code class="inline-code">animal_recognition_node</code></td>
        <td>RViz / rqt_image_view</td>
        <td>15 Hz</td>
        <td>Annotated imagery displaying bounding boxes, distance, and HUD overlay.</td>
      </tr>
      <tr>
        <td><code class="inline-code">/animal_detection/detection_status</code></td>
        <td><span class="table-badge badge-green">std_msgs/String</span></td>
        <td><code class="inline-code">animal_recognition_node</code></td>
        <td><code class="inline-code">autonomous_patrol_node</code></td>
        <td>15 Hz</td>
        <td>JSON formatted telemetry (target presence, label, confidence, distance, bounding box coordinates).</td>
      </tr>
      <tr>
        <td><code class="inline-code">/animal_robot/cmd_vel</code></td>
        <td><span class="table-badge badge-amber">geometry_msgs/Twist</span></td>
        <td><code class="inline-code">autonomous_patrol_node</code> or teleop</td>
        <td><code class="inline-code">differential_drive_controller</code></td>
        <td>10 Hz</td>
        <td>Linear velocity (x) and angular yaw rate (z) sent to differential drive plugin.</td>
      </tr>
    </tbody>
  </table>

  <h2 class="sub-title">2.3 Message Serialization & cv_bridge Mechanics</h2>
  <p>
    ROS 2 nodes transmit image messages as serialized byte arrays formatted according to the <code class="inline-code">sensor_msgs/msg/Image</code> specification (width, height, encoding, step, data). Computer vision algorithms in OpenCV and PyTorch require contiguous NumPy memory buffers arranged in BGR format. The project uses <strong>cv_bridge</strong> to achieve zero-copy or minimal-overhead pointer conversions:
  </p>
  <div class="code-header"><span>Conversion Pipeline: sensor_msgs/Image ➔ OpenCV BGR8</span><span>ros_recognition_yolo.py</span></div>
  <div class="code-block">
# Ingest ROS 2 Image message into native OpenCV NumPy array
try:
    cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
except CvBridgeError as e:
    self.get_logger().error(f'CvBridge Error: {e}')
    return

# After CLAHE enhancement, inference, and HUD rendering, publish back:
out_msg = self.bridge.cv2_to_imgmsg(annotated_image, encoding='bgr8')
out_msg.header = msg.header  # Preserve original simulation timestamp
self.annotated_pub.publish(out_msg)
  </div>

  <h2 class="sub-title">2.4 Latency Budget & Real-Time Factor (RTF) Analysis</h2>
  <p>
    On standard non-GPU laptop architectures (such as Intel Core i5 with 16 GB RAM), executing physics simulation and deep neural network inference simultaneously can easily overwhelm the CPU, causing Gazebo's Real Time Factor (RTF = Simulated Time / Wall Clock Time) to plummet from 1.0 down to 0.3. This project introduces a three-tier optimization strategy to guarantee RTF &ge; 0.95:
  </p>
  <ul>
    <li><strong>Inference Throttling (<code class="inline-code">frame_skip = 1</code>):</strong> YOLOv8 is evaluated on every 2nd incoming video frame. Intermediate frames reuse smoothed bounding boxes, immediately slicing CPU neural compute load by 50% without dropping HUD frame rates.</li>
    <li><strong>Shadow Rasterization Bypass:</strong> Dynamic solar shadow casting is disabled (<code class="inline-code">&lt;cast_shadows&gt;false&lt;/cast_shadows&gt;</code>) in Gazebo world SDF files, reducing GPU/CPU polygon fragment shader overhead by ~65%.</li>
    <li><strong>Decoupled Physical Rates:</strong> Differential drive physics runs at 50 Hz, camera publishing at 15 Hz, patrol control at 10 Hz, and YOLO inference at ~7.5 Hz (every 133 ms). This decoupled frequency hierarchy ensures physics stability while keeping inference latency well within the robot's stopping distance window.</li>
  </ul>
</div>
"""

def get_ch3():
    return """
<!-- ==================== CHAPTER 3 ==================== -->
<div class="page-break">
  <h1 class="section-title"><span class="section-num">03</span> Robot Kinematics, Mechanical Anatomy & URDF Modeling</h1>

  <h2 class="sub-title">3.1 Physical Robot Specification & Dimensional Geometry</h2>
  <p>
    The robot, designated as <code class="inline-code">animal_robot</code>, is modeled in XML using the <strong>Unified Robot Description Format (URDF)</strong>. It utilizes a two-wheel differential drive configuration paired with a passive, low-friction front spherical caster ball. This mechanical topology grants the vehicle zero-radius turning agility, essential for scanning dense woodlands without colliding with trees.
  </p>

  <div class="two-col avoid-break">
    <div class="card-box">
      <h4>Chassis & Mass Properties</h4>
      <ul>
        <li><strong>Chassis Box:</strong> 0.22 m (L) &times; 0.12 m (W) &times; 0.06 m (H)</li>
        <li><strong>Chassis Mass:</strong> 3.0 kg</li>
        <li><strong>Inertia Matrix (kg&middot;m²):</strong>
          <br><code class="inline-code">Ixx=0.008, Iyy=0.015, Izz=0.020</code>
        </li>
        <li><strong>Center of Mass:</strong> [0, 0, -0.02] m (low COM ensures pitch/roll stability during acceleration)</li>
      </ul>
    </div>
    <div class="card-box">
      <h4>Actuation & Caster Assembly</h4>
      <ul>
        <li><strong>Wheel Diameter (2r):</strong> 0.07 m (Radius r = 0.035 m)</li>
        <li><strong>Track Separation (L):</strong> 0.12 m</li>
        <li><strong>Wheel Mass / Inertia:</strong> 0.3 kg / <code class="inline-code">Izz=0.0002</code></li>
        <li><strong>Wheel Friction (&mu;1, &mu;2):</strong> 1.5 (High traction rubber)</li>
        <li><strong>Caster Sphere:</strong> Radius 0.015 m, Mass 0.2 kg, &mu;=0.001 (Ultra-low friction frictionless glide)</li>
      </ul>
    </div>
  </div>

  <h2 class="sub-title">3.2 Differential Drive Kinematics Equations</h2>
  <p>
    Let $(x, y, \theta)$ represent the robot's pose in the 2D planar global coordinate frame, where $\theta$ is the heading (yaw) angle relative to the global X-axis. Let $v$ represent the forward linear velocity along the robot's longitudinal axis, and $\omega$ represent the angular yaw rate about the vertical Z-axis.
  </p>

  <div class="math-card">
    <div class="math-equation">
      v = \frac{r}{2} (\omega_R + \omega_L) \quad , \quad \omega = \frac{r}{L} (\omega_R - \omega_L)
    </div>
    <div class="math-explanation">
      <strong>Forward Kinematics:</strong> Calculates linear velocity $v$ and angular velocity $\omega$ from right wheel speed $\omega_R$ and left wheel speed $\omega_L$.
    </div>
  </div>

  <div class="math-card">
    <div class="math-equation">
      \omega_R = \frac{v + \frac{L}{2}\omega}{r} \quad , \quad \omega_L = \frac{v - \frac{L}{2}\omega}{r}
    </div>
    <div class="math-explanation">
      <strong>Inverse Kinematics:</strong> Used by the Gazebo differential drive plugin to compute required wheel angular velocities from commanded linear/angular velocities in <code class="inline-code">cmd_vel</code>.
    </div>
  </div>

  <p>
    The robot rotates about an instantaneous point known as the <strong>Instantaneous Center of Curvature (ICC)</strong>. The distance $R$ from the center of the robot chassis to the ICC is given by:
  </p>
  <div class="math-card">
    <div class="math-equation">
      R = \frac{v}{\omega} = \frac{L}{2} \cdot \left( \frac{\omega_R + \omega_L}{\omega_R - \omega_L} \right)
    </div>
    <div class="math-explanation">
      When $\omega_R = -\omega_L$, $R = 0$, producing a pure in-place rotation (zero turning radius, used in the <code class="inline-code">SCAN_SWEEP</code> state).
    </div>
  </div>

  <p>
    The differential drive robot is subject to a <strong>non-holonomic kinematic constraint</strong> representing the assumption of rolling without lateral slip:
  </p>
  <div class="math-card">
    <div class="math-equation">
      \dot{y} \cos\theta - \dot{x} \sin\theta = 0
    </div>
    <div class="math-explanation">
      The robot cannot accelerate sideways directly along its lateral Y-axis; any displacement must be achieved via combined linear translation and heading rotation.
    </div>
  </div>

  <h2 class="sub-title">3.3 URDF Kinematic Structure & Plugin Binding</h2>
  <p>The robot URDF (<code class="inline-code">animal_robot.urdf</code>) defines the tree of rigid bodies (links) connected by actuated or fixed joints:</p>

  <table class="custom-table">
    <thead>
      <tr>
        <th>Parent Link</th>
        <th>Child Link</th>
        <th>Joint Name</th>
        <th>Joint Type</th>
        <th>Transform (Origin xyz / rpy)</th>
        <th>Function</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><code class="inline-code">base_link</code></td>
        <td><code class="inline-code">chassis</code></td>
        <td><code class="inline-code">base_link_joint</code></td>
        <td>fixed</td>
        <td><code class="inline-code">0 0 0 / 0 0 0</code></td>
        <td>Root geometric reference point on the ground plane.</td>
      </tr>
      <tr>
        <td><code class="inline-code">chassis</code></td>
        <td><code class="inline-code">right_wheel</code></td>
        <td><code class="inline-code">joint_right_wheel</code></td>
        <td>continuous</td>
        <td><code class="inline-code">-0.05 0.06 -0.025 / 0 0 0</code></td>
        <td>Actuated right drive wheel; continuous rotation about Y-axis.</td>
      </tr>
      <tr>
        <td><code class="inline-code">chassis</code></td>
        <td><code class="inline-code">left_wheel</code></td>
        <td><code class="inline-code">joint_left_wheel</code></td>
        <td>continuous</td>
        <td><code class="inline-code">-0.05 -0.06 -0.025 / 0 0 0</code></td>
        <td>Actuated left drive wheel; continuous rotation about Y-axis.</td>
      </tr>
      <tr>
        <td><code class="inline-code">chassis</code></td>
        <td><code class="inline-code">front_pitch_link</code></td>
        <td><code class="inline-code">front_pitch_joint</code></td>
        <td>fixed</td>
        <td><code class="inline-code">0.08 0 -0.045 / 0 0 0</code></td>
        <td>Low-friction caster ball supporting front weight.</td>
      </tr>
      <tr>
        <td><code class="inline-code">chassis</code></td>
        <td><code class="inline-code">rgb_cam_camera_link</code></td>
        <td><code class="inline-code">rgb_cam_camera_link_joint</code></td>
        <td>fixed</td>
        <td><code class="inline-code">0.09 0.0 0.08 / 0 0 0</code></td>
        <td>Forward-facing optical sensor mount elevated above chassis.</td>
      </tr>
    </tbody>
  </table>

  <h2 class="sub-title">3.4 Gazebo Differential Drive Plugin Parameters</h2>
  <p>The differential drive plugin executes closed-loop velocity control inside Gazebo physics:</p>
  <div class="code-header"><span>Differential Drive Controller Tag</span><span>animal_robot.urdf</span></div>
  <div class="code-block">
&lt;plugin filename="libgazebo_ros_diff_drive.so" name="differential_drive_controller"&gt;
  &lt;ros&gt;&lt;namespace&gt;/animal_robot&lt;/namespace&gt;&lt;/ros&gt;
  &lt;update_rate&gt;50&lt;/update_rate&gt;
  &lt;left_joint&gt;joint_right_wheel&lt;/left_joint&gt;
  &lt;right_joint&gt;joint_left_wheel&lt;/right_joint&gt;
  &lt;wheel_separation&gt;0.12&lt;/wheel_separation&gt;
  &lt;wheel_diameter&gt;0.07&lt;/wheel_diameter&gt;
  &lt;max_wheel_torque&gt;20.0&lt;/max_wheel_torque&gt;
  &lt;max_wheel_acceleration&gt;5.0&lt;/max_wheel_acceleration&gt;
  &lt;publish_odom&gt;true&lt;/publish_odom&gt;
  &lt;publish_odom_tf&gt;true&lt;/publish_odom_tf&gt;
  &lt;odometry_frame&gt;odom&lt;/odometry_frame&gt;
  &lt;robot_base_frame&gt;chassis&lt;/robot_base_frame&gt;
&lt;/plugin&gt;
  </div>
</div>
"""


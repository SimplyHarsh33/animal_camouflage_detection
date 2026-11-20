# -*- coding: utf-8 -*-
"""Part 4: Autonomous Patrol FSM, Visual Servoing, AI Training & Docker"""

def get_part4():
    return """
<!-- ==================== PART 4 ==================== -->
<div class="page-break">
  <div class="part-header-card border-blue">
    <div class="part-badge badge-blue">MODULE 4 OF 4</div>
    <h1 class="part-title">Part 4: Autonomous Navigation, Visual Servoing, AI Training & DevOps</h1>
    <p class="part-subtitle">
      Comprehensive technical handbook covering the 4-state autonomous patrol Finite State Machine (FSM), proportional visual servoing control laws, synthetic dataset capture, YOLOv8 training hyperparameters, multi-layer Docker containerization, X11 GUI forwarding, and cross-subsystem integration defense.
    </p>
  </div>

  <h2 class="sub-title">4.1 Subsystem Role Distribution & Core Ownership</h2>
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
        <td><strong>Autonomous State Machine Lead</strong></td>
        <td><strong>Behavioral Robotics & Patrol Sequencing</strong></td>
        <td>
          &bull; Authoring <code class="inline-code">autonomous_patrol.py</code> state transition engine.<br>
          &bull; Implementing 360° rotational sweep (<code class="inline-code">SCAN_SWEEP</code>).<br>
          &bull; Formulating sinusoidal FOV expansion weave (<code class="inline-code">EXPLORE_CREEP</code>).<br>
          &bull; 5.0-second target inspection hold and sector exit bounce.
        </td>
        <td>FSM state transitions, S-curve weave mathematics, timeout overrides.</td>
      </tr>
      <tr>
        <td><strong>Visual Servoing & Control Lead</strong></td>
        <td><strong>Closed-Loop Image-Based Steering</strong></td>
        <td>
          &bull; Formulating proportional image-based steering law (Kp = 0.0028).<br>
          &bull; Calculating horizontal tracking error (Center X difference).<br>
          &bull; Enforcing standoff distance holding (3.0m) via depth telemetry.<br>
          &bull; Velocity saturation limits (yaw speed capped at 0.45 rad/s).
        </td>
        <td>Visual servoing P-control law, closed-loop stability, standoff holding.</td>
      </tr>
      <tr>
        <td><strong>AI Training & Datasets Lead</strong></td>
        <td><strong>Synthetic Datasets & YOLOv8 Fine-Tuning</strong></td>
        <td>
          &bull; Authoring synthetic frame capture node (<code class="inline-code">capture_dataset.py</code>).<br>
          &bull; Organizing YOLO dataset standard (<code class="inline-code">data.yaml</code>, normalized labels).<br>
          &bull; Camouflage data augmentations (HSV jitter, mosaic, mixup).<br>
          &bull; Authoring fine-tuning training script (<code class="inline-code">train_camouflage_yolo.py</code>).
        </td>
        <td>Data augmentation strategies for camouflage, loss functions, mAP metrics.</td>
      </tr>
      <tr>
        <td><strong>DevOps & Systems Integration Lead</strong></td>
        <td><strong>Docker Containers, X11 & Colcon Builds</strong></td>
        <td>
          &bull; Architecting multi-layer <code class="inline-code">Dockerfile</code> (Ubuntu 22.04 + ROS 2 + PyTorch).<br>
          &bull; Configuring host X11 display forwarding in <code class="inline-code">start_docker.sh</code>.<br>
          &bull; Implementing software rendering flags (<code class="inline-code">LIBGL_ALWAYS_SOFTWARE=1</code>).<br>
          &bull; Managing colcon workspace build systems and symlink sourcing.
        </td>
        <td>Docker architecture, X11 UNIX socket bridging, software GL rendering.</td>
      </tr>
    </tbody>
  </table>

  <h2 class="sub-title">4.2 Autonomous 4-State Finite State Machine (FSM)</h2>
  <p>
    The robot's autonomous exploration and target inspection logic is governed by a deterministic <strong>Finite State Machine (FSM)</strong> implemented in <code class="inline-code">packages/animal_control/scripts/autonomous_patrol.py</code>, executing at 10 Hz:
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
      <path d="M 170 65 L 230 65" fill="none" stroke="#64748b" stroke-width="1.8" marker-end="url(#arrow-fsm2)" />
      <text x="200" y="58" font-family="'Plus Jakarta Sans', sans-serif" font-size="6.5" fill="#64748b" text-anchor="middle">360° Done</text>

      <!-- State 2: EXPLORE_CREEP -->
      <rect x="235" y="30" width="165" height="70" rx="8" fill="#f0f9ff" stroke="#0284c7" stroke-width="2"/>
      <text x="317" y="55" font-family="'Plus Jakarta Sans', sans-serif" font-size="9" font-weight="700" fill="#0369a1" text-anchor="middle">2. EXPLORE_CREEP</text>
      <text x="317" y="70" font-family="'JetBrains Mono', monospace" font-size="7.5" fill="#0284c7" text-anchor="middle">v=0.22, w=0.14*sin(1.5t)</text>
      <text x="317" y="84" font-family="'Plus Jakarta Sans', sans-serif" font-size="7" fill="#64748b" text-anchor="middle">S-Curve Weave FOV Expansion</text>

      <!-- Arrow 2 to 1 (Timeout loop) -->
      <path d="M 317 30 C 317 10, 95 10, 95 30" fill="none" stroke="#64748b" stroke-width="1.5" stroke-dasharray="3,3" marker-end="url(#arrow-fsm2)" />
      <text x="206" y="16" font-family="'Plus Jakarta Sans', sans-serif" font-size="6.5" fill="#64748b" text-anchor="middle">After 9.0s Creep ➔ New Scan</text>

      <!-- Target Spotted Interrupt Arrow to State 3 -->
      <path d="M 317 100 L 317 130 L 515 130" fill="none" stroke="#059669" stroke-width="2" marker-end="url(#arrow-fsm-green2)" />
      <path d="M 95 100 L 95 130 L 515 130" fill="none" stroke="#059669" stroke-width="2" />
      <text x="310" y="124" font-family="'Plus Jakarta Sans', sans-serif" font-size="7" font-weight="700" fill="#047857" text-anchor="middle">TARGET SPOTTED! (Interrupt)</text>

      <!-- State 3: TRACK_TARGET -->
      <rect x="520" y="85" width="220" height="90" rx="8" fill="#fefce8" stroke="#ca8a04" stroke-width="2"/>
      <text x="630" y="108" font-family="'Plus Jakarta Sans', sans-serif" font-size="9" font-weight="700" fill="#854d0e" text-anchor="middle">3. TRACK_TARGET (Servoing)</text>
      <text x="630" y="123" font-family="'JetBrains Mono', monospace" font-size="7.5" fill="#a16207" text-anchor="middle">w = kp*(320 - cx) | Approach</text>
      <text x="630" y="138" font-family="'JetBrains Mono', monospace" font-size="7.5" fill="#a16207" text-anchor="middle">If Dist &lt;= 3.0m ➔ Halt (v=0)</text>
      <text x="630" y="153" font-family="'Plus Jakarta Sans', sans-serif" font-size="7" fill="#713f12" text-anchor="middle">Hold Scientific Inspection for 5.0s</text>

      <!-- Arrow 3 to 4 -->
      <path d="M 630 175 L 630 205 L 430 205" fill="none" stroke="#9333ea" stroke-width="2" marker-end="url(#arrow-fsm-purple2)" />
      <text x="530" y="200" font-family="'Plus Jakarta Sans', sans-serif" font-size="7" fill="#7e22ce" text-anchor="middle">Inspection Complete (5.0s)</text>

      <!-- State 4: TURN_BOUNCE -->
      <rect x="250" y="170" width="175" height="55" rx="8" fill="#faf5ff" stroke="#9333ea" stroke-width="2"/>
      <text x="337" y="192" font-family="'Plus Jakarta Sans', sans-serif" font-size="9" font-weight="700" fill="#6b21a8" text-anchor="middle">4. TURN_BOUNCE</text>
      <text x="337" y="206" font-family="'JetBrains Mono', monospace" font-size="7.5" fill="#7e22ce" text-anchor="middle">w = 0.40 rad/s (for 3.5s)</text>
      <text x="337" y="218" font-family="'Plus Jakarta Sans', sans-serif" font-size="6.5" fill="#64748b" text-anchor="middle">Turns ~110° to explore new sector</text>

      <!-- Arrow 4 back to 2 -->
      <path d="M 250 197 L 195 197 L 195 75 L 235 75" fill="none" stroke="#64748b" stroke-width="1.8" marker-end="url(#arrow-fsm2)" />
      <text x="175" y="140" font-family="'Plus Jakarta Sans', sans-serif" font-size="6.5" fill="#64748b" text-anchor="middle" transform="rotate(-90 175 140)">Advance Sector</text>

      <defs>
        <marker id="arrow-fsm2" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
          <path d="M 0 1 L 10 5 L 0 9 z" fill="#64748b" />
        </marker>
        <marker id="arrow-fsm-green2" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
          <path d="M 0 1 L 10 5 L 0 9 z" fill="#059669" />
        </marker>
        <marker id="arrow-fsm-purple2" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
          <path d="M 0 1 L 10 5 L 0 9 z" fill="#9333ea" />
        </marker>
      </defs>
    </svg>
    <div class="diagram-caption">Figure 4.1: Autonomous Camouflage Search & Visual Servoing State Transition Diagram</div>
  </div>

  <h2 class="sub-title">4.3 Proportional Visual Servoing Control Law</h2>
  <p>
    When a camouflaged animal is acquired, the controller switches instantly to <code class="inline-code">STATE_TRACK_TARGET</code>. It calculates the horizontal pixel error between the image center and the animal's bounding box center:
  </p>

  <div class="formula-box">
    <div class="formula-title">Proportional Visual Servoing Steering Formula</div>
    <div class="formula-main">
      Steering Turn Speed (&omega;<sub>z</sub>) = Sensitivity Gain (K<sub>p</sub>) &times; (Image Center X &minus; Detected Target Center X)
    </div>
    <div class="formula-details">
      With Image Center = 320 pixels (half of 640 px) and Sensitivity Gain K<sub>p</sub> = 0.0028:
      <br><strong>Steering Speed (&omega;<sub>z</sub>) = 0.0028 &times; (320 &minus; Animal Center X) rad/s</strong>
      <br><em>(Output is safely capped between &minus;0.45 and +0.45 rad/s to prevent aggressive skidding)</em>
    </div>
    <div class="formula-explanation">
      <strong>What this means in plain words:</strong>
      <br>&bull; If the deer is spotted on the <strong>right side of the screen</strong> (e.g. at pixel 420):
      <br>Error = 320 &minus; 420 = &minus;100 pixels &rarr; Turn Speed = 0.0028 &times; (&minus;100) = <strong>&minus;0.28 rad/s</strong> (the robot smoothly turns right to center the deer).
      <br>&bull; If the deer is spotted on the <strong>left side</strong> (e.g. at pixel 220):
      <br>Error = 320 &minus; 220 = +100 pixels &rarr; Turn Speed = 0.0028 &times; (+100) = <strong>+0.28 rad/s</strong> (the robot turns left to center the deer).
      <br>&bull; When the deer is <strong>dead-center at pixel 320</strong>:
      <br>Error = 0 pixels &rarr; Turn Speed = 0 rad/s (the robot drives straight forward directly toward the animal).
    </div>
  </div>

  <div class="code-header"><span>Visual Servoing & Standoff Logic</span><span>autonomous_patrol.py</span></div>
  <div class="code-block">
cx = self.primary_target['center_x']
dist = self.primary_target['distance_m']
error_x = self.image_center_x - cx

# Proportional steering to center target in FOV
angular_z = float(self.kp_steer * error_x)
angular_z = max(min(angular_z, 0.45), -0.45)

# Standoff Inspection Logic
if dist > self.stop_distance:
    linear_x = self.forward_speed * 0.7  # Cautious approach (0.154 m/s)
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
        self.get_logger().info(f'TARGET ACQUIRED: Holding inspection at {dist:.1f}m')

    # Hold inspection for 5 seconds, then resume search
    if (now - self.inspection_start_time) > 5.0:
        self.state = self.STATE_TURN_BOUNCE
        self.state_start_time = now
  </div>

  <div class="formula-box">
    <div class="formula-title">Sinusoidal Field-of-View Expansion Weave Formula</div>
    <div class="formula-main">
      Weaving Turn Speed (&omega;) = 0.14 &times; sin(1.5 &times; Elapsed Time) rad/s
    </div>
    <div class="formula-explanation">
      <strong>What this means in plain words:</strong> While driving forward at 0.22 m/s, the robot gently wiggles its heading from side to side in an S-curve wave. Because the camera is fixed to the robot chassis, this weaving motion widens the camera's effective field of view from 80 degrees to over 115 degrees across the forest floor, discovering animals hidden off to the sides!
    </div>
  </div>

  <h2 class="sub-title">4.4 Synthetic Dataset Generation & Training Pipeline</h2>
  <p>
    Training neural networks for cryptic camouflage requires specialized datasets. The project implements an automated dataset collector (<code class="inline-code">training/capture_dataset.py</code>) that records camera frames from the Gazebo simulation:
  </p>
  <div class="code-block">
ros2 run animal_recognition capture_dataset.py --ros-args -p auto_interval_sec:=0.5
  </div>

  <h3 class="sub-sub-title">Data Augmentation Hyperparameters for Camouflage Feature Learning</h3>
  <p>
    Standard data augmentations can inadvertently destroy subtle camouflage boundaries. In <code class="inline-code">training/train_camouflage_yolo.py</code>, hyperparameters are specifically tuned:
  </p>
  <table class="custom-table">
    <thead>
      <tr>
        <th>Hyperparameter</th>
        <th>Setting</th>
        <th>Engineering Justification for Camouflage</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><code class="inline-code">hsv_h / hsv_s / hsv_v</code></td>
        <td>0.015 / 0.7 / 0.4</td>
        <td>Controlled color jitter; forces the network to learn fur texture patterns rather than memorizing exact RGB hue values.</td>
      </tr>
      <tr>
        <td><code class="inline-code">mosaic</code></td>
        <td>1.0</td>
        <td>Stitches 4 training images into one composite; forces multi-scale invariance and simulates heavy partial occlusion.</td>
      </tr>
      <tr>
        <td><code class="inline-code">mixup</code></td>
        <td>0.1</td>
        <td>Alpha-blends two training images; trains the model to discern faint target edges through transparent foliage.</td>
      </tr>
      <tr>
        <td><code class="inline-code">scale</code></td>
        <td>0.5</td>
        <td>Scales object size between 50% and 150%, ensuring robust detection across all 4 distance tiers.</td>
      </tr>
    </tbody>
  </table>

  <h2 class="sub-title">4.5 Docker Containerization & System Administration</h2>
  <p>
    The entire software stack (Ubuntu 22.04 LTS, ROS 2 Humble Desktop-Full, Gazebo Classic 11, PyTorch CPU, Ultralytics, and OpenCV) is containerized inside a multi-layer Docker image (<code class="inline-code">Dockerfile</code>):
  </p>

  <div class="two-col avoid-break">
    <div class="card-box">
      <h4>X11 Host Display Socket Bridging</h4>
      <p>
        In <code class="inline-code">start_docker.sh</code>, the host X11 display socket (<code class="inline-code">/tmp/.X11-unix</code>) is mounted into the container. Passing <code class="inline-code">--net=host</code> and <code class="inline-code">--ipc=host</code> enables zero-latency IPC communication between the container GUI threads and the host X11 display server.
      </p>
    </div>
    <div class="card-box">
      <h4>Headless & Software Rendering Flags</h4>
      <p>
        Setting <code class="inline-code">LIBGL_ALWAYS_SOFTWARE=1</code> forces Mesa software rasterization (LLVMpipe). This eliminates OpenGL driver crashes on laptops lacking discrete GPUs. Passing <code class="inline-code">QT_X11_NO_MITSHM=1</code> prevents Qt shared-memory errors across container namespaces.
      </p>
    </div>
  </div>

  <h2 class="sub-title">4.6 Part 4 Dedicated Viva & Oral Exam Defense Guide</h2>

  <div class="viva-card">
    <div class="viva-q"><span class="viva-badge">Q4.1</span> Explain the proportional visual servoing control law used during target tracking.</div>
    <div class="viva-concept">Topic Focus: Visual Servoing & Closed-Loop Steering</div>
    <div class="viva-ans">
      <strong>Model Answer:</strong>
      Our controller implements Image-Based Visual Servoing (IBVS). It computes horizontal tracking error as the difference between the optical image center (320 pixels) and the target animal's detected horizontal center coordinate.
      <br><br>
      The commanded angular yaw velocity is computed using a proportional gain of Kp = 0.0028:
      <br>Turn Speed = 0.0028 &times; (320 &minus; Target Center X) rad/s.
      <br><br>
      If the target is to the right of center, the error is negative, commanding a smooth clockwise turn to bring the animal back into the center of the camera view. The output is clamped to [-0.45, 0.45] rad/s to guarantee smooth, non-aggressive steering dynamics.
    </div>
  </div>

  <div class="viva-card">
    <div class="viva-q"><span class="viva-badge">Q4.2</span> Why does the robot execute a sinusoidal S-curve weave during exploration?</div>
    <div class="viva-concept">Topic Focus: Behavioral Robotics & FOV Expansion</div>
    <div class="viva-ans">
      <strong>Model Answer:</strong>
      A fixed forward-facing monocular camera with an 80-degree horizontal field of view has blind spots on either side when moving in a straight line. Camouflaged animals hidden behind trees or rocks off the direct forward path would remain undetected.
      <br><br>
      By introducing a subtle sinusoidal yaw oscillation (0.14 &times; sin(1.5 &times; time)), the camera sweeps continuously across an expanded optical cone (covering approximately 115 degrees of effective visual field over the exploration leg), greatly increasing discovery probability without significantly deviating from the forward exploration path.
    </div>
  </div>

  <div class="viva-card">
    <div class="viva-q"><span class="viva-badge">Q4.3</span> What prevents the robot from getting permanently stuck inspecting the same animal forever?</div>
    <div class="viva-concept">Topic Focus: Finite State Machine State Sequencing</div>
    <div class="viva-ans">
      <strong>Model Answer:</strong>
      When the robot reaches the 3.0-meter standoff threshold, it initiates a 5.0-second countdown timer (<code class="inline-code">inspection_start_time</code>). 
      Once 5 seconds elapse:
      <ol>
        <li>The node logs confirmation of target inspection and increments the inspected target count.</li>
        <li>It forcibly overrides the tracking state and transitions to <code class="inline-code">STATE_TURN_BOUNCE</code>.</li>
        <li>During <code class="inline-code">TURN_BOUNCE</code>, the robot executes a sustained 3.5-second rotation at 0.40 rad/s (approximately 110 degrees deflection), slewing the camera away from the animal and breaking visual lock so exploration can resume in a fresh quadrant.</li>
      </ol>
    </div>
  </div>

  <div class="viva-card">
    <div class="viva-q"><span class="viva-badge">Q4.4</span> Why did you use Mosaic and MixUp augmentations during camouflage training?</div>
    <div class="viva-concept">Topic Focus: Deep Learning Data Augmentation</div>
    <div class="viva-ans">
      <strong>Model Answer:</strong>
      <strong>Mosaic (1.0):</strong> Stitches four training images into one composite canvas. This forces the model to recognize animals across four different scale factors simultaneously and creates synthetic crop boundaries, teaching the network to detect partially occluded animals behind trees.
      <br><br>
      <strong>MixUp (0.1):</strong> Linearly blends two images by superimposing them semi-transparently. This teaches the convolutional kernels to discern faint, translucent boundary edges, mimicking real-world scenarios where an animal's body is seen through thin foliage or brush.
    </div>
  </div>

  <div class="viva-card">
    <div class="viva-q"><span class="viva-badge">Q4.5</span> What do <code class="inline-code">LIBGL_ALWAYS_SOFTWARE=1</code> and <code class="inline-code">QT_X11_NO_MITSHM=1</code> do in your Docker setup?</div>
    <div class="viva-concept">Topic Focus: Containerization & Display Forwarding</div>
    <div class="viva-ans">
      <strong>Model Answer:</strong>
      <code class="inline-code">LIBGL_ALWAYS_SOFTWARE=1</code> instructs the Mesa 3D graphics library to bypass hardware GPU drivers and use CPU-based software rasterization (LLVMpipe). On laptops with integrated Intel graphics or non-NVIDIA GPUs, this prevents Gazebo and OGRE from crashing due to unsupported hardware calls.
      <br><br>
      <code class="inline-code">QT_X11_NO_MITSHM=1</code> disables the MIT Shared Memory Extension in Qt. Because the Docker container and host operate in separate IPC and memory namespaces, attempting to share memory segments for GUI rendering results in black screens or segmentation faults. Disabling it forces Qt to use standard X11 socket transmission, guaranteeing stable GUI rendering.
    </div>
  </div>
</div>
"""

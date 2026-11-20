# -*- coding: utf-8 -*-
"""Team Structure, Cover Page, and Master Division Map for 4 Project Modules"""

def get_cover():
    return """
<!-- ==================== COVER PAGE ==================== -->
<div class="cover-container">
  <div class="cover-top-content">
    <div class="cover-badge">Academic Reference & Project Defense Manual</div>
    <h1 class="cover-title">Autonomous Camouflage<br><span>Animal Detection</span> System</h1>
    <p class="cover-subtitle">
      A Comprehensive Technical Treatise and Subsystem Division Handbook for ROS 2 Humble & Gazebo Classic 11 Simulation, Contrast-Enhanced YOLOv8 Perception, Differential Drive Kinematics, Procedural World Synthesis, and Closed-Loop Autonomous Visual Servoing.
    </p>
    <div class="cover-divider"></div>

    <div class="cover-team-grid">
      <div class="team-box-card border-green">
        <div class="team-card-header">
          <span class="team-pill pill-green">Part 1</span>
          <span class="team-tag">Robotics & Hardware</span>
        </div>
        <h4 class="team-card-title">Robot Kinematics, Mechanical Modeling & Optical Sensors</h4>
        <p class="team-card-desc">URDF design, differential drive forward/inverse kinematics, turning radius math, wheel contact dynamics, virtual pinhole camera sensor, and coordinate transform trees (TF2).</p>
        <div class="team-files-tag"><strong>Primary Files:</strong> animal_robot.urdf, spawn_robot.launch.py</div>
      </div>

      <div class="team-box-card border-purple">
        <div class="team-card-header">
          <span class="team-pill pill-purple">Part 2</span>
          <span class="team-tag">Simulation & Ecology</span>
        </div>
        <h4 class="team-card-title">Gazebo 3D World, Procedural Forests & Domain Randomization</h4>
        <p class="team-card-desc">SDF 1.6 architecture, procedural forest generator, obstacle spacing algorithms, multi-tier camouflage concealment, companion natural cover, solar lighting shifts, and CPU shadow optimizations.</p>
        <div class="team-files-tag"><strong>Primary Files:</strong> generate_random_world.py, animal_world.world, models/</div>
      </div>

      <div class="team-box-card border-amber">
        <div class="team-card-header">
          <span class="team-pill pill-amber">Part 3</span>
          <span class="team-tag">Vision & Deep Learning</span>
        </div>
        <h4 class="team-card-title">CIELAB CLAHE Micro-Contrast & YOLOv8 Camouflage Perception</h4>
        <p class="team-card-desc">Principles of camouflage crypsis, CIELAB color space, CLAHE contrast filter, YOLOv8 deep architecture, taxonomic ungulate prior mapping, monocular depth math, and tactical HUD.</p>
        <div class="team-files-tag"><strong>Primary Files:</strong> ros_recognition_yolo.py, recognition.launch.py</div>
      </div>

      <div class="team-box-card border-blue">
        <div class="team-card-header">
          <span class="team-pill pill-blue">Part 4</span>
          <span class="team-tag">Autonomy, AI & DevOps</span>
        </div>
        <h4 class="team-card-title">Autonomous Patrol FSM, Visual Servoing, AI Training & Docker</h4>
        <p class="team-card-desc">4-state patrol state machine, proportional visual servoing steering law, synthetic dataset collection, YOLO training hyperparameters, and Docker X11 deployment architecture.</p>
        <div class="team-files-tag"><strong>Primary Files:</strong> autonomous_patrol.py, train_camouflage_yolo.py, Dockerfile</div>
      </div>
    </div>
  </div>

  <div class="cover-footer">
    <span>Department of Computer Science & Robotics Engineering</span>
    <span>Autonomous Mobile Systems & Computer Vision Capstone</span>
    <span>Academic Year 2026-2027</span>
  </div>
</div>
"""

def get_toc():
    return """
<!-- ==================== MASTER TABLE OF CONTENTS & SUBSYSTEM MATRIX ==================== -->
<div class="page-break">
  <h1 class="section-title"><span class="section-num">00</span> Master Subsystem Syllabus & Cross-Integration</h1>
  
  <p>
    This project is organized into <strong>4 Specialized Technical Modules</strong>. Each part contains exhaustive architectural explanations, clear mathematical formulations in simple English, complete code walkthroughs, parameter justifications, and dedicated Viva / Oral Exam defense questions.
  </p>

  <h2 class="sub-title">Master Subsystem Allocation Matrix</h2>
  <table class="custom-table">
    <thead>
      <tr>
        <th style="width: 15%;">Project Part</th>
        <th style="width: 25%;">Subsystem Domain</th>
        <th style="width: 44%;">Core Topics & Workings to Master</th>
        <th style="width: 16%;">Source Files</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Part 1</strong></td>
        <td><strong>Robot Kinematics, URDF & Sensor Physics</strong></td>
        <td>
          &bull; 2-Wheel Differential Drive Forward & Inverse Kinematics<br>
          &bull; Turning Radius, Instantaneous Center of Curvature & No-Slip Limits<br>
          &bull; URDF rigid body link/joint trees, center of gravity & inertia<br>
          &bull; Gazebo diff-drive plugin (<code class="inline-code">libgazebo_ros_diff_drive.so</code>)<br>
          &bull; Pinhole camera sensor simulation & TF2 coordinate frames
        </td>
        <td><span class="table-badge badge-green">animal_robot.urdf</span><br><span class="table-badge badge-green">spawn_robot.launch.py</span></td>
      </tr>
      <tr>
        <td><strong>Part 2</strong></td>
        <td><strong>Gazebo 3D Simulation & Procedural Worlds</strong></td>
        <td>
          &bull; SDF 1.6 world specification vs URDF<br>
          &bull; Procedural generator: Distance-based obstacle spacing<br>
          &bull; 4 Camouflage concealment tiers (Close, Medium, Far, Flank)<br>
          &bull; Companion natural cover (trees & boulders within 1.2m of targets)<br>
          &bull; Solar domain randomization (sun angle and warmth shifts)<br>
          &bull; Visual vs Collision mesh decoupling for fast constant-time physics<br>
          &bull; Shadow disabling optimization for 1.0 Real Time Factor (RTF)
        </td>
        <td><span class="table-badge badge-purple">generate_random_world.py</span><br><span class="table-badge badge-purple">animal_world.world</span><br><span class="table-badge badge-purple">models/</span></td>
      </tr>
      <tr>
        <td><strong>Part 3</strong></td>
        <td><strong>Computer Vision & YOLOv8 Camouflage AI</strong></td>
        <td>
          &bull; Principles of Camouflage (crypsis, edge disruption, background matching)<br>
          &bull; CIELAB CLAHE micro-texture contrast filter (4&times;4 grid, clip 3.0)<br>
          &bull; YOLOv8n deep architecture (C2f modules, PAN-Net, decoupled head)<br>
          &bull; Ungulate taxonomic prior mapping (COCO quadrupeds ➔ DEER)<br>
          &bull; Monocular pinhole depth calculation: Distance = 515.025 / Box Height<br>
          &bull; Foliage false-positive suppression filter (confidence threshold 0.65)<br>
          &bull; Temporal box stabilization & tactical OpenCV HUD overlay
        </td>
        <td><span class="table-badge badge-amber">ros_recognition_yolo.py</span><br><span class="table-badge badge-amber">recognition.launch.py</span></td>
      </tr>
      <tr>
        <td><strong>Part 4</strong></td>
        <td><strong>Autonomous Navigation, AI Training & DevOps</strong></td>
        <td>
          &bull; 4-State Finite State Machine (SCAN, CREEP, TRACK, BOUNCE)<br>
          &bull; Proportional visual servoing steering controller (Kp = 0.0028)<br>
          &bull; Target approach & 5.0-second stationary inspection hold at 3.0m<br>
          &bull; Synthetic dataset capture node (<code class="inline-code">capture_dataset.py</code>)<br>
          &bull; YOLO training hyperparameters (HSV jitter, mosaic, mixup)<br>
          &bull; Two-phase training: synthetic pre-training to COD10K fine-tuning<br>
          &bull; Docker multi-layer architecture, X11 forwarding & colcon builds
        </td>
        <td><span class="table-badge badge-blue">autonomous_patrol.py</span><br><span class="table-badge badge-blue">train_camouflage_yolo.py</span><br><span class="table-badge badge-blue">capture_dataset.py</span><br><span class="table-badge badge-blue">Dockerfile, start_docker.sh</span></td>
      </tr>
    </tbody>
  </table>

  <h2 class="sub-title">System-Wide Inter-Module Dataflow Topology</h2>
  <div class="diagram-container avoid-break">
    <svg width="100%" height="160" viewBox="0 0 760 160" xmlns="http://www.w3.org/2000/svg">
      <!-- Part 2 Box -->
      <rect x="10" y="20" width="165" height="110" rx="8" fill="#faf5ff" stroke="#9333ea" stroke-width="2" />
      <text x="92" y="42" font-family="'Plus Jakarta Sans', sans-serif" font-size="10" font-weight="700" fill="#6b21a8" text-anchor="middle">PART 2: GAZEBO WORLD</text>
      <text x="92" y="58" font-family="'Plus Jakarta Sans', sans-serif" font-size="8" fill="#7e22ce" text-anchor="middle">Simulation & Environment</text>
      <rect x="25" y="70" width="135" height="48" rx="4" fill="#ffffff" stroke="#d8b4fe" />
      <text x="92" y="88" font-family="'JetBrains Mono', monospace" font-size="7.5" fill="#334155" text-anchor="middle">Procedural Forest & Deer</text>
      <text x="92" y="103" font-family="'JetBrains Mono', monospace" font-size="7.5" fill="#334155" text-anchor="middle">ODE Physics & Lighting</text>

      <!-- Arrow Part 2 to Part 1 -->
      <path d="M 175 75 L 205 75" fill="none" stroke="#64748b" stroke-width="2" marker-end="url(#arrow-flow)" />

      <!-- Part 1 Box -->
      <rect x="210" y="20" width="165" height="110" rx="8" fill="#ecfdf5" stroke="#10b981" stroke-width="2" />
      <text x="292" y="42" font-family="'Plus Jakarta Sans', sans-serif" font-size="10" font-weight="700" fill="#065f46" text-anchor="middle">PART 1: ROBOT & SENSORS</text>
      <text x="292" y="58" font-family="'Plus Jakarta Sans', sans-serif" font-size="8" fill="#047857" text-anchor="middle">Kinematics & Hardware</text>
      <rect x="225" y="70" width="135" height="48" rx="4" fill="#ffffff" stroke="#a7f3d0" />
      <text x="292" y="88" font-family="'JetBrains Mono', monospace" font-size="7.5" fill="#334155" text-anchor="middle">URDF Diff-Drive Wheels</text>
      <text x="292" y="103" font-family="'JetBrains Mono', monospace" font-size="7.5" fill="#334155" text-anchor="middle">Pinhole Camera Plugin</text>

      <!-- Arrow Part 1 to Part 3 -->
      <path d="M 375 75 L 405 75" fill="none" stroke="#059669" stroke-width="2.5" marker-end="url(#arrow-flow-green)" />
      <text x="390" y="66" font-family="'JetBrains Mono', monospace" font-size="7" fill="#047857" text-anchor="middle">Image</text>

      <!-- Part 3 Box -->
      <rect x="410" y="20" width="165" height="110" rx="8" fill="#fffbeb" stroke="#f59e0b" stroke-width="2" />
      <text x="492" y="42" font-family="'Plus Jakarta Sans', sans-serif" font-size="10" font-weight="700" fill="#92400e" text-anchor="middle">PART 3: VISION & YOLO</text>
      <text x="492" y="58" font-family="'Plus Jakarta Sans', sans-serif" font-size="8" fill="#b45309" text-anchor="middle">Perception & Detection</text>
      <rect x="425" y="70" width="135" height="48" rx="4" fill="#ffffff" stroke="#fde68a" />
      <text x="492" y="88" font-family="'JetBrains Mono', monospace" font-size="7.5" fill="#334155" text-anchor="middle">CIELAB CLAHE Filter</text>
      <text x="492" y="103" font-family="'JetBrains Mono', monospace" font-size="7.5" fill="#334155" text-anchor="middle">YOLOv8 + Depth Math</text>

      <!-- Arrow Part 3 to Part 4 -->
      <path d="M 575 75 L 605 75" fill="none" stroke="#d97706" stroke-width="2.5" marker-end="url(#arrow-flow-amber)" />
      <text x="590" y="66" font-family="'JetBrains Mono', monospace" font-size="7" fill="#b45309" text-anchor="middle">JSON</text>

      <!-- Part 4 Box -->
      <rect x="610" y="20" width="145" height="110" rx="8" fill="#f0f9ff" stroke="#0284c7" stroke-width="2" />
      <text x="682" y="42" font-family="'Plus Jakarta Sans', sans-serif" font-size="9.5" font-weight="700" fill="#0369a1" text-anchor="middle">PART 4: AUTONOMY</text>
      <text x="682" y="58" font-family="'Plus Jakarta Sans', sans-serif" font-size="8" fill="#0284c7" text-anchor="middle">Control & AI Pipeline</text>
      <rect x="620" y="70" width="125" height="48" rx="4" fill="#ffffff" stroke="#bae6fd" />
      <text x="682" y="88" font-family="'JetBrains Mono', monospace" font-size="7.5" fill="#334155" text-anchor="middle">4-State FSM Patrol</text>
      <text x="682" y="103" font-family="'JetBrains Mono', monospace" font-size="7.5" fill="#334155" text-anchor="middle">Visual Servoing Loop</text>

      <!-- Feedback Arrow Part 4 back to Part 1 Diff-Drive -->
      <path d="M 682 130 L 682 148 L 292 148 L 292 130" fill="none" stroke="#ef4444" stroke-width="2" stroke-dasharray="4,3" marker-end="url(#arrow-flow-red)" />
      <text x="492" y="144" font-family="'JetBrains Mono', monospace" font-size="7.5" fill="#dc2626" text-anchor="middle">cmd_vel (geometry_msgs/Twist 10 Hz) ➔ Actuate Left/Right Wheels</text>

      <defs>
        <marker id="arrow-flow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
          <path d="M 0 1 L 10 5 L 0 9 z" fill="#64748b" />
        </marker>
        <marker id="arrow-flow-green" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
          <path d="M 0 1 L 10 5 L 0 9 z" fill="#059669" />
        </marker>
        <marker id="arrow-flow-amber" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
          <path d="M 0 1 L 10 5 L 0 9 z" fill="#d97706" />
        </marker>
        <marker id="arrow-flow-red" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
          <path d="M 0 1 L 10 5 L 0 9 z" fill="#ef4444" />
        </marker>
      </defs>
    </svg>
    <div class="diagram-caption">Figure 0.1: Cross-Subsystem Modular Pipeline & Cyclic Control Loop</div>
  </div>
</div>
"""

# -*- coding: utf-8 -*-
"""Section content for the Master Handbook"""

def get_cover():
    return """
<!-- ==================== COVER PAGE ==================== -->
<div class="cover-container page-break">
  <div>
    <div class="cover-badge">Academic Reference & Project Defense Manual</div>
    <h1 class="cover-title">Autonomous Camouflage<br><span>Animal Detection</span> System</h1>
    <p class="cover-subtitle">
      A Comprehensive Technical Treatise on Real-Time Embedded Vision, Synthetic Ecology Simulation in ROS 2 & Gazebo, Contrast-Enhanced YOLOv8 Perception, and Closed-Loop Autonomous Visual Servoing.
    </p>
    <div class="cover-divider"></div>

    <div class="cover-meta-grid">
      <div class="meta-item">
        <span class="meta-label">Middleware Platform</span>
        <span class="meta-val">ROS 2 Humble Hawksbill (Linux / Docker)</span>
      </div>
      <div class="meta-item">
        <span class="meta-label">Physics & World Engine</span>
        <span class="meta-val">Gazebo Classic 11 (ODE Solver, SDF 1.6)</span>
      </div>
      <div class="meta-item">
        <span class="meta-label">Vision & Deep Learning</span>
        <span class="meta-val">YOLOv8n + CIELAB CLAHE + cv_bridge</span>
      </div>
      <div class="meta-item">
        <span class="meta-label">Kinematics & Robot Type</span>
        <span class="meta-val">Two-Wheel Differential Drive + Caster (URDF)</span>
      </div>
      <div class="meta-item">
        <span class="meta-label">Deployment Architecture</span>
        <span class="meta-val">Docker Container (Ubuntu 22.04 LTS, CPU Opt)</span>
      </div>
      <div class="meta-item">
        <span class="meta-label">Autonomous Controller</span>
        <span class="meta-val">4-State FSM + Proportional Visual Servoing</span>
      </div>
    </div>

    <div class="cover-highlights">
      <div class="highlight-card">
        <h4>🔬 Camouflage Vision</h4>
        <p>Micro-texture enhancement in CIELAB space + Ungulate taxonomic priors for concealed wildlife detection.</p>
      </div>
      <div class="highlight-card">
        <h4>🌲 Domain Randomization</h4>
        <p>Procedural forest generation with Poisson-disc spacing, lighting variance, and concealment tiers.</p>
      </div>
      <div class="highlight-card">
        <h4>🎯 Closed-Loop Autonomy</h4>
        <p>360° sweeping, FOV S-curve weaving, monocular depth estimation, and 3.0m standoff target lock.</p>
      </div>
    </div>
  </div>

  <div class="cover-footer">
    <span>Department of Computer Science & Robotics Engineering</span>
    <span>Embedded Systems & Autonomous Perception Capstone</span>
    <span>November 2026</span>
  </div>
</div>
"""

def get_toc():
    return """
<!-- ==================== TABLE OF CONTENTS ==================== -->
<div class="page-break">
  <h1 class="section-title"><span class="section-num">00</span> Table of Contents & Study Map</h1>
  <p>This handbook is meticulously organized into ten foundational chapters and an exhaustive viva defense guide. Use this map to quickly navigate through theoretical foundations, mathematical derivations, source code implementations, and examination Q&A.</p>

  <table class="custom-table">
    <thead>
      <tr>
        <th style="width: 10%;">Chapter</th>
        <th style="width: 40%;">Title & Core Focus</th>
        <th style="width: 35%;">Key Technical Concepts Covered</th>
        <th style="width: 15%;">Primary Files</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Ch. 01</strong></td>
        <td><strong>Executive Summary & Foundations</strong></td>
        <td>Problem statement, COD vs SOD, biological camouflage principles, system matrix</td>
        <td><span class="table-badge badge-gray">README.md</span></td>
      </tr>
      <tr>
        <td><strong>Ch. 02</strong></td>
        <td><strong>End-to-End System Architecture</strong></td>
        <td>ROS 2 graph, topic topology, message pipelines, latency budgets, RTF constraints</td>
        <td><span class="table-badge badge-blue">simulation.launch</span></td>
      </tr>
      <tr>
        <td><strong>Ch. 03</strong></td>
        <td><strong>Robot Kinematics & URDF Modeling</strong></td>
        <td>Differential drive kinematics, ICR, Jacobian, URDF links/joints, ODE friction</td>
        <td><span class="table-badge badge-green">animal_robot.urdf</span></td>
      </tr>
      <tr>
        <td><strong>Ch. 04</strong></td>
        <td><strong>Optical Sensors & Monocular Depth</strong></td>
        <td>Pinhole camera model, FOV derivation, focal length, similar triangles depth math</td>
        <td><span class="table-badge badge-green">animal_robot.urdf</span></td>
      </tr>
      <tr>
        <td><strong>Ch. 05</strong></td>
        <td><strong>Gazebo Simulation & Procedural Worlds</strong></td>
        <td>SDF 1.6, procedural generator, Poisson disc, concealment tiers, CPU optimizations</td>
        <td><span class="table-badge badge-purple">generate_random_world</span></td>
      </tr>
      <tr>
        <td><strong>Ch. 06</strong></td>
        <td><strong>Computer Vision Perception Engine</strong></td>
        <td>CIELAB CLAHE, YOLOv8 architecture, taxonomic prior mapping, EMA smoothing, HUD</td>
        <td><span class="table-badge badge-amber">ros_recognition_yolo</span></td>
      </tr>
      <tr>
        <td><strong>Ch. 07</strong></td>
        <td><strong>Autonomous Navigation & Visual Servoing</strong></td>
        <td>4-state FSM, proportional yaw steering, S-curve creep, telemetry JSON stream</td>
        <td><span class="table-badge badge-blue">autonomous_patrol</span></td>
      </tr>
      <tr>
        <td><strong>Ch. 08</strong></td>
        <td><strong>AI Training & Transfer Learning</strong></td>
        <td>Synthetic frame capture, dataset structure, hyperparameter tuning, loss functions</td>
        <td><span class="table-badge badge-amber">train_camouflage_yolo</span></td>
      </tr>
      <tr>
        <td><strong>Ch. 09</strong></td>
        <td><strong>Dockerization & Deployment</strong></td>
        <td>Multi-layer Dockerfile, X11 socket forwarding, software GL, colcon build</td>
        <td><span class="table-badge badge-purple">Dockerfile, start_docker</span></td>
      </tr>
      <tr>
        <td><strong>Ch. 10</strong></td>
        <td><strong>Comprehensive Viva Defense Guide</strong></td>
        <td>25 deep technical viva questions with core concepts and model high-scoring answers</td>
        <td><span class="table-badge badge-green">Full System Scope</span></td>
      </tr>
    </tbody>
  </table>

  <div class="callout callout-info">
    <div class="callout-title">💡 How to Study This Document for Defense & Viva</div>
    If preparing for an examination or presentation, focus on <strong>Chapter 3</strong> (Kinematics equations), <strong>Chapter 4</strong> (Monocular depth derivation), <strong>Chapter 6</strong> (CLAHE math and taxonomic prior mapping), and <strong>Chapter 10</strong> (Viva questions). Every equation, parameter, and algorithm used in the repository is explained from first principles.
  </div>
</div>
"""

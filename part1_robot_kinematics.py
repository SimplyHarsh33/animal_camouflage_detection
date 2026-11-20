# -*- coding: utf-8 -*-
"""Part 1: Robot Kinematics, Mechanical Modeling & Optical Sensors"""

def get_part1():
    return """
<!-- ==================== PART 1 ==================== -->
<div class="page-break">
  <div class="part-header-card border-green">
    <div class="part-badge badge-green">MODULE 1 OF 4</div>
    <h1 class="part-title">Part 1: Robot Kinematics, Mechanical Modeling & Optical Sensor Simulation</h1>
    <p class="part-subtitle">
      Comprehensive technical handbook covering robot physical design, URDF XML structure, differential drive forward and inverse kinematics, turning radius physics, wheel contact dynamics, virtual pinhole camera simulation, and coordinate transform trees (TF2).
    </p>
  </div>

  <h2 class="sub-title">1.1 Subsystem Role Distribution & Core Ownership</h2>
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
        <td><strong>Mechanical Modeling Lead</strong></td>
        <td><strong>URDF Architecture & Inertia Tensors</strong></td>
        <td>
          &bull; Authoring <code class="inline-code">animal_robot.urdf</code> links and joints.<br>
          &bull; Mass distribution (3.0kg chassis, 0.3kg wheels, 0.2kg caster).<br>
          &bull; Principal moment of inertia matrix calculations.<br>
          &bull; Low center of gravity placement to prevent tilting.
        </td>
        <td>URDF vs SDF, link/joint trees, inertia tensors, center of mass stability.</td>
      </tr>
      <tr>
        <td><strong>Kinematics & Actuation Lead</strong></td>
        <td><strong>Differential Drive Motion Mathematics</strong></td>
        <td>
          &bull; Formulating forward and inverse differential drive equations.<br>
          &bull; Calculating Instantaneous Center of Curvature (ICC/ICR).<br>
          &bull; Formulating the non-holonomic no-slip constraint.<br>
          &bull; Configuring <code class="inline-code">libgazebo_ros_diff_drive.so</code> (torque, acceleration, track).
        </td>
        <td>Forward/inverse kinematics formulas, wheel speed mapping, non-holonomic limits.</td>
      </tr>
      <tr>
        <td><strong>Sensors & Transforms Lead</strong></td>
        <td><strong>Optical Sensor Simulation & TF2 Trees</strong></td>
        <td>
          &bull; Integrating <code class="inline-code">libgazebo_ros_camera.so</code> virtual pinhole plugin.<br>
          &bull; Establishing 80° HFOV, 640x480 resolution, and 15 Hz update rate.<br>
          &bull; Configuring the TF2 transform tree (<code class="inline-code">odom ➔ chassis ➔ camera_frame</code>).<br>
          &bull; Authoring <code class="inline-code">spawn_robot.launch.py</code> and <code class="inline-code">robot_state_publisher</code>.
        </td>
        <td>Pinhole camera model, focal length, coordinate frames, TF2 tree.</td>
      </tr>
    </tbody>
  </table>

  <h2 class="sub-title">1.2 Robot Physical Specifications & Dimensional Engineering</h2>
  <p>
    The mobile robot (<code class="inline-code">animal_robot</code>) is engineered as a compact, highly agile differential-drive platform designed to maneuver through dense woodland vegetation without snagging on tree trunks or boulders.
  </p>

  <div class="two-col avoid-break">
    <div class="card-box">
      <h4>Chassis Structure & Inertia</h4>
      <ul>
        <li><strong>Chassis Dimensions:</strong> Length 0.22 meters, Width 0.12 meters, Height 0.06 meters.</li>
        <li><strong>Chassis Net Mass:</strong> 3.0 kilograms.</li>
        <li><strong>Center of Mass (COM):</strong> Positioned at [0.0, 0.0, -0.02] meters. Placing the mass center below the wheel axle level provides strong passive pitch and roll self-righting stability during sharp acceleration.</li>
        <li><strong>Inertia Tensor:</strong>
          <br><code class="inline-code">Ixx = 0.008, Iyy = 0.015, Izz = 0.020 kg&middot;m²</code>.
        </li>
      </ul>
    </div>
    <div class="card-box">
      <h4>Wheel Actuators & Caster Sphere</h4>
      <ul>
        <li><strong>Drive Wheels:</strong> 2 actuated wheels, radius r = 0.035 meters (diameter 0.07 meters), length 0.02 meters, mass 0.3 kilograms each.</li>
        <li><strong>Track Separation (L):</strong> 0.12 meters between left and right wheel midpoints.</li>
        <li><strong>Wheel Friction:</strong> High traction &mu;1 = 1.5, &mu;2 = 1.5, stiffness Kp = 100000.0, Kd = 10.0.</li>
        <li><strong>Passive Support:</strong> Front caster sphere, radius 0.015 meters, mass 0.2 kilograms, near-zero friction &mu; = 0.001 allowing frictionless omnidirectional gliding.</li>
      </ul>
    </div>
  </div>

  <h2 class="sub-title">1.3 Differential Drive Kinematics (Human-Readable Formulations)</h2>
  <p>
    The robot operates on a 2-dimensional flat ground plane. At any moment, the robot's physical state is defined by its <strong>position (X, Y)</strong> and its <strong>heading angle (&theta;)</strong> pointing toward where it is facing.
  </p>

  <!-- Formula 1: Forward Speed -->
  <div class="formula-box">
    <div class="formula-title">1. Forward Speed Formula (v)</div>
    <div class="formula-main">
      Forward Velocity (v) = (Right Wheel Speed + Left Wheel Speed) &divide; 2
    </div>
    <div class="formula-details">
      In terms of wheel spin: <strong>v = 0.5 &times; Wheel Radius &times; (&omega;<sub>Right</sub> + &omega;<sub>Left</sub>)</strong>
      <br>Using our robot's wheel radius (r = 0.035 meters): <strong>v = 0.0175 &times; (&omega;<sub>Right</sub> + &omega;<sub>Left</sub>) m/s</strong>
    </div>
    <div class="formula-explanation">
      <strong>What this means in plain words:</strong> The robot's straight-ahead velocity is simply the average ground speed of the two drive wheels. If both wheels spin forward at the exact same speed, the robot travels straight forward.
    </div>
  </div>

  <!-- Formula 2: Turning Speed -->
  <div class="formula-box">
    <div class="formula-title">2. Turning Yaw Speed Formula (&omega;)</div>
    <div class="formula-main">
      Turning Rate (&omega;) = (Right Wheel Speed &minus; Left Wheel Speed) &divide; Wheel Track Distance (L)
    </div>
    <div class="formula-details">
      In terms of wheel spin: <strong>&omega; = (Wheel Radius / Track Distance) &times; (&omega;<sub>Right</sub> &minus; &omega;<sub>Left</sub>)</strong>
      <br>Using our robot dimensions (r = 0.035 m, Track L = 0.12 m): <strong>&omega; = 0.2917 &times; (&omega;<sub>Right</sub> &minus; &omega;<sub>Left</sub>) rad/s</strong>
    </div>
    <div class="formula-explanation">
      <strong>What this means in plain words:</strong> Turning is created by the speed difference between the two wheels. If the right wheel spins faster than the left wheel, the robot curves to the left. If the wheels spin in opposite directions at equal speed, the robot spins in place around its own center!
    </div>
  </div>

  <!-- Formula 3: Inverse Kinematics -->
  <div class="formula-box">
    <div class="formula-title">3. Inverse Kinematics: How the Computer Commands the Wheel Motors</div>
    <div class="formula-main">
      Right Wheel Motor Speed (&omega;<sub>Right</sub>) = (Desired Forward Speed + 0.5 &times; Track &times; Desired Turn Speed) &divide; Wheel Radius
      <br>Left Wheel Motor Speed (&omega;<sub>Left</sub>) = (Desired Forward Speed &minus; 0.5 &times; Track &times; Desired Turn Speed) &divide; Wheel Radius
    </div>
    <div class="formula-details">
      Plugging in our robot values (r = 0.035 meters, Track L = 0.12 meters):
      <br>&bull; <strong>Right Motor Speed (&omega;<sub>Right</sub>) = (v + 0.06 &times; &omega;) &divide; 0.035 rad/s</strong>
      <br>&bull; <strong>Left Motor Speed (&omega;<sub>Left</sub>) = (v &minus; 0.06 &times; &omega;) &divide; 0.035 rad/s</strong>
    </div>
    <div class="formula-explanation">
      <strong>What this means in plain words:</strong> When the autonomous navigation system decides that the robot should move forward at 0.22 m/s while gently turning at 0.14 rad/s, these two formulas calculate the exact motor speeds to send to each wheel. This runs automatically at 50 Hz inside the Gazebo differential drive plugin.
    </div>
  </div>

  <!-- Formula 4: Turning Radius & ICC -->
  <div class="formula-box">
    <div class="formula-title">4. Turning Radius (R) & Instantaneous Center of Curvature</div>
    <div class="formula-main">
      Turning Radius (R) = Forward Speed (v) &divide; Turning Speed (&omega;)
    </div>
    <div class="formula-details">
      In terms of wheel spin: <strong>R = 0.06 &times; [(&omega;<sub>Right</sub> + &omega;<sub>Left</sub>) / (&omega;<sub>Right</sub> &minus; &omega;<sub>Left</sub>)] meters</strong>
    </div>
    <div class="formula-explanation">
      <strong>What this means in plain words:</strong>
      <br>&bull; <strong>Straight line motion:</strong> Both wheels spin at the same speed &rarr; Turning Radius is infinite (no turn).
      <br>&bull; <strong>In-place zero-radius spin:</strong> Wheels spin in opposite directions (&omega;<sub>Right</sub> = &minus;&omega;<sub>Left</sub>) &rarr; Turning Radius = 0 (the robot spins on its own center point like a tank, which is used in the 360° environmental scan).
    </div>
  </div>

  <!-- Formula 5: No-Slip Driving Constraint -->
  <div class="formula-box">
    <div class="formula-title">5. Driving Constraint: No Sideways Slipping (Non-Holonomic Motion)</div>
    <div class="formula-main">
      Instantaneous Lateral Sliding Speed = 0.0 m/s
    </div>
    <div class="formula-explanation">
      <strong>What this means in plain words:</strong> Like a regular passenger car, a differential-drive robot cannot slide sideways directly. The wheels grip the ground and only allow motion forward, backward, or in an arc. To reach a spot to its side, the robot must first turn to face that direction and then drive forward.
    </div>
  </div>

  <h2 class="sub-title">1.4 Comprehensive URDF XML Code Walkthrough</h2>
  <p>
    The robot kinematic tree is defined in <code class="inline-code">packages/animal_description/urdf/animal_robot.urdf</code>. Let us analyze every essential XML block:
  </p>

  <div class="code-header"><span>Chassis Link & Visual / Collision Definitions</span><span>animal_robot.urdf</span></div>
  <div class="code-block">
&lt;link name="base_link"&gt;&lt;/link&gt;

&lt;link name="chassis"&gt;
  &lt;pose&gt;0 0 0 0 0 0&lt;/pose&gt;
  &lt;inertial&gt;
    &lt;mass value="3.0"/&gt;
    &lt;origin rpy="0 0 0" xyz="0 0 -0.02"/&gt;
    &lt;inertia ixx="0.008" ixy="0" ixz="0" iyy="0.015" iyz="0" izz="0.020"/&gt;
  &lt;/inertial&gt;
  &lt;collision name="collision_chassis"&gt;
    &lt;geometry&gt;
      &lt;box size="0.22 0.12 0.06"/&gt;
    &lt;/geometry&gt;
  &lt;/collision&gt;
  &lt;visual name="visual_chassis"&gt;
    &lt;geometry&gt;
      &lt;box size="0.22 0.12 0.06"/&gt;
    &lt;/geometry&gt;
    &lt;material name="red"/&gt;
  &lt;/visual&gt;
&lt;/link&gt;

&lt;joint name="base_link_joint" type="fixed"&gt;
  &lt;origin rpy="0 0 0" xyz="0 0 0"/&gt;
  &lt;parent link="base_link"/&gt;
  &lt;child link="chassis"/&gt;
&lt;/joint&gt;
  </div>

  <div class="code-header"><span>Continuous Drive Wheel Joints & Actuators</span><span>animal_robot.urdf</span></div>
  <div class="code-block">
&lt;!-- RIGHT DRIVE WHEEL --&gt;
&lt;joint name="joint_right_wheel" type="continuous"&gt;
  &lt;origin rpy="0 0 0" xyz="-0.05 0.06 -0.025"/&gt;
  &lt;child link="right_wheel"/&gt;
  &lt;parent link="chassis"/&gt;
  &lt;axis rpy="0 0 0" xyz="0 1 0"/&gt;
  &lt;limit effort="20.0" velocity="20.0"/&gt;
  &lt;dynamics damping="0.1" friction="0.05"/&gt;
&lt;/joint&gt;

&lt;!-- LEFT DRIVE WHEEL --&gt;
&lt;joint name="joint_left_wheel" type="continuous"&gt;
  &lt;origin rpy="0 0 0" xyz="-0.05 -0.06 -0.025"/&gt;
  &lt;child link="left_wheel"/&gt;
  &lt;parent link="chassis"/&gt;
  &lt;axis rpy="0 0 0" xyz="0 1 0"/&gt;
  &lt;limit effort="20.0" velocity="20.0"/&gt;
  &lt;dynamics damping="0.1" friction="0.05"/&gt;
&lt;/joint&gt;
  </div>

  <div class="code-header"><span>Front Passive Caster Sphere (Frictionless Support)</span><span>animal_robot.urdf</span></div>
  <div class="code-block">
&lt;link name="front_pitch_link"&gt;
  &lt;inertial&gt;
    &lt;mass value="0.2"/&gt;
    &lt;origin rpy="0 0 0" xyz="0 0 0"/&gt;
    &lt;inertia ixx="0.00005" ixy="0" ixz="0" iyy="0.00005" iyz="0" izz="0.00005"/&gt;
  &lt;/inertial&gt;
  &lt;collision name="front_collision"&gt;
    &lt;geometry&gt;&lt;sphere radius="0.015"/&gt;&lt;/geometry&gt;
  &lt;/collision&gt;
  &lt;visual name="front_visual"&gt;
    &lt;geometry&gt;&lt;sphere radius="0.015"/&gt;&lt;/geometry&gt;
    &lt;material name="green"/&gt;
  &lt;/visual&gt;
&lt;/link&gt;

&lt;gazebo reference="front_pitch_link"&gt;
  &lt;kp&gt;50000.0&lt;/kp&gt;
  &lt;kd&gt;20.0&lt;/kd&gt;
  &lt;mu1&gt;0.001&lt;/mu1&gt; &lt;!-- Ultra-low friction for smooth turning --&gt;
  &lt;mu2&gt;0.001&lt;/mu2&gt;
  &lt;material&gt;Gazebo/Green&lt;/material&gt;
&lt;/gazebo&gt;
  </div>

  <h2 class="sub-title">1.5 Gazebo Differential Drive Plugin Integration</h2>
  <p>
    The ODE physics engine in Gazebo does not accept raw velocity commands directly on joints without a controller. The <code class="inline-code">libgazebo_ros_diff_drive.so</code> plugin acts as the digital closed-loop servo amplifier:
  </p>
  <ul>
    <li>It binds to <code class="inline-code">joint_right_wheel</code> and <code class="inline-code">joint_left_wheel</code>.</li>
    <li>It subscribes to <code class="inline-code">/animal_robot/cmd_vel</code> (<code class="inline-code">geometry_msgs/msg/Twist</code>).</li>
    <li>It applies torque (up to 20.0 N&middot;m) with maximum rotational acceleration limit 5.0 rad/s² to reach target speeds smoothly.</li>
    <li>It integrates wheel revolutions over time to publish dead-reckoning odometry on <code class="inline-code">/animal_robot/odom</code> and broadcasts the spatial transform from <code class="inline-code">odom</code> to <code class="inline-code">chassis</code>.</li>
  </ul>

  <h2 class="sub-title">1.6 Optical Sensor Pinhole Camera Physics & TF2 Tree</h2>
  <p>
    The camera is rigidly mounted at coordinates [x=0.09, y=0.0, z=0.08] meters relative to the chassis origin, elevated above the wheel plane to maintain an unobstructed view across the ground plane:
  </p>
  <div class="code-block">
&lt;gazebo reference="rgb_cam_camera_link_frame"&gt;
  &lt;sensor type="camera" name="rgb_cam"&gt;
    &lt;always_on&gt;1&lt;/always_on&gt;
    &lt;update_rate&gt;15.0&lt;/update_rate&gt;
    &lt;camera name="rgb_cam"&gt;
      &lt;horizontal_fov&gt;1.3962634&lt;/horizontal_fov&gt; &lt;!-- 80 degrees --&gt;
      &lt;image&gt;
        &lt;width&gt;640&lt;/width&gt;
        &lt;height&gt;480&lt;/height&gt;
        &lt;format&gt;R8G8B8&lt;/format&gt;
      &lt;/image&gt;
      &lt;clip&gt;&lt;near&gt;0.05&lt;/near&gt;&lt;far&gt;25.0&lt;/far&gt;&lt;/clip&gt;
    &lt;/camera&gt;
    &lt;plugin name="camera_controller" filename="libgazebo_ros_camera.so"&gt;
      &lt;ros&gt;
        &lt;remapping&gt;image_raw:=/rgb_cam/image_raw&lt;/remapping&gt;
        &lt;remapping&gt;camera_info:=/rgb_cam/camera_info&lt;/remapping&gt;
      &lt;/ros&gt;
      &lt;frame_name&gt;rgb_cam_camera_link_frame&lt;/frame_name&gt;
    &lt;/plugin&gt;
  &lt;/sensor&gt;
&lt;/gazebo&gt;
  </div>

  <p>
    The <strong>TF2 Transform Hierarchy</strong> established by <code class="inline-code">robot_state_publisher</code> and the differential drive plugin is:
    <br><code class="inline-code">odom</code> (Global Odometry) &rarr; <code class="inline-code">chassis</code> (Robot Base Link) &rarr; <code class="inline-code">rgb_cam_camera_link</code> (Physical Mount) &rarr; <code class="inline-code">rgb_cam_camera_link_frame</code> (Optical Sensor Center).
  </p>

  <h2 class="sub-title">1.7 Part 1 Dedicated Viva & Oral Exam Defense Guide</h2>

  <div class="viva-card">
    <div class="viva-q"><span class="viva-badge">Q1.1</span> How does the robot turn in place with zero turning radius, and how do the wheel speeds relate?</div>
    <div class="viva-concept">Topic Focus: Differential Drive Kinematics</div>
    <div class="viva-ans">
      <strong>Model Answer:</strong>
      To turn in place with a zero turning radius, the robot commands both drive wheels to spin at the exact same rotational speed but in opposite directions (Right Wheel = &minus;Left Wheel). 
      <br><br>
      Since the forward speed is the sum of both wheel speeds divided by two, the net forward speed becomes zero (v = 0 m/s). Meanwhile, the turning speed is proportional to the difference between the wheels, producing maximum rotation around the center point between the wheels. This allows our robot to execute 360-degree environmental scans in dense brush without needing any space to move forward or backward.
    </div>
  </div>

  <div class="viva-card">
    <div class="viva-q"><span class="viva-badge">Q1.2</span> Why is the chassis center of mass (COM) set at [0, 0, -0.02] meters instead of [0, 0, 0]?</div>
    <div class="viva-concept">Topic Focus: Mechanical Stability & Dynamics</div>
    <div class="viva-ans">
      <strong>Model Answer:</strong>
      Setting the center of mass 2 centimeters below the wheel axle creates a natural pendulum-like self-stabilizing effect. If the center of mass were positioned high above the wheels, rapid acceleration or sudden braking would cause the chassis to pitch and tilt aggressively forward or backward. A low center of mass keeps the camera horizontal and stable, preventing distorted camera frames.
    </div>
  </div>

  <div class="viva-card">
    <div class="viva-q"><span class="viva-badge">Q1.3</span> What is the role of <code class="inline-code">robot_state_publisher</code> and how does it interface with URDF?</div>
    <div class="viva-concept">Topic Focus: Coordinate Systems & TF2 Tree</div>
    <div class="viva-ans">
      <strong>Model Answer:</strong>
      <code class="inline-code">robot_state_publisher</code> reads the robot description XML (<code class="inline-code">animal_robot.urdf</code>) and listens to the joint positions published on <code class="inline-code">/joint_states</code>. It calculates the 3D position and orientation of every single component of the robot and broadcasts them dynamically as coordinate transforms over the <code class="inline-code">/tf</code> topic. This allows the computer vision and navigation nodes to know the exact 3D position of the camera relative to the chassis wheels.
    </div>
  </div>

  <div class="viva-card">
    <div class="viva-q"><span class="viva-badge">Q1.4</span> Why did you use <code class="inline-code">continuous</code> joints for the drive wheels rather than <code class="inline-code">revolute</code> joints?</div>
    <div class="viva-concept">Topic Focus: URDF Joint Modeling</div>
    <div class="viva-ans">
      <strong>Model Answer:</strong>
      In URDF, a <code class="inline-code">revolute</code> joint is a rotational joint that has strict physical angle limits (for example, rotating between -90° and +90°, like a robot elbow). A <code class="inline-code">continuous</code> joint has no angle limits and can spin indefinitely without stopping. Because drive wheels must spin continuously to propel the robot forward over long distances, they must be declared as <code class="inline-code">type="continuous"</code>.
    </div>
  </div>

  <div class="viva-card">
    <div class="viva-q"><span class="viva-badge">Q1.5</span> Explain how wheel friction parameters &mu;1 and &mu;2 impact simulation realism.</div>
    <div class="viva-concept">Topic Focus: Physics & Contact Friction</div>
    <div class="viva-ans">
      <strong>Model Answer:</strong>
      In the ODE physics engine, &mu;1 represents friction along the primary direction of rolling, and &mu;2 represents friction along the perpendicular sideways direction. For the drive wheels, setting &mu;1 = &mu;2 = 1.5 models high-traction rubber on soil, preventing wheel slippage. For the front caster, setting &mu;1 = &mu;2 = 0.001 creates an omnidirectional, nearly frictionless glide pad that eliminates lateral scrubbing resistance during sharp turns.
    </div>
  </div>
</div>
"""

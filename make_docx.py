#!/usr/bin/env python3
"""Generates PROJECT_GUIDE.docx from the project README content."""

from docx import Document
from docx.shared import Pt, RGBColor, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import copy

doc = Document()

# ── Page margins ──────────────────────────────────────────────────────────────
for section in doc.sections:
    section.top_margin    = Cm(2.0)
    section.bottom_margin = Cm(2.0)
    section.left_margin   = Cm(2.5)
    section.right_margin  = Cm(2.5)

# ── Helper: set paragraph background shading ─────────────────────────────────
def shade_paragraph(para, fill_hex):
    pPr = para._p.get_or_add_pPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill_hex)
    pPr.append(shd)

# ── Helper: add a coloured heading ───────────────────────────────────────────
def add_heading(text, level=1, color=None):
    p = doc.add_heading(text, level=level)
    if color:
        for run in p.runs:
            run.font.color.rgb = RGBColor(*color)
    return p

# ── Helper: add body paragraph ───────────────────────────────────────────────
def add_para(text, bold=False, italic=False, size=11, indent=False):
    p = doc.add_paragraph()
    if indent:
        p.paragraph_format.left_indent = Inches(0.3)
    run = p.add_run(text)
    run.bold   = bold
    run.italic = italic
    run.font.size = Pt(size)
    return p

# ── Helper: add a styled code block ──────────────────────────────────────────
def add_code(lines):
    for line in lines:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.4)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.space_before = Pt(0)
        shade_paragraph(p, 'F0F0F0')
        run = p.add_run(line)
        run.font.name = 'Courier New'
        run.font.size = Pt(9)
        run.font.color.rgb = RGBColor(0x1A, 0x1A, 0x2E)

# ── Helper: add a table ───────────────────────────────────────────────────────
def add_table(headers, rows, col_widths=None):
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = 'Table Grid'
    # Header row
    hdr = table.rows[0]
    for i, h in enumerate(headers):
        cell = hdr.cells[i]
        cell.text = h
        for run in cell.paragraphs[0].runs:
            run.bold = True
            run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        tc = cell._tc
        tcPr = tc.get_or_add_tcPr()
        shd = OxmlElement('w:shd')
        shd.set(qn('w:val'), 'clear')
        shd.set(qn('w:color'), 'auto')
        shd.set(qn('w:fill'), '1F4E79')
        tcPr.append(shd)
    # Data rows
    for r_idx, row_data in enumerate(rows):
        row = table.rows[r_idx + 1]
        fill = 'DEEAF1' if r_idx % 2 == 0 else 'FFFFFF'
        for c_idx, val in enumerate(row_data):
            cell = row.cells[c_idx]
            cell.text = val
            tc = cell._tc
            tcPr = tc.get_or_add_tcPr()
            shd = OxmlElement('w:shd')
            shd.set(qn('w:val'), 'clear')
            shd.set(qn('w:color'), 'auto')
            shd.set(qn('w:fill'), fill)
            tcPr.append(shd)
    doc.add_paragraph()

# ══════════════════════════════════════════════════════════════════════════════
#  TITLE
# ══════════════════════════════════════════════════════════════════════════════
title = doc.add_heading('Autonomous Camouflage Animal Detection', 0)
title.alignment = WD_ALIGN_PARAGRAPH.CENTER
for run in title.runs:
    run.font.color.rgb = RGBColor(0x1F, 0x4E, 0x79)

sub = doc.add_paragraph('ROS 2 Humble  •  Gazebo Classic  •  YOLOv8  •  Flask Dashboard')
sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
for run in sub.runs:
    run.font.size = Pt(12)
    run.italic = True
    run.font.color.rgb = RGBColor(0x40, 0x40, 0x80)

doc.add_paragraph()

# ══════════════════════════════════════════════════════════════════════════════
#  1. WHAT IS THIS PROJECT
# ══════════════════════════════════════════════════════════════════════════════
add_heading('1. What Is This Project?', level=1, color=(0x1F, 0x4E, 0x79))
add_para(
    'This project simulates an autonomous robot that patrols a virtual forest and detects '
    'camouflaged deer using an AI camera. It runs entirely inside a Docker container using '
    'ROS 2 and Gazebo, and provides a live web dashboard for monitoring and control.'
)
add_para(
    'Goal: Detect animals that are hard to see (camouflaged) using a combination of image '
    'enhancement (CLAHE) and deep learning (YOLOv8).',
    bold=True
)

# ══════════════════════════════════════════════════════════════════════════════
#  2. TECH STACK
# ══════════════════════════════════════════════════════════════════════════════
add_heading('2. Tech Stack', level=1, color=(0x1F, 0x4E, 0x79))
add_table(
    ['Component', 'Tool Used', 'Purpose'],
    [
        ['Robot Operating System', 'ROS 2 Humble',          'Node communication via topics'],
        ['Physics Simulator',      'Gazebo Classic',         'Simulates robot, forest, camera'],
        ['AI Detection',           'YOLOv8n (Ultralytics)',  'Detects animals in camera frames'],
        ['Web Dashboard',          'Flask + HTML/JS',        'Browser-based control & live video'],
        ['Container',              'Docker',                 'Isolated, reproducible environment'],
        ['Image Processing',       'OpenCV + cv_bridge',     'Converts ROS images to OpenCV frames'],
    ]
)

# ══════════════════════════════════════════════════════════════════════════════
#  3. OVERALL SYSTEM WORKFLOW
# ══════════════════════════════════════════════════════════════════════════════
add_heading('3. Overall System Workflow', level=1, color=(0x1F, 0x4E, 0x79))
add_code([
    'GAZEBO SIMULATION',
    '  Forest World + Robot + Camera Sensor Plugin',
    '  Publishes raw camera frames at 15 Hz',
    '  ROS Topic: /rgb_cam/image_raw',
    '       |',
    '       v',
    'YOLO RECOGNITION NODE  (ros_recognition_yolo.py)',
    '  1. cv_bridge converts ROS Image --> OpenCV frame',
    '  2. CLAHE enhances camouflage contrast',
    '  3. YOLOv8 detects animals (async worker thread)',
    '  4. Publishes annotated image + JSON telemetry',
    '       |                           |',
    '  /animal_detection/        /animal_detection/',
    '   annotated_image           detection_status',
    '       |                           |',
    '       +----------+----------------+',
    '                  |',
    '                  v',
    'FLASK DASHBOARD (app.py)  -->  Browser: localhost:5000',
    '  Streams MJPEG video | Telemetry JSON | Control API',
    '                  |',
    '       +----------+----------+',
    '       |                     |',
    '  Manual WASD           Autonomous Patrol',
    '  D-pad control         autonomous_patrol.py',
    '       |                     |',
    '       +----------+----------+',
    '                  |',
    '   ROS Topic: /animal_robot/cmd_vel',
    '                  |',
    '           Robot moves in Gazebo',
])
doc.add_paragraph()

# ══════════════════════════════════════════════════════════════════════════════
#  4. HOW CAMERA FEED WORKS
# ══════════════════════════════════════════════════════════════════════════════
add_heading('4. How the Robot Takes Raw Camera Feed', level=1, color=(0x1F, 0x4E, 0x79))

p = doc.add_paragraph()
run = p.add_run('Viva Question: "How does the robot capture and process camera images?"')
run.bold = True
run.italic = True
run.font.color.rgb = RGBColor(0xC0, 0x00, 0x00)

steps = [
    ('Step 1 — Camera defined in robot model (SDF file)',
     'The robot has a <sensor type="camera"> tag in its model file. '
     'A Gazebo plugin called libgazebo_ros_camera.so is attached to it.'),
    ('Step 2 — Gazebo renders and publishes',
     'Gazebo simulates the camera view (640x480 pixels, 15 fps) and publishes it as a '
     'ROS 2 message of type sensor_msgs/Image on the topic: /rgb_cam/image_raw'),
    ('Step 3 — Recognition node subscribes',
     'ros_recognition_yolo.py creates a ROS 2 subscription to /rgb_cam/image_raw. '
     'Every time a new frame arrives, image_callback() is triggered.'),
    ('Step 4 — cv_bridge converts the message',
     'ROS uses its own Image message format. OpenCV and YOLO need a NumPy array. '
     'cv_bridge handles this:  ROS sensor_msgs/Image  ->  cv_bridge  ->  NumPy BGR array'),
    ('Step 5 — Frame goes to async YOLO worker',
     'Instead of running YOLO inside the callback (which would block ROS), the frame is '
     'dropped into a shared variable. A background worker thread picks it up and runs '
     'inference — this keeps the camera feed smooth and non-blocking.'),
    ('Step 6 — Annotated image published back',
     'After detection, bounding boxes are drawn and published to '
     '/animal_detection/annotated_image. The dashboard streams this as MJPEG to the browser.'),
]
for title_text, body_text in steps:
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Inches(0.3)
    r1 = p.add_run(title_text + '\n')
    r1.bold = True
    r1.font.size = Pt(11)
    r2 = p.add_run(body_text)
    r2.font.size = Pt(10)

doc.add_paragraph()
add_para('Summary of camera pipeline:', bold=True)
add_code(['Gazebo camera plugin  ->  /rgb_cam/image_raw (ROS topic)  ->  cv_bridge',
          '  ->  NumPy frame  ->  CLAHE  ->  YOLO inference (async thread)',
          '  ->  Annotated frame  ->  /animal_detection/annotated_image  ->  MJPEG  ->  Browser'])
doc.add_paragraph()

# ══════════════════════════════════════════════════════════════════════════════
#  5. ROS 2 CONCEPTS
# ══════════════════════════════════════════════════════════════════════════════
add_heading('5. ROS 2 Key Concepts', level=1, color=(0x1F, 0x4E, 0x79))
add_table(
    ['Term', 'Definition'],
    [
        ['Node',       'An individual program that does one job (e.g. camera processing, motor control)'],
        ['Topic',      'A named channel; publishers send to it, subscribers receive from it'],
        ['Publisher',  'A node that sends data on a topic'],
        ['Subscriber', 'A node that receives data from a topic'],
        ['Message',    'Typed data packet sent over a topic (e.g. Image, Twist, String)'],
        ['rclpy',      'Python library for writing ROS 2 nodes'],
        ['cv_bridge',  'Converts between ROS Image messages and OpenCV NumPy arrays'],
    ]
)
add_para(
    'Why ROS 2? It decouples components. The camera node does not need to know about the '
    'dashboard — it just publishes. The dashboard subscribes independently. '
    'This makes the system modular and extensible.'
)
doc.add_paragraph()

# ══════════════════════════════════════════════════════════════════════════════
#  6. GAZEBO
# ══════════════════════════════════════════════════════════════════════════════
add_heading('6. Gazebo Simulation', level=1, color=(0x1F, 0x4E, 0x79))
add_para('Gazebo simulates:', bold=True)
for item in [
    'Robot body, wheels, and differential drive physics',
    'Camera sensor (renders 3D scene → 2D image at 15 Hz)',
    'Forest environment (procedurally generated trees, rocks, deer models)',
]:
    p = doc.add_paragraph(item, style='List Bullet')
    p.paragraph_format.left_indent = Inches(0.4)

add_para('Why simulate?', bold=True)
for item in [
    'No hardware cost — no real robot needed',
    'Safe to test autonomous behaviours — can crash without damage',
    'Repeatable experiments — same seed = same world layout',
    'Easy to change environment for testing generalization',
]:
    p = doc.add_paragraph(item, style='List Bullet')
    p.paragraph_format.left_indent = Inches(0.4)
doc.add_paragraph()

# ══════════════════════════════════════════════════════════════════════════════
#  7. YOLO DETECTION
# ══════════════════════════════════════════════════════════════════════════════
add_heading('7. YOLOv8 Detection Pipeline', level=1, color=(0x1F, 0x4E, 0x79))

add_heading('7.1  CLAHE Preprocessing', level=2)
add_para(
    'Camouflaged animals have similar colors to the background. '
    'CLAHE (Contrast Limited Adaptive Histogram Equalization) boosts local contrast '
    'in small patches of the image — this makes fur texture stand out against bark or grass, '
    'improving detection even when colors blend perfectly.'
)

add_heading('7.2  YOLO (You Only Look Once)', level=2)
for item in [
    'YOLOv8n ("nano") is a lightweight deep learning model optimized for speed',
    'Processes the entire image in one forward pass (hence "only look once")',
    'Outputs: bounding boxes + class labels + confidence scores',
    'Trained on COCO dataset — detects horse, cow, giraffe, bear → mapped to DEER label',
    'Confidence threshold: 0.22 (low, to avoid missing camouflaged targets)',
]:
    p = doc.add_paragraph(item, style='List Bullet')
    p.paragraph_format.left_indent = Inches(0.4)

add_heading('7.3  Distance Estimation (Monocular)', level=2)
add_para('Using the pinhole camera model:')
add_code([
    'distance = (focal_length_px  x  real_height_m) / bounding_box_height_px',
    '',
    'focal_length_px  = 381.5 px   (derived from 80 degree FOV, 640px width)',
    'real_height_m    = 1.35 m     (assumed deer height)',
    'Result: approximate distance in metres, clamped to 0.8m -- 25.0m',
])
doc.add_paragraph()

# ══════════════════════════════════════════════════════════════════════════════
#  8. AUTONOMOUS FSM
# ══════════════════════════════════════════════════════════════════════════════
add_heading('8. Autonomous Patrol — Finite State Machine', level=1, color=(0x1F, 0x4E, 0x79))
add_code([
    'SCAN --(target found)--> APPROACH --(close enough)--> INSPECT',
    '  ^                                                        |',
    '  +---------------------(inspection done)-----------------+',
    '  ^',
    '  +-- BOUNCE (hit wall --> turn around --> back to SCAN)',
])
doc.add_paragraph()
add_table(
    ['State', 'Robot Behaviour'],
    [
        ['SCAN',     'Rotate in place (0.58 rad/s) to sweep for animals'],
        ['APPROACH', 'Drive toward detected animal (0.24 m/s forward)'],
        ['INSPECT',  'Stop, log inspection, wait for next sweep'],
        ['BOUNCE',   'Reverse + turn when wall or obstacle detected'],
    ]
)

# ══════════════════════════════════════════════════════════════════════════════
#  9. DIFFERENTIAL DRIVE
# ══════════════════════════════════════════════════════════════════════════════
add_heading('9. Differential Drive Robot', level=1, color=(0x1F, 0x4E, 0x79))
add_para(
    'The robot has two independently driven wheels. Speed difference between them controls direction:'
)
add_table(
    ['Wheel Speeds', 'Robot Motion'],
    [
        ['Both equal, forward',         'Move straight'],
        ['Left faster than right',       'Turn right'],
        ['Right faster than left',       'Turn left'],
        ['Opposite directions',          'Rotate in place'],
    ]
)
add_para('Commands use geometry_msgs/Twist messages on /animal_robot/cmd_vel:')
add_code([
    'linear.x   ->  forward / backward speed  (m/s)',
    'angular.z  ->  rotation speed            (rad/s)',
])
doc.add_paragraph()

# ══════════════════════════════════════════════════════════════════════════════
#  10. FLASK DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
add_heading('10. Flask Web Dashboard', level=1, color=(0x1F, 0x4E, 0x79))
add_para(
    'The dashboard (dashboard/app.py) is a Flask web server running inside Docker on port 5000. '
    'Two threads run simultaneously:'
)
for item in [
    'Flask thread — serves HTTP requests (video, telemetry API, control commands)',
    'ROS thread — runs rclpy.spin() listening to ROS topics',
]:
    p = doc.add_paragraph(item, style='List Bullet')
    p.paragraph_format.left_indent = Inches(0.4)

add_para('Control flow when user presses W key in browser:', bold=True)
add_code([
    'User presses W in browser',
    '  -> JavaScript sends POST to /api/cmd_vel with {linear_x: 0.4}',
    '  -> Flask receives -> ros_backend.send_cmd(0.4, 0)',
    '  -> Publishes Twist message on /animal_robot/cmd_vel',
    '  -> Gazebo moves the robot forward',
])
doc.add_paragraph()

# ══════════════════════════════════════════════════════════════════════════════
#  11. DOCKER
# ══════════════════════════════════════════════════════════════════════════════
add_heading('11. Docker Architecture & Containerization', level=1, color=(0x1F, 0x4E, 0x79))
add_para(
    'Docker packages the entire environment (ROS 2 Humble, Gazebo Classic, Python libraries, '
    'and model weights) into an isolated container — ensuring reproducible execution across any host.'
)
add_table(
    ['Command Flag', 'Technical Purpose & Why It Is Used'],
    [
        ['--net=host',              'Shares host network stack. Critical for ROS 2 DDS multicast node discovery & direct access to Flask dashboard on localhost:5000.'],
        ['--ipc=host',              'Shares inter-process communication memory space with the host for low-latency ROS 2 middleware transfer.'],
        ['-v "$(pwd)":/workspace',  'Volume bind-mounts project folder. Code changes on host apply instantly inside container without rebuilding the 7.5GB image.'],
        ['-v /tmp/.X11-unix...',    'Mounts host X11 display socket into container to render Gazebo 3D simulation GUI directly onto the host monitor.'],
        ['-e DISPLAY=$DISPLAY',     'Points graphical applications to the host display server.'],
        ['--rm',                    'Auto-removes container on shutdown, preventing stale stopped containers from wasting disk storage.'],
        ['-e LIBGL_ALWAYS_SOFTWARE=1', 'Forces Mesa/LLVMpipe software OpenGL rendering when no dedicated NVIDIA GPU passthrough is configured.'],
    ]
)

# ══════════════════════════════════════════════════════════════════════════════
#  12. FILE STRUCTURE
# ══════════════════════════════════════════════════════════════════════════════
add_heading('12. Project File Structure', level=1, color=(0x1F, 0x4E, 0x79))
add_code([
    'animal_detection/',
    '├── dashboard/',
    '│   ├── app.py                   <- Flask backend (ROS bridge + web server)',
    '│   └── templates/index.html    <- Browser dashboard UI',
    '├── packages/',
    '│   ├── animal_recognition/',
    '│   │   └── scripts/ros_recognition_yolo.py  <- YOLO detection node',
    '│   ├── animal_control/',
    '│   │   └── scripts/autonomous_patrol.py      <- Autonomous FSM patrol node',
    '│   └── animal_gazebo/',
    '│       ├── worlds/animal_world.world          <- Gazebo world file',
    '│       ├── launch/simulation.launch.py        <- ROS 2 launch file',
    '│       └── scripts/generate_random_world.py  <- Procedural world generator',
    '├── models/',
    '│   ├── pine_tree/model.sdf     <- 3D tree model',
    '│   └── oak_tree/model.sdf      <- 3D tree model',
    '├── start_dashboard.py           <- Entry point',
    '└── start_docker.sh              <- Docker launch script',
])
doc.add_paragraph()

# ══════════════════════════════════════════════════════════════════════════════
#  13. VIVA Q&A
# ══════════════════════════════════════════════════════════════════════════════
add_heading('13. Expected Viva Questions & Answers', level=1, color=(0x1F, 0x4E, 0x79))

qas = [
    (
        'Q: What is the difference between ROS 1 and ROS 2?',
        'A: ROS 2 supports real-time systems, has better security (DDS middleware), supports '
        'multiple operating systems, and does not need a central rosmaster node. '
        'ROS 1 required a master node to coordinate all communication between nodes.'
    ),
    (
        'Q: What is a ROS topic?',
        'A: A named communication channel. Publishers send messages to it, subscribers receive '
        'from it. There is no direct connection between publisher and subscriber — fully decoupled.'
    ),
    (
        'Q: What is cv_bridge?',
        'A: A ROS library that converts between sensor_msgs/Image (ROS format) and OpenCV\'s '
        'NumPy array format. Without cv_bridge, you cannot use ROS camera data in OpenCV or YOLO.'
    ),
    (
        'Q: What is CLAHE and why is it important for this project?',
        'A: Contrast Limited Adaptive Histogram Equalization — it enhances local contrast in an '
        'image by processing small patches independently. For camouflaged animals, their fur '
        'texture is subtle and blends with the background. CLAHE makes these textures more '
        'distinct, helping YOLO detect animals that might otherwise be missed.'
    ),
    (
        'Q: What does "You Only Look Once" mean in YOLO?',
        'A: Traditional object detection used a two-step process: first propose candidate regions, '
        'then classify them. YOLO does both in a single neural network forward pass — detecting '
        'all objects in one shot. This makes it fast enough for real-time use.'
    ),
    (
        'Q: How does the robot estimate distance without a depth camera?',
        'A: Using the pinhole camera model. If we know the real height of a deer (~1.35 m) and '
        'measure the height of its bounding box in pixels, we can calculate: '
        'distance = (focal_length × real_height) / pixel_height. '
        'It is approximate but sufficient for the robot to approach the target.'
    ),
    (
        'Q: What is an FSM (Finite State Machine)?',
        'A: A model where the system is always in exactly one state, and transitions between states '
        'are triggered by specific events or conditions. In this project: '
        'SCAN → APPROACH → INSPECT → back to SCAN. The robot always knows what it should be doing.'
    ),
    (
        'Q: Why use Docker for this project?',
        'A: ROS 2 Humble and Gazebo Classic have hundreds of strict system libraries, C++ dependencies, '
        'and specific Ubuntu version requirements that are notorious for "dependency hell" on personal computers. '
        'Docker encapsulates the exact OS environment, ROS 2 binaries, Gazebo physics engine, and Python '
        'libraries in an isolated image. Any team member can launch the exact same simulation environment '
        'in seconds with a single script without modifying their host operating system.'
    ),
    (
        'Q: Why use Docker containers instead of a traditional Virtual Machine (VM)?',
        'A: Virtual Machines emulate entire hardware systems and run a separate, heavy guest OS kernel via a hypervisor, '
        'consuming massive RAM and CPU overhead. Docker containers share the host Linux kernel and run as lightweight, '
        'isolated native processes. This near-native performance is critical for this project because 3D physics rendering '
        '(Gazebo) and deep neural network inference (YOLOv8) require maximum CPU throughput.'
    ),
    (
        'Q: What is the difference between a Docker Image and a Docker Container?',
        'A: An image (e.g. animal_detection_ros2:humble) is a read-only, immutable blueprint containing all code, binaries, '
        'and dependencies. A container is a runnable, ephemeral instance created from that image with a temporary writable layer. '
        'When the container stops (especially with the --rm flag), its writable layer is discarded, but the base image remains untouched.'
    ),
    (
        'Q: What does volume bind-mounting (-v "$(pwd)":/workspace) achieve in this project?',
        'A: It links the project directory on your laptop directly to the /workspace directory inside the container. '
        'Any edits you make to Python scripts, launch files, or models on the host machine reflect inside the container '
        'instantly without needing to rebuild the 7.5GB Docker image. Furthermore, dataset snapshots and logs generated inside '
        'the container are directly saved to your laptop drive.'
    ),
    (
        'Q: Why is --net=host critical when launching the container?',
        'A: By default, Docker places containers on an isolated bridge network with private IP mapping. --net=host attaches '
        'the container directly to your host machine\'s network interface. This serves two vital functions: (1) ROS 2 uses '
        'DDS (Data Distribution Service) with UDP multicast for automatic node discovery, which isolated bridge networks often '
        'block; and (2) it exposes the Flask web dashboard on port 5000 so opening http://localhost:5000 on your host browser '
        'connects directly without needing complex port-forwarding rules.'
    ),
    (
        'Q: Why do you have to run "pip install flask" each time a fresh container is created?',
        'A: Because the container is launched with the --rm flag (which auto-destroys the container on exit), and Flask was not '
        'pre-baked into the static base image (animal_detection_ros2:humble). Any package installed at runtime only lives in the '
        'ephemeral writable layer. To make it permanent, one would simply run "RUN pip3 install flask" inside the Dockerfile and rebuild.'
    ),
    (
        'Q: How does the graphical simulation (Gazebo GUI / OpenCV window) render on the host screen from inside Docker?',
        'A: Through X11 Unix socket forwarding: (1) The host X11 display socket is mounted into the container via -v /tmp/.X11-unix:/tmp/.X11-unix:rw; '
        '(2) The environment variable -e DISPLAY=$DISPLAY tells graphical apps where to send display commands; and (3) The command '
        '"xhost +local:root" grants the container permission to draw windows on the host desktop.'
    ),
    (
        'Q: What is MJPEG streaming?',
        'A: Motion JPEG — a video format where each frame is sent as a separate JPEG image over '
        'HTTP. It is simple and works in any browser without special plugins. The Flask server '
        'sends frames continuously; the browser <img> tag displays them, creating live video.'
    ),
    (
        'Q: What is differential drive and how are turn commands computed?',
        'A: A robot with two independently motorized wheels. The angular.z value in the Twist '
        'message tells the robot how fast to rotate. Internally, Gazebo translates this to: '
        'left_wheel_speed = linear - (angular × width/2), '
        'right_wheel_speed = linear + (angular × width/2).'
    ),
    (
        'Q: What is colcon and symlink-install?',
        'A: colcon is the ROS 2 build tool. --symlink-install means instead of copying Python '
        'scripts to the install folder, it creates symbolic links pointing back to the source '
        'files. So any edit to packages/ takes effect immediately without rebuilding.'
    ),
    (
        'Q: Why did you use bounding boxes instead of image segmentation?',
        'A: Three reasons — speed, hardware, and sufficiency.\n'
        '   Speed: Segmentation (e.g. YOLOv8-seg) computes a pixel-level mask for every '
        'detected object, which is significantly more compute-heavy. On a CPU-only system '
        '(no GPU in the container), this would drop FPS drastically.\n'
        '   Hardware: The Docker container runs with software rendering and CPU-only PyTorch. '
        'Segmentation models are simply too slow for this setup.\n'
        '   Sufficiency: The robot only needs to know where the animal is (centre X, '
        'bounding box height for distance estimation) and whether it is a target. '
        'A bounding box provides all that information. Pixel-perfect outlines are not '
        'needed to approach or inspect the animal.\n'
        '   In short: bounding boxes give everything needed, at real-time speed, '
        'on the available hardware. Segmentation would be the right choice if the task '
        'required counting animals in a dense herd or measuring body posture.'
    ),
]

for q_text, a_text in qas:
    p = doc.add_paragraph()
    r1 = p.add_run(q_text + '\n')
    r1.bold = True
    r1.font.size = Pt(11)
    r1.font.color.rgb = RGBColor(0x1F, 0x4E, 0x79)
    r2 = p.add_run(a_text)
    r2.font.size = Pt(10)
    p.paragraph_format.space_after = Pt(10)

# ══════════════════════════════════════════════════════════════════════════════
#  14. HOW TO RUN
# ══════════════════════════════════════════════════════════════════════════════
add_heading('14. How to Run', level=1, color=(0x1F, 0x4E, 0x79))
add_code([
    '# Step 1 — Start Docker container',
    'cd /home/harsh-yadav/Desktop/animal_detection',
    './start_docker.sh',
    '',
    '# Step 2 — Inside container, start the dashboard',
    'source install/setup.bash',
    'pip install flask -q',
    'python3 start_dashboard.py',
    '',
    '# Step 3 — Open browser on host machine',
    'http://localhost:5000',
])
doc.add_paragraph()
add_para(
    'Note: pip install flask must be re-run every time a new container is created '
    'because the Docker image does not include Flask pre-installed.',
    italic=True
)

# ── Save ──────────────────────────────────────────────────────────────────────
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
out = '/workspace/PROJECT_GUIDE.docx' if os.path.exists('/workspace') else os.path.join(script_dir, 'PROJECT_GUIDE.docx')
doc.save(out)
print(f'Saved: {out}')

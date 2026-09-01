FROM osrf/ros:humble-desktop-full

# Avoid interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Layer 1: System dependencies & ROS 2 packages
RUN apt-get update && apt-get install -y \
    ros-humble-gazebo-ros-pkgs \
    ros-humble-gazebo-msgs \
    ros-humble-cv-bridge \
    ros-humble-joy \
    ros-humble-robot-state-publisher \
    ros-humble-xacro \
    python3-pip \
    python3-opencv \
    && rm -rf /var/lib/apt/lists/*

# Layer 2: PyTorch CPU (lightweight, no GPU needed for simulation)
RUN pip3 install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Layer 3: YOLOv8 (ultralytics) + all required Python dependencies
RUN pip3 install --no-cache-dir \
    "setuptools<80" \
    "numpy<2.0.0" \
    ultralytics \
    opencv-python \
    requests \
    PyYAML \
    matplotlib \
    Pillow \
    scipy \
    tqdm \
    seaborn

# Set working directory inside container
WORKDIR /workspace

# Gazebo model path points to our models/ folder
ENV GAZEBO_MODEL_PATH=/workspace/models:${GAZEBO_MODEL_PATH}

# Software rendering for systems without a dedicated GPU
ENV LIBGL_ALWAYS_SOFTWARE=1
ENV QT_X11_NO_MITSHM=1

# Auto-source ROS 2 and workspace on every terminal
RUN echo "export GAZEBO_MODEL_PATH=/workspace/models:\$GAZEBO_MODEL_PATH" >> ~/.bashrc
RUN echo "export LIBGL_ALWAYS_SOFTWARE=1" >> ~/.bashrc
RUN echo "export QT_X11_NO_MITSHM=1" >> ~/.bashrc
RUN echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
RUN echo "if [ -f /workspace/install/setup.bash ]; then source /workspace/install/setup.bash; fi" >> ~/.bashrc

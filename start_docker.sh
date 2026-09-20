#!/bin/bash
set -e

# Allow GUI access from Docker container to host display
xhost +local:root || true
xhost +local:docker || true

# Auto-detect if sudo is needed for docker
if ! docker info > /dev/null 2>&1; then
    DOCKER_CMD="sudo docker"
else
    DOCKER_CMD="docker"
fi

echo "======================================================="
echo "  Animal Camouflage Detection — ROS 2 + Gazebo"
echo "  Starting Docker container with GUI support..."
echo "======================================================="

$DOCKER_CMD run -it --rm \
  --net=host \
  --ipc=host \
  -e DISPLAY=$DISPLAY \
  -e QT_X11_NO_MITSHM=1 \
  -e LIBGL_ALWAYS_SOFTWARE=1 \
  -e GAZEBO_MODEL_DATABASE_URI="" \
  -e GAZEBO_MODEL_PATH="/workspace/models" \
  -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
  -v "$(pwd)":/workspace \
  animal_detection_ros2:humble \
  bash

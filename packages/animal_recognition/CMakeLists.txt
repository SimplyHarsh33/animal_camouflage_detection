cmake_minimum_required(VERSION 3.5)
project(animal_recognition)

find_package(ament_cmake REQUIRED)

install(
  PROGRAMS
    scripts/ros_recognition_yolo.py
  DESTINATION
    lib/${PROJECT_NAME}
)

install(
  DIRECTORY
    launch
  DESTINATION
    share/${PROJECT_NAME}
  OPTIONAL
)

ament_package()

cmake_minimum_required(VERSION 3.5)
project(animal_control)

find_package(ament_cmake REQUIRED)

install(
  DIRECTORY
    launch
  DESTINATION
    share/${PROJECT_NAME}/
  OPTIONAL
)

install(
  PROGRAMS
    scripts/robot_control.py
  DESTINATION
    lib/${PROJECT_NAME}
  OPTIONAL
)

ament_package()

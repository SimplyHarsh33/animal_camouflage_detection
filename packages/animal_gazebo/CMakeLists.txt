cmake_minimum_required(VERSION 3.5)
project(animal_gazebo)

find_package(ament_cmake REQUIRED)

install(
  PROGRAMS
    scripts/generate_random_world.py
  DESTINATION
    lib/${PROJECT_NAME}
)

install(
  DIRECTORY
    launch
    worlds
    scripts
  DESTINATION
    share/${PROJECT_NAME}/
)

ament_package()

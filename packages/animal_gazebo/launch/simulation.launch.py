#!/usr/bin/python3
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

def generate_launch_description():
    pkg_animal_gazebo = get_package_share_directory('animal_gazebo')
    pkg_animal_description = get_package_share_directory('animal_description')

    start_world = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_animal_gazebo, 'launch', 'start_world.launch.py'),
        )
    )

    spawn_robot = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_animal_description, 'launch', 'spawn_robot.launch.py'),
        )
    )

    return LaunchDescription([
        start_world,
        spawn_robot,
    ])

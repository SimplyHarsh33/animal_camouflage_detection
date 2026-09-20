#!/usr/bin/python3
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    pkg_animal_gazebo = get_package_share_directory('animal_gazebo')
    pkg_animal_description = get_package_share_directory('animal_description')

    gui = LaunchConfiguration('gui')

    declare_gui_cmd = DeclareLaunchArgument(
        'gui',
        default_value='false',
        description='Set to "true" for Gazebo 3D GUI window, "false" for headless mode')

    start_world = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_animal_gazebo, 'launch', 'start_world.launch.py'),
        ),
        launch_arguments={'gui': gui}.items()
    )

    spawn_robot = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_animal_description, 'launch', 'spawn_robot.launch.py'),
        )
    )

    return LaunchDescription([
        declare_gui_cmd,
        start_world,
        spawn_robot,
    ])

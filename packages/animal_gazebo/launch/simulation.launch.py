#!/usr/bin/python3
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    pkg_animal_gazebo = get_package_share_directory('animal_gazebo')
    pkg_animal_description = get_package_share_directory('animal_description')
    pkg_animal_recognition = get_package_share_directory('animal_recognition')

    gui = LaunchConfiguration('gui')
    recognition = LaunchConfiguration('recognition')

    declare_gui_cmd = DeclareLaunchArgument(
        'gui',
        default_value='false',
        description='Set to "true" for Gazebo 3D GUI window, "false" for headless mode')

    declare_recognition_cmd = DeclareLaunchArgument(
        'recognition',
        default_value='false',
        description='Set to "true" to automatically start the YOLO camouflage recognition node')

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

    start_recognition = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_animal_recognition, 'launch', 'recognition.launch.py'),
        ),
        condition=IfCondition(recognition)
    )

    return LaunchDescription([
        declare_gui_cmd,
        declare_recognition_cmd,
        start_world,
        spawn_robot,
        start_recognition,
    ])

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
    random_world = LaunchConfiguration('random_world')
    seed = LaunchConfiguration('seed')
    density = LaunchConfiguration('density')
    num_deer = LaunchConfiguration('num_deer')

    declare_gui_cmd = DeclareLaunchArgument(
        'gui',
        default_value='false',
        description='Set to "true" for Gazebo 3D GUI window, "false" for headless mode')

    declare_recognition_cmd = DeclareLaunchArgument(
        'recognition',
        default_value='false',
        description='Set to "true" to automatically start the YOLO camouflage recognition node')

    declare_random_world_cmd = DeclareLaunchArgument(
        'random_world',
        default_value='false',
        description='Set to "true" to procedurally generate a brand new randomized forest on launch')

    declare_seed_cmd = DeclareLaunchArgument(
        'seed',
        default_value='',
        description='Seed for reproducible research world benchmarks (e.g. seed:=42)')

    declare_density_cmd = DeclareLaunchArgument(
        'density',
        default_value='medium',
        description='Vegetation density: low, medium, or high')

    declare_num_deer_cmd = DeclareLaunchArgument(
        'num_deer',
        default_value='3',
        description='Number of deer targets (1-4)')

    start_world = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_animal_gazebo, 'launch', 'start_world.launch.py'),
        ),
        launch_arguments={
            'gui': gui,
            'random_world': random_world,
            'seed': seed,
            'density': density,
            'num_deer': num_deer,
        }.items()
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
        declare_random_world_cmd,
        declare_seed_cmd,
        declare_density_cmd,
        declare_num_deer_cmd,
        start_world,
        spawn_robot,
        start_recognition,
    ])

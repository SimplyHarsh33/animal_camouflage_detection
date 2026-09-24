#!/usr/bin/python3
import os
import sys
import subprocess
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, OpaqueFunction
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration

def launch_setup(context, *args, **kwargs):
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')
    pkg_animal_gazebo = get_package_share_directory('animal_gazebo')

    gui = LaunchConfiguration('gui')
    random_world_str = context.perform_substitution(LaunchConfiguration('random_world'))
    seed_str = context.perform_substitution(LaunchConfiguration('seed'))
    density_str = context.perform_substitution(LaunchConfiguration('density'))
    num_deer_str = context.perform_substitution(LaunchConfiguration('num_deer'))

    world_path = os.path.join(pkg_animal_gazebo, 'worlds', 'animal_world.world')

    # If random_world is true or a seed is provided, run procedural world generator
    if random_world_str.lower() in ['true', '1'] or seed_str.strip() != '':
        gen_script = os.path.join(pkg_animal_gazebo, 'scripts', 'generate_random_world.py')
        if not os.path.exists(gen_script):
            gen_script = os.path.join('/workspace/packages/animal_gazebo/scripts/generate_random_world.py')

        cmd = [sys.executable, gen_script, '--output', world_path]
        if seed_str.strip() != '':
            cmd.extend(['--seed', seed_str.strip()])
        if density_str.strip() != '':
            cmd.extend(['--density', density_str.strip()])
        if num_deer_str.strip() != '':
            cmd.extend(['--num-deer', num_deer_str.strip()])

        print(f"\n[LAUNCH] Generating Procedural Wildlife World...")
        subprocess.run(cmd, check=True)

    # Launch gzserver with custom world and ROS factory plugins
    gzserver = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gzserver.launch.py'),
        ),
        launch_arguments={
            'world': world_path,
            'verbose': 'true',
            'init': 'true',
            'factory': 'true',
            'force_system': 'true',
        }.items()
    )

    # Launch gzclient if gui is true
    gzclient = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gzclient.launch.py'),
        ),
        condition=IfCondition(gui),
        launch_arguments={'verbose': 'true'}.items()
    )

    return [gzserver, gzclient]


def generate_launch_description():
    declare_gui_cmd = DeclareLaunchArgument(
        'gui',
        default_value='false',
        description='Set to "true" to open Gazebo 3D GUI window, "false" for headless')

    declare_random_world_cmd = DeclareLaunchArgument(
        'random_world',
        default_value='false',
        description='Set to "true" to procedurally generate a brand new world on startup')

    declare_seed_cmd = DeclareLaunchArgument(
        'seed',
        default_value='',
        description='Seed for reproducible procedural world generation (e.g. 42)')

    declare_density_cmd = DeclareLaunchArgument(
        'density',
        default_value='medium',
        description='Vegetation density (low, medium, high)')

    declare_num_deer_cmd = DeclareLaunchArgument(
        'num_deer',
        default_value='3',
        description='Number of deer targets (1-4)')

    return LaunchDescription([
        declare_gui_cmd,
        declare_random_world_cmd,
        declare_seed_cmd,
        declare_density_cmd,
        declare_num_deer_cmd,
        OpaqueFunction(function=launch_setup)
    ])

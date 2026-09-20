#!/usr/bin/python3
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')
    pkg_animal_gazebo = get_package_share_directory('animal_gazebo')

    world = LaunchConfiguration('world')
    gui = LaunchConfiguration('gui')

    declare_world_cmd = DeclareLaunchArgument(
        'world',
        default_value=os.path.join(pkg_animal_gazebo, 'worlds', 'animal_world.world'),
        description='SDF world file path')

    declare_gui_cmd = DeclareLaunchArgument(
        'gui',
        default_value='false',
        description='Set to "true" to open Gazebo 3D GUI window, "false" for headless (fast)')

    # Launch gzserver with custom world and ROS factory plugins
    gzserver = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gzserver.launch.py'),
        ),
        launch_arguments={
            'world': world,
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

    return LaunchDescription([
        declare_world_cmd,
        declare_gui_cmd,
        gzserver,
        gzclient,
    ])

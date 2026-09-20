#!/usr/bin/env python3
import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    model_path_arg = DeclareLaunchArgument(
        'model_path',
        default_value='yolov8n.pt',
        description='Path or name of the YOLOv8 model'
    )

    conf_thresh_arg = DeclareLaunchArgument(
        'confidence_threshold',
        default_value='0.25',
        description='Confidence threshold for animal detection'
    )

    clahe_arg = DeclareLaunchArgument(
        'enable_clahe_enhancement',
        default_value='true',
        description='Enable CLAHE preprocessing for camouflage enhancement'
    )

    target_animal_arg = DeclareLaunchArgument(
        'target_animal',
        default_value='deer',
        description='Target animal class name'
    )

    recognition_node = Node(
        package='animal_recognition',
        executable='ros_recognition_yolo.py',
        name='animal_recognition_node',
        output='screen',
        parameters=[{
            'model_path': LaunchConfiguration('model_path'),
            'confidence_threshold': LaunchConfiguration('confidence_threshold'),
            'enable_clahe_enhancement': LaunchConfiguration('enable_clahe_enhancement'),
            'target_animal': LaunchConfiguration('target_animal'),
        }]
    )

    return LaunchDescription([
        model_path_arg,
        conf_thresh_arg,
        clahe_arg,
        target_animal_arg,
        recognition_node
    ])

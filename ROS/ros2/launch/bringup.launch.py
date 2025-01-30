#!/usr/bin/env python
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction, SetEnvironmentVariable
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

from ament_index_python.packages import get_package_share_directory
import os


# def generate_launch_description():
#     config = os.path.join(
#         get_package_share_directory('inertial_sense_ros2'),
#         'config', 'param.yaml')
    
#     return LaunchDescription([

#         # Launch Nodes
#         Node(
#             package='inertial_sense_ros2',
#             executable='inertial_sense_ros2_node',
#             output='screen',
#             parameters=[config],
#         )
        
#     ])

def generate_launch_description():
    # Get the full path to the YAML configuration file
    config_path = os.path.join(
        get_package_share_directory('inertial_sense_ros2'),
        'config',
        'param.yaml'
    )

    return LaunchDescription([
        # Launch the node with the YAML file path as a command-line argument
        Node(
            package='inertial_sense_ros2',
            executable='inertial_sense_ros2_node',
            output='screen',
            arguments=[config_path],  # Pass file path as argument
        )
    ])
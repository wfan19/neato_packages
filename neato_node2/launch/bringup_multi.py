"""
Sample invocation:

ros2 launch neato_node2 bringup_multi.py host:=192.168.16.59 robot_name:=a udp_video_port:=5002 gscam_config:='udpsrc port=5002 ! application/x-rtp, payload=96 ! rtpjitterbuffer ! rtph264depay ! avdec_h264  ! videoconvert'
"""

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.actions import IncludeLaunchDescription, GroupAction
from launch_ros.actions import Node, PushRosNamespace
from launch.substitutions import LaunchConfiguration
import os

def generate_launch_description():
    use_udp = DeclareLaunchArgument('use_udp', default_value="true")
    host = DeclareLaunchArgument('host', default_value="")
    gscam_config = DeclareLaunchArgument('gscam_config', default_value='udpsrc port=5002 ! application/x-rtp, payload=96 ! rtpjitterbuffer ! rtph264depay ! avdec_h264  ! videoconvert')
    udp_video_port = DeclareLaunchArgument('udp_video_port', default_value="5002")
    robot_name = LaunchConfiguration('robot_name')
    robot_name_command = DeclareLaunchArgument('robot_name', default_value='')
    interfaces_launch_file_dir = os.path.join(get_package_share_directory('neato2_gazebo'), 'launch')

    return LaunchDescription([
        use_udp,
        host,
        gscam_config,
        udp_video_port,
        robot_name_command,
        GroupAction(actions=[PushRosNamespace(namespace=robot_name),
           Node(
                package='neato_node2',
                executable='neato_node',
                name='neato_driver',
                parameters=[{"use_udp": LaunchConfiguration('use_udp')},
                            {"robot_name": robot_name},
                            {"host": LaunchConfiguration('host')}],
                output='screen'
           ),
           Node(
                package='fix_scan',
                executable='fix_scan',
                name='fix_scan',
                parameters=[{"robot_name": robot_name}]
            ),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource([interfaces_launch_file_dir, '/robot_state_publisher.py']),
                launch_arguments={'tf_prefix': robot_name}.items()
            ),
            Node(
                package='neato_node2',
                executable='setup_udp_stream',
                name='udp_stream_setup',
                parameters=[{"receive_port": LaunchConfiguration('udp_video_port')},
                            {"width": 1024},
                            {"height": 768},
                            {"fps": 30},
                            {"host": LaunchConfiguration('host')}],
                output='screen'
            ),
            Node(
                package='gscam',
                executable='gscam_node',
                parameters=[
                    {'preroll': True},
                    {'camera_name': 'camera'},
                    {'use_gst_timestamps': False},
                    {'frame_id': 'camera'},
                    {'gscam_config': LaunchConfiguration('gscam_config')}
                ]
            )
        ])
    ])

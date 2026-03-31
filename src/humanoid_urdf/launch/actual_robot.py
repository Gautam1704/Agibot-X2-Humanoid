import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
import xacro
from os.path import join

def generate_launch_description():

    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')
    pkg_ros_gz_rbot = get_package_share_directory('humanoid_urdf')


    robot_description_file = os.path.join(pkg_ros_gz_rbot, 'urdf', 'x2_ultra_simple_collision.urdf')
    ros_gz_bridge_config = os.path.join(pkg_ros_gz_rbot, 'config', 'ros_gz_bridge_gazebo.yaml')
    
    robot_description = { 'robot_description': open(robot_description_file).read() }

   
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[robot_description],
    )

   
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(join(pkg_ros_gz_sim, "launch", "gz_sim.launch.py")),
        launch_arguments={
    'gz_args': '-r -v 4 ' + os.path.join(
        get_package_share_directory('humanoid_urdf'),
        'worlds',
        'empty.world'
    )
}.items()
    )

    spawn_robot = TimerAction(
        period=5.0,  
        actions=[Node(
    package='ros_gz_sim',
    executable='create',
    arguments=[
        "-topic", "/robot_description",
        "-name", "slam",
        "-allow_renaming", "true",   # 👈 change this
            ],
            output='screen'#both robot were getting spawned together so added this to remove existing model before spawn
        )]
    )

    ros_gz_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        parameters=[{'config_file': ros_gz_bridge_config}],
        arguments=[
            # '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
            # '/cmd_vel@geometry_msgs/msg/Twist@ignition.msgs.Twist',
            # '/tf@tf2_msgs/msg/TFMessage@ignition.msgs.Pose_V',
            # '/scan@sensor_msgs/msg/LaserScan@ignition.msgs.LaserScan',
            #'/joint_states@sensor_msgs/msg/JointState@ignition.msgs.Model'


        ],
        output='screen'
    )

    return LaunchDescription([
        gazebo,
        spawn_robot,
        ros_gz_bridge,
        robot_state_publisher,
    ])
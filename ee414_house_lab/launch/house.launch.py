"""Start the EE 414 lab: a TurtleBot3 Burger inside the House world.

    ros2 launch ee414_house_lab house.launch.py              # with the Gazebo window
    ros2 launch ee414_house_lab house.launch.py gui:=false   # no window (weak PC)
    ros2 launch ee414_house_lab house.launch.py rviz:=true   # also open RViz

Or simply:   ./lab sim      (from the repository folder)

What this file starts, in order:
  1. Gazebo, with our world (worlds/ee414_house.sdf)
  2. The Burger robot, at (x, y, yaw) = (-4.0, 0.5, 0.0) in the world
  3. robot_state_publisher, which publishes base_link -> base_scan and the wheels
  4. The bridge, which copies /scan, /odom, /tf, /clock and /cmd_vel
     between Gazebo and ROS 2, plus /ground_truth: where the robot REALLY
     is (only the lab monitor uses it -- a real robot has no such topic)
"""

import os
import tempfile

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (AppendEnvironmentVariable, DeclareLaunchArgument,
                            IncludeLaunchDescription, SetEnvironmentVariable)
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

# The robot always starts here. Lab 2 needs these numbers: the odom frame
# starts where the robot starts, so world -> odom is exactly this pose.
SPAWN_X = '-4.0'
SPAWN_Y = '0.5'
SPAWN_YAW = '0.0'


# Two changes to a COPY of the official Burger model (the original is not touched):
#
# 1. Gazebo knows where the robot REALLY is. This plugin publishes that on
#    /ground_truth (nav_msgs/Odometry, world frame), so the lab monitor can
#    compare it with /odom, which is only what the wheels believe.
#
# 2. Gentler acceleration. With the official limits (1.0 m/s^2 linear, no
#    angular limit) every start and stop is so abrupt that the tall Burger
#    rocks onto its caster and its wheels slip: /odom gains 3-6 degrees of
#    heading error at EVERY start, turn or stop (measured against
#    /ground_truth). Measured on one 9-move test (spins, curves, straights):
#        angular limit 2.0 rad/s^2: 5-6 cm and 1.4-1.8 deg of /odom error
#        angular limit 1.0 rad/s^2: 5 cm and 3 deg
#        angular limit 0.5 rad/s^2: 2 cm and 0.0-0.3 deg      <- used
#    (a frictionless caster or stiffer wheel contact did not help). The robot
#    still reaches 0.6 rad/s in 1.2 s and 0.18 m/s in 0.9 s.
GROUND_TRUTH_PLUGIN = """
    <plugin filename="gz-sim-odometry-publisher-system"
            name="gz::sim::systems::OdometryPublisher">
      <odom_frame>world</odom_frame>
      <robot_base_frame>base_footprint</robot_base_frame>
      <odom_topic>ground_truth</odom_topic>
      <tf_topic>ground_truth_tf</tf_topic>
      <odom_publish_frequency>20</odom_publish_frequency>
      <dimensions>2</dimensions>
    </plugin>
  </model>"""
ACCEL_OLD = '<max_linear_acceleration>1.0</max_linear_acceleration>'
ACCEL_NEW = """<max_linear_acceleration>0.2</max_linear_acceleration>
      <min_linear_acceleration>-0.2</min_linear_acceleration>
      <max_angular_acceleration>0.5</max_angular_acceleration>
      <min_angular_acceleration>-0.5</min_angular_acceleration>"""


def lab_robot_sdf(sdf_path):
    """A copy of the official Burger model with the two changes above."""
    with open(sdf_path) as f:
        text = f.read()
    if ACCEL_OLD not in text:
        raise RuntimeError(f'{sdf_path}: acceleration limit line not found; the TurtleBot3 model changed')
    text = text.replace(ACCEL_OLD, ACCEL_NEW)
    head, _, tail = text.rpartition('</model>')
    out = os.path.join(tempfile.gettempdir(), f'ee414_burger_{os.getuid()}.sdf')
    with open(out, 'w') as f:
        f.write(head + GROUND_TRUTH_PLUGIN + tail)
    return out


def generate_launch_description():
    os.environ['TURTLEBOT3_MODEL'] = 'burger'      # one robot for the whole lab

    lab = get_package_share_directory('ee414_house_lab')
    tb3 = get_package_share_directory('turtlebot3_gazebo')
    ros_gz_sim = get_package_share_directory('ros_gz_sim')

    world = os.path.join(lab, 'worlds', 'ee414_house.sdf')
    robot_sdf = os.path.join(tb3, 'models', 'turtlebot3_burger', 'model.sdf')
    bridge_yaml = os.path.join(tb3, 'params', 'turtlebot3_burger_bridge.yaml')
    rviz_config = os.path.join(lab, 'rviz', 'house_lab.rviz')
    gui_config = os.path.join(lab, 'config', 'gazebo_gui.config')
    with open(os.path.join(tb3, 'urdf', 'turtlebot3_burger.urdf')) as f:
        robot_urdf = f.read()
    robot_sdf = lab_robot_sdf(robot_sdf)

    gui = LaunchConfiguration('gui')
    rviz = LaunchConfiguration('rviz')

    return LaunchDescription([
        DeclareLaunchArgument('gui', default_value='true',
                              description='Show the Gazebo window.'),
        DeclareLaunchArgument('rviz', default_value='false',
                              description='Also open RViz with the lab layout.'),

        SetEnvironmentVariable('TURTLEBOT3_MODEL', 'burger'),
        AppendEnvironmentVariable('GZ_SIM_RESOURCE_PATH', os.path.join(tb3, 'models')),

        # 1. Gazebo: the server always, the window only when gui:=true.
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(ros_gz_sim, 'launch', 'gz_sim.launch.py')),
            launch_arguments={'gz_args': f'-r -s -v1 {world}',
                              'on_exit_shutdown': 'true'}.items()),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(ros_gz_sim, 'launch', 'gz_sim.launch.py')),
            launch_arguments={'gz_args': f'-g -v1 --gui-config {gui_config}',
                              'on_exit_shutdown': 'true'}.items(),
            condition=IfCondition(gui)),

        # 2. The robot.
        Node(package='ros_gz_sim', executable='create', output='screen',
             arguments=['-name', 'burger', '-file', robot_sdf,
                        '-x', SPAWN_X, '-y', SPAWN_Y, '-z', '0.01', '-Y', SPAWN_YAW]),

        # 3. The robot's fixed frames (base_link -> base_scan, ...).
        Node(package='robot_state_publisher', executable='robot_state_publisher',
             output='screen',
             parameters=[{'use_sim_time': True, 'robot_description': robot_urdf}]),

        # 4. Gazebo <-> ROS 2 topics.
        Node(package='ros_gz_bridge', executable='parameter_bridge', output='screen',
             arguments=['--ros-args', '-p', f'config_file:={bridge_yaml}']),
        Node(package='ros_gz_bridge', executable='parameter_bridge', output='screen',
             name='ground_truth_bridge',
             arguments=['/ground_truth@nav_msgs/msg/Odometry[gz.msgs.Odometry']),

        Node(package='rviz2', executable='rviz2', arguments=['-d', rviz_config],
             parameters=[{'use_sim_time': True}], output='log',
             condition=IfCondition(rviz)),
    ])

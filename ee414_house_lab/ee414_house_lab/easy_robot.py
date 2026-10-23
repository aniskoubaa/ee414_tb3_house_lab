"""EasyRobot: a TurtleBot3 node with the boring parts already written.

You do NOT need to change this file. But read it once (Lab 1, Task A3 asks
you about it), because there is no magic here. It is exactly what you wrote
in Weeks 3 and 4:

    one PUBLISHER      /cmd_vel   geometry_msgs/msg/TwistStamped  (to the wheels)
    two SUBSCRIBERS    /scan      sensor_msgs/msg/LaserScan       (from the LiDAR)
                       /odom      nav_msgs/msg/Odometry           (from the wheels)
    one TIMER          calls self.step() 10 times per second

Your lab programs inherit from EasyRobot and write only step():

    class MyRobot(EasyRobot):
        def step(self):
            if self.scan is None:      # no data yet: do nothing
                return
            self.drive(0.1, 0.0)       # 0.1 m/s forward, no turning

    run(MyRobot('my_robot'))
"""

import math
import signal
import time

import rclpy
from geometry_msgs.msg import TwistStamped
from nav_msgs.msg import Odometry
from rclpy.node import Node
from rclpy.signals import SignalHandlerOptions
from sensor_msgs.msg import LaserScan

# TurtleBot3 Burger limits (from the robot's data sheet).
MAX_SPEED = 0.22   # m/s
MAX_TURN = 2.84    # rad/s


def clamp(value, limit):
    """Keep value between -limit and +limit."""
    return max(-limit, min(limit, value))


def yaw_from_quaternion(q):
    """The heading (rotation about z) of a quaternion, in radians.

    A robot on a flat floor only turns about z, so x and y of the
    quaternion are zero and the general formula becomes this one line.
    """
    return math.atan2(2.0 * (q.w * q.z + q.x * q.y), 1.0 - 2.0 * (q.y * q.y + q.z * q.z))


class EasyRobot(Node):
    """A TurtleBot3 node: velocity out, laser and odometry in."""

    def __init__(self, name, rate_hz=10.0):
        super().__init__(name)
        # On ROS 2 Jazzy the TurtleBot3 listens for TwistStamped, not Twist.
        # Publish a plain Twist and NOTHING happens -- and no error is shown.
        self.cmd_pub = self.create_publisher(TwistStamped, '/cmd_vel', 10)
        self.create_subscription(LaserScan, '/scan', self._on_scan, 10)
        self.create_subscription(Odometry, '/odom', self._on_odom, 10)

        self.scan = None          # the latest LaserScan message
        self.scan_time = 0.0      # when it arrived (seconds, wall clock)
        self.x = None             # position in the odom frame (m)
        self.y = None
        self.yaw = None           # heading in the odom frame (rad)
        self.speed = 0.0          # measured forward speed (m/s)
        self.distance = 0.0       # how far the wheels have driven so far (m)

        self.create_timer(1.0 / rate_hz, self._tick)

    # ---- incoming data -------------------------------------------------
    def _on_scan(self, msg):
        self.scan = msg
        self.scan_time = time.monotonic()

    def scan_age(self):
        """Seconds since the last scan arrived (a large number if none yet)."""
        return time.monotonic() - self.scan_time

    def _on_odom(self, msg):
        p = msg.pose.pose.position
        if self.x is not None:
            self.distance += math.hypot(p.x - self.x, p.y - self.y)
        self.x, self.y = p.x, p.y
        self.yaw = yaw_from_quaternion(msg.pose.pose.orientation)
        self.speed = msg.twist.twist.linear.x

    # ---- outgoing commands ---------------------------------------------
    def drive(self, v, w):
        """Send one command: v forward (m/s), w turning (rad/s, + is LEFT)."""
        msg = TwistStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'base_link'
        msg.twist.linear.x = float(clamp(v, MAX_SPEED))
        msg.twist.angular.z = float(clamp(w, MAX_TURN))
        self.cmd_pub.publish(msg)

    def stop(self):
        """Stop the robot. Sent 5 times: a topic does not retry, and one lost
        stop message leaves the robot driving away."""
        if not rclpy.ok():
            return
        for _ in range(5):
            self.drive(0.0, 0.0)
            time.sleep(0.02)

    # ---- the control loop ----------------------------------------------
    def _tick(self):
        self.step()

    def step(self):
        """Called 10 times per second. Your program writes this."""


def run(node):
    """Spin the node until Ctrl-C (or until node.done is True), then stop the robot."""
    # Let Ctrl-C raise KeyboardInterrupt, so that the 'finally' below can
    # still publish the stop command before ROS shuts down.
    signal.signal(signal.SIGINT, signal.default_int_handler)
    try:
        while rclpy.ok() and not getattr(node, 'done', False):
            rclpy.spin_once(node, timeout_sec=0.1)
    except KeyboardInterrupt:
        print('\n  Ctrl-C')
    finally:
        node.stop()
        print('  robot stopped.')
        node.destroy_node()
        rclpy.try_shutdown()


def init():
    """rclpy.init(), but leaving Ctrl-C to us (see run())."""
    rclpy.init(signal_handler_options=SignalHandlerOptions.NO)

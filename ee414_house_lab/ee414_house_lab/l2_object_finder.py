#!/usr/bin/env python3
"""Lab 2 -- find the cylinders with the laser, and put them on the map with TF2.

    terminal 1:   ./lab sim rviz
    terminal 2:   ros2 run ee414_house_lab l2_object_finder
    terminal 3:   ./lab teleop               (drive slowly around the living room)

THE IDEA, IN FOUR STEPS

  1. POINTS.   Each valid laser reading (r, angle) becomes a point (x, y) in
               the frame of the laser, base_scan.                  <- TODO 1

  2. CLUSTERS. Neighbouring points that are close to each other belong to
               the same object. A big jump in distance starts a new object.
               (This part is written for you: find_clusters.)

  3. CYLINDER? A cylinder of radius 0.12 m looks like a short arc about
               0.24 m wide. A wall is much wider; a table leg is much
               narrower. Keep only clusters of the right width.    <- TODO 2
               A cylinder also STANDS ALONE: the beams just beside it see
               something farther away. A short piece of wall seen between
               two door frames does not. (Written for you: stands_alone.)
               Then estimate the CENTRE of the cylinder.           <- TODO 3

  4. TF2.      The centre is in base_scan, which moves with the robot. Ask
               TF2 for the transform base_scan -> odom, and express the
               centre in odom, which does NOT move.                 <- TODO 4

Then (written for you) every cylinder found is remembered, drawn in RViz
as a coloured cylinder on topic /objects, and published as a TF frame
object_0, object_1, ... so that other programs (and Lab 3) can find it.

THE TEST: drive the robot around. If TODO 4 is right, the markers in RViz
stay exactly where the cylinders are. If you swap the two frames, the
markers ride along with the robot.

Test TODO 1-3 without the simulator:   ./lab check 2
"""

import math

import rclpy
from geometry_msgs.msg import PointStamped, TransformStamped
from rclpy.duration import Duration
from rclpy.node import Node
from rclpy.parameter import Parameter
from rclpy.signals import SignalHandlerOptions
from sensor_msgs.msg import LaserScan
from tf2_ros import Buffer, TransformBroadcaster, TransformListener
from visualization_msgs.msg import Marker, MarkerArray

import tf2_geometry_msgs  # noqa: F401  (this import teaches TF2 about PointStamped)
from tf2_geometry_msgs import do_transform_point

CYLINDER_RADIUS = 0.12   # m   all three cylinders have this radius
JUMP = 0.10              # m   a gap this big between neighbours starts a new cluster
MIN_POINTS = 4           #     fewer points than this: too little to trust
MIN_WIDTH = 0.12         # m   a cylinder cluster is between MIN_WIDTH ...
MAX_WIDTH = 0.36         # m   ... and MAX_WIDTH wide
MAX_RANGE = 3.0          # m   ignore objects farther than this (too few points)
SAME_OBJECT = 0.40       # m   a detection this close to a known object IS that object
CONFIRM = 5              #     an object must be seen this many times before we believe it


# ---- 1. points ------------------------------------------------------------

def polar_to_xy(r, angle):
    """TODO 1: a laser reading (r metres, angle radians) -> the point (x, y).

    The laser frame base_scan: x points FORWARD, y points LEFT.
    A reading straight ahead (angle 0) at 2 m is the point (2, 0).
    A reading to the left (angle pi/2) at 1 m is the point (0, 1).

        x = r cos(angle)
        y = r sin(angle)
    """
    raise NotImplementedError('TODO 1: polar_to_xy')


def scan_points(scan):
    """All beams as points in base_scan, in beam order. A beam with no valid
    reading (or too far) becomes None, which will separate two clusters."""
    points = []
    for i, r in enumerate(scan.ranges):
        if math.isfinite(r) and scan.range_min <= r <= min(scan.range_max, MAX_RANGE):
            points.append(polar_to_xy(r, scan.angle_min + i * scan.angle_increment))
        else:
            points.append(None)
    return points


# ---- 2. clusters (written for you) -----------------------------------------

def find_clusters(points):
    """Split the scan into clusters of neighbouring beams.

    Walk through the points in beam order. Keep adding beams to the current
    cluster while each point is within JUMP of the previous one. A None or a
    big jump ends the cluster.

    Returns a list of clusters; each cluster is a list of beam INDICES
    (so we still know which beams are just beside it). The points of a
    cluster are [points[i] for i in cluster].
    """
    clusters, current = [], []
    for i, p in enumerate(points):
        if p is not None and current and math.dist(p, points[current[-1]]) <= JUMP:
            current.append(i)
        else:
            if current:
                clusters.append(current)
            current = [i] if p is not None else []
    if current:
        clusters.append(current)
    # The scan is a circle: the last beam is next to the first one.
    if (len(clusters) > 1 and points[0] is not None and points[-1] is not None
            and math.dist(points[0], points[-1]) <= JUMP):
        clusters[0] = clusters.pop() + clusters[0]
    return clusters


def stands_alone(scan, cluster, margin=0.15):
    """True if the beams just BESIDE the cluster see something farther away
    (or nothing at all). Written for you.

    A cylinder in a room stands in front of the background, so its two
    neighbouring beams hit the wall behind it. A short piece of wall seen
    between two door frames, or the edge of a corner, has a neighbour beam
    that is about as close as the piece itself: that is not a free-standing
    object. On the recorded test drive this one rule removed every false
    detection and kept almost 9 in 10 of the real ones.
    """
    n = len(scan.ranges)
    nearest = min(scan.ranges[i] for i in cluster)
    for beside in (cluster[0] - 1, cluster[-1] + 1):
        r = scan.ranges[beside % n]
        if math.isfinite(r) and scan.range_min <= r <= scan.range_max and r < nearest + margin:
            return False
    return True


# ---- 3. is it a cylinder? where is its centre? -----------------------------

def looks_like_cylinder(cluster):
    """TODO 2: True if this cluster could be one of our cylinders.

    Two checks:
      - it has at least MIN_POINTS points
      - its WIDTH is between MIN_WIDTH and MAX_WIDTH, where the width is the
        distance from its first point to its last point:
              width = math.dist(cluster[0], cluster[-1])

    Why this works: a cylinder of radius 0.12 m always shows an arc about
    0.20-0.24 m wide. A table leg is only 2-4 cm wide. A wall is metres wide.
    """
    raise NotImplementedError('TODO 2: looks_like_cylinder')


def cylinder_centre(cluster):
    """TODO 3: the centre (x, y) of the cylinder, in base_scan.

    Step 1: the average of the points:  mx = mean of the x's, my = mean of the y's.

    Step 2: the laser only sees the FRONT of the cylinder, so the average
    point lies ON THE SURFACE, about one radius too close to the robot:

                robot  o ------------>  (  .  )      . = true centre
                                        ^
                                   the points are here

    So push the point further away, along the same direction, by one
    radius. The direction from the robot to (mx, my) has length
    d = math.hypot(mx, my), so the pushed point is

              (mx, my) * (d + CYLINDER_RADIUS) / d

    Return (x, y).
    """
    raise NotImplementedError('TODO 3: cylinder_centre')


# ---- the node ---------------------------------------------------------------

class ObjectFinder(Node):

    def __init__(self):
        super().__init__('l2_object_finder',
                         parameter_overrides=[Parameter('use_sim_time', value=True)])
        self.tf_buffer = Buffer()
        # The listener gets its OWN little node (None) and its own thread
        # (spin_thread=True), so /tf keeps arriving while on_scan waits inside
        # lookup_transform(..., timeout). With one thread for everything, the
        # wait blocks the very messages it is waiting for, and every lookup fails.
        self.tf_listener = TransformListener(self.tf_buffer, None, spin_thread=True)
        self.tf_broadcaster = TransformBroadcaster(self)
        self.marker_pub = self.create_publisher(MarkerArray, '/objects', 10)
        self.create_subscription(LaserScan, '/scan', self.on_scan, 10)
        self.objects = []        # each one: {'x': .., 'y': .., 'seen': .., 'id': ..}  (odom frame)
        self.next_id = 0         # the number of the next object we become sure about
        self.tf_errors = 0

    def to_odom(self, x, y, stamp):
        """TODO 4: the point (x, y) in base_scan -> the same point in odom.

        Three lines, exactly as in Lecture 7B:

          1. Ask TF2 for the transform that takes base_scan coordinates to
             odom coordinates, at the time the scan was taken:

                t = self.tf_buffer.lookup_transform(
                        'odom', 'base_scan', stamp, timeout=Duration(seconds=0.2))

             Remember the order:  lookup_transform(TARGET, SOURCE, time).
             We want the point IN odom, so odom is the target.

          2. Make a PointStamped in base_scan (written for you below: p).

          3. q = do_transform_point(p, t)     and return (q.point.x, q.point.y).

        If the transform is not available yet, lookup_transform raises an
        exception. That is normal for the first second; on_scan catches it.
        """
        p = PointStamped()
        p.header.frame_id = 'base_scan'
        p.header.stamp = stamp
        p.point.x, p.point.y = float(x), float(y)
        raise NotImplementedError('TODO 4: to_odom')

    def on_scan(self, scan):
        points = scan_points(scan)
        for beams in find_clusters(points):
            cluster = [points[i] for i in beams]
            if not looks_like_cylinder(cluster) or not stands_alone(scan, beams):
                continue
            cx, cy = cylinder_centre(cluster)
            try:
                ox, oy = self.to_odom(cx, cy, scan.header.stamp)
            except NotImplementedError:
                raise
            except Exception as e:          # TF not ready yet: skip this scan
                self.tf_errors += 1
                if self.tf_errors in (1, 10, 100):
                    self.get_logger().warn(f'TF not ready ({type(e).__name__}): {e}')
                return
            self.remember(ox, oy)
        self.publish()

    def remember(self, x, y):
        """Average a new detection into a known object, or start a new one."""
        for obj in self.objects:
            if math.dist((x, y), (obj['x'], obj['y'])) < SAME_OBJECT:
                n = min(obj['seen'], 20)           # a running average over the last ~20
                obj['x'] = (obj['x'] * n + x) / (n + 1)
                obj['y'] = (obj['y'] * n + y) / (n + 1)
                obj['seen'] += 1
                if obj['seen'] == CONFIRM:          # sure now: give it a name for good
                    obj['id'] = self.next_id
                    self.next_id += 1
                    print(f'  NEW OBJECT object_{obj["id"]} '
                          f'at odom ({obj["x"]:+.2f}, {obj["y"]:+.2f})')
                return
        self.objects.append({'x': x, 'y': y, 'seen': 1, 'id': None})

    def confirmed(self):
        """The objects seen at least CONFIRM times, in the order they were named."""
        return sorted((o for o in self.objects if o['id'] is not None), key=lambda o: o['id'])

    def publish(self):
        """Draw every confirmed object in RViz and broadcast it as a TF frame."""
        markers = MarkerArray()
        now = self.get_clock().now().to_msg()
        for obj in self.confirmed():
            i = obj['id']
            t = TransformStamped()
            t.header.stamp = now
            t.header.frame_id = 'odom'
            t.child_frame_id = f'object_{i}'
            t.transform.translation.x = obj['x']
            t.transform.translation.y = obj['y']
            t.transform.rotation.w = 1.0
            self.tf_broadcaster.sendTransform(t)

            m = Marker()
            m.header.frame_id = 'odom'
            m.header.stamp = now
            m.ns, m.id, m.type, m.action = 'objects', i, Marker.CYLINDER, Marker.ADD
            m.pose.position.x, m.pose.position.y, m.pose.position.z = obj['x'], obj['y'], 0.25
            m.pose.orientation.w = 1.0
            m.scale.x = m.scale.y = 2 * CYLINDER_RADIUS
            m.scale.z = 0.5
            m.color.r, m.color.g, m.color.b, m.color.a = 1.0, 0.8, 0.0, 0.8
            markers.markers.append(m)

            label = Marker()
            label.header = m.header
            label.ns, label.id, label.type, label.action = 'labels', i, Marker.TEXT_VIEW_FACING, Marker.ADD
            label.pose.position.x, label.pose.position.y, label.pose.position.z = obj['x'], obj['y'], 0.7
            label.pose.orientation.w = 1.0
            label.scale.z = 0.2
            label.color.r = label.color.g = label.color.b = label.color.a = 1.0
            label.text = f'object_{i}'
            markers.markers.append(label)
        self.marker_pub.publish(markers)


def main():
    rclpy.init(signal_handler_options=SignalHandlerOptions.NO)
    node = ObjectFinder()
    print('\n  Looking for cylinders. Drive slowly with ./lab teleop. Ctrl-C to stop.\n')
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        print('\n  Objects found (odom frame):')
        for o in node.confirmed():
            print(f'    object_{o["id"]}:  x = {o["x"]:+.3f}   y = {o["y"]:+.3f}   (seen {o["seen"]} times)')
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()

# Cheat sheet

## The lab

```bash
./lab sim | sim nogui | sim rviz      ./lab teleop      ./lab rviz      ./lab stop
./lab check 1|2|3                      ./lab run <program> [args]
./lab monitor 1                        ./lab monitor 3 --goal X Y
./lab submit N <ID>                    ./lab doctor
```

## ROS 2: look at the robot

```bash
ros2 topic list                        # all topics
ros2 topic type /cmd_vel               # geometry_msgs/msg/TwistStamped
ros2 topic hz /scan                    # rate (Ctrl-C)
ros2 topic echo /scan --once           # one message
ros2 topic echo /odom --field pose.pose.position
ros2 node list
```

## TF2: frames

```bash
ros2 run tf2_tools view_frames                       # the tree as a PDF
ros2 run tf2_ros tf2_echo base_link base_scan        # one transform, live
ros2 run tf2_ros tf2_echo odom object_0              # where is object_0 ?
ros2 run tf2_ros static_transform_publisher --x -4.0 --y 0.5 \
    --frame-id world --child-frame-id odom           # publish a fixed transform
```

`lookup_transform(TARGET, SOURCE, time)` gives the transform that takes a point **from SOURCE
to TARGET**.

## The robot: TurtleBot3 Burger

| | |
|---|---|
| max speed | 0.22 m/s forward, 2.84 rad/s turning (the lab uses ≤ 0.6 rad/s) |
| laser | 360 beams, 1° apart, 0.12–3.5 m, 5 scans/s, **17 cm above the floor** |
| beam 0 | straight ahead; angles grow to the **left** (counter-clockwise) |
| frames | `odom → base_footprint → base_link → base_scan` |
| start | world (−4.0, 0.5), facing +x, which is odom (0, 0) |

## The world (world frame, metres)

| Thing | Position |
|---|---|
| red cylinder (r = 0.12) | (−3.0, 3.6) |
| green cylinder | (−1.0, 2.0) |
| blue cylinder | (−4.3, 2.4) |
| orange box (0.4 × 1.0) | centre (−2.4, 0.45) |
| robot start | (−4.0, 0.5), yaw 0 |

`world = odom + (−4.0, 0.5)` (no rotation, because the start yaw is 0).

## Python you will need

```python
import math
math.inf, math.isinf(r), math.isfinite(r), math.isnan(r)
math.cos(a), math.sin(a), math.atan2(y, x)       # radians
math.degrees(a), math.radians(d)
math.hypot(dx, dy)                               # length of (dx, dy)
math.dist((x1, y1), (x2, y2))                    # distance between two points
min(a, b), max(a, b), abs(x), sum(list) / len(list)
for i, r in enumerate(scan.ranges):              # index and value together
```

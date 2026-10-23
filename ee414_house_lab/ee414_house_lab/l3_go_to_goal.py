#!/usr/bin/env python3
"""Lab 3, Part A -- drive to a goal point (no obstacles yet).

    terminal 1:   ./lab sim
    terminal 2:   ./lab monitor 3 --goal 1.0 1.0
    terminal 3:   ros2 run ee414_house_lab l3_go_to_goal 1.0 1.0

The goal (gx, gy) is in the ODOM frame: (0, 0) is where the robot started,
x is the direction it was facing at the start, y is to its left.

CLOSED-LOOP CONTROL: 10 times per second the robot
    1. reads where it is:  x, y, yaw   (from /odom)
    2. computes two errors:
          distance       how far away the goal is
          heading error  how much it must turn to face the goal
    3. turns in proportion to the heading error, and drives forward in
       proportion to the distance -- but only once it roughly faces the goal.

          goal  *
               /
              /  distance
             /
            / ) heading error = (direction to goal) - yaw
     robot o --------> (the way the robot faces, yaw)

YOUR TASKS:  TODO 1 and TODO 2 below.
Test them without the simulator:   ./lab check 3
"""

import math
import sys

from ee414_house_lab.easy_robot import EasyRobot, clamp, init, run

K_DRIVE = 0.5          # (m/s) per metre of distance
K_TURN = 1.5           # (rad/s) per radian of heading error
MAX_SPEED = 0.18       # m/s
MAX_TURN = 0.6         # rad/s  (faster turns make the wheels slip: /odom drifts)
AIM_FIRST = math.radians(45)   # heading error larger than this: turn on the spot first
GOAL_TOL = 0.10        # m    closer than this: we are there


def angle_wrap(a):
    """TODO 1: the same angle, but between -pi and +pi.

    Why: the robot faces 170 deg and the goal is at -170 deg. The heading
    error is -170 - 170 = -340 deg: "turn right almost a full circle".
    Wrapped, it is +20 deg: "turn left a little". Always wrap an angle
    that you got by subtracting two angles.

    One line does it:   math.atan2(math.sin(a), math.cos(a))
    """
    raise NotImplementedError('TODO 1: angle_wrap')


def go_to_goal_command(x, y, yaw, gx, gy):
    """TODO 2: the (v, w) that drives the robot at (x, y, yaw) toward (gx, gy).

    Steps:
      distance      = math.hypot(gx - x, gy - y)
      goal_angle    = math.atan2(gy - y, gx - x)
      heading_error = angle_wrap(goal_angle - yaw)

      w = K_TURN * heading_error           limited to +-MAX_TURN  (use clamp)
      v = K_DRIVE * distance               limited to MAX_SPEED   (use min)
      but if abs(heading_error) > AIM_FIRST:  v = 0   (turn first, then drive)

    Return (v, w).
    """
    raise NotImplementedError('TODO 2: go_to_goal_command')


class GoToGoal(EasyRobot):

    def __init__(self, gx, gy):
        super().__init__('l3_go_to_goal')
        self.gx, self.gy = gx, gy
        self.done = False
        self.ticks = 0

    def step(self):
        if self.x is None:              # no odometry yet
            return
        distance = math.hypot(self.gx - self.x, self.gy - self.y)
        if distance < GOAL_TOL:
            self.stop()
            print(f'\n  GOAL reached: ({self.x:+.2f}, {self.y:+.2f}), '
                  f'{distance * 100:.0f} cm from the goal, after {self.distance:.2f} m of driving.')
            self.done = True
            return
        v, w = go_to_goal_command(self.x, self.y, self.yaw, self.gx, self.gy)
        self.drive(v, w)
        self.ticks += 1
        if self.ticks % 10 == 0:
            print(f'  at ({self.x:+.2f}, {self.y:+.2f})  yaw {math.degrees(self.yaw):+5.0f} deg'
                  f'   distance {distance:.2f} m   v={v:.2f}  w={w:+.2f}')


def read_goal(default=(1.0, 1.0)):
    """The goal from the command line:  ... l3_go_to_goal 1.0 1.0"""
    numbers = [a for a in sys.argv[1:] if not a.startswith('-')]
    if len(numbers) >= 2:
        return float(numbers[0]), float(numbers[1])
    return default


def main():
    gx, gy = read_goal()
    init()
    print(f'\n  Going to ({gx}, {gy}) in the odom frame. Ctrl-C to stop.\n')
    run(GoToGoal(gx, gy))


if __name__ == '__main__':
    main()

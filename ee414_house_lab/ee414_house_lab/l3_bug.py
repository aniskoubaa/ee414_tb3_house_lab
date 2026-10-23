#!/usr/bin/env python3
"""Lab 3, Parts B and C -- the Bug algorithm: reach a goal behind an obstacle.

    terminal 1:   ./lab sim
    terminal 2:   ./lab monitor 3 --goal 3.0 0.0
    terminal 3:   ros2 run ee414_house_lab l3_bug 3.0 0.0 --algorithm bug0
                  ros2 run ee414_house_lab l3_bug 3.0 0.0 --algorithm bug2

The goal (3.0, 0.0) in odom is 3 m straight ahead of the start, behind the
orange box. Your go-to-goal from Part A would drive straight into the box.

THE BUG ALGORITHM uses only two behaviours you already have:
    GO_TO_GOAL    your go_to_goal_command  (Part A)
    FOLLOW_WALL   keep the obstacle on the RIGHT, at WALL_DIST (written for you)
and switches between them:

                     front < HIT_DIST   (the "hit point")
    +------------+  ------------------->  +-------------+
    | GO_TO_GOAL |                        | FOLLOW_WALL |
    +------------+  <-------------------  +-------------+
                        the LEAVE rule

The two algorithms differ ONLY in the leave rule:

  Bug 0:  leave the wall as soon as the direction to the goal is clear.
          Simple. Can loop for ever around some obstacles.

  Bug 2:  draw the "m-line", the straight line from the START to the GOAL.
          Leave the wall only when you are back on the m-line AND closer to
          the goal than you were at the hit point.
          Never loops: each time it leaves, it is closer to the goal.

YOUR TASKS:  TODO 3 (Bug 0 leave rule), TODO 4 (m-line), TODO 5 (the switch).
Test them without the simulator:   ./lab check 3
"""

import math
import sys

from ee414_house_lab.easy_robot import EasyRobot, clamp, init, run
from ee414_house_lab.l1_scan_reader import sector_min
from ee414_house_lab.l3_go_to_goal import angle_wrap, go_to_goal_command, read_goal

HIT_DIST = 0.40        # m   front closer than this: we hit an obstacle
WALL_DIST = 0.35       # m   keep the wall this far away on the right
WALL_SPEED = 0.12      # m/s while following a wall
K_WALL = 2.5           # (rad/s) per metre of wall-distance error
LOST_WALL = 0.80       # m   right side farther than this: we passed a corner
CLEAR_AHEAD = 1.00     # m   Bug 0: "the way to the goal is clear" means nothing within this
MLINE_TOL = 0.10       # m   Bug 2: this close to the m-line counts as "on it"
GOAL_TOL = 0.15        # m


# ---- the two behaviours -----------------------------------------------------

def follow_wall(scan):
    """Keep the obstacle on the RIGHT side at WALL_DIST. Written for you.

    - Something close in front: turn left on the spot.
    - Wall lost on the right (we passed its corner): arc to the right to find it.
    - Otherwise: drive forward and steer so that the right distance = WALL_DIST
      (too close: turn left; too far: turn right) -- a P controller.
    """
    front = sector_min(scan, -30.0, 30.0)
    right = sector_min(scan, -110.0, -40.0)
    if front < HIT_DIST:
        return 0.0, 0.5
    if right > LOST_WALL:
        return 0.08, -0.45
    error = WALL_DIST - right             # > 0 when too close
    return WALL_SPEED, clamp(K_WALL * error, 0.6)


# ---- the leave rules ---------------------------------------------------------

def goal_direction_clear(scan, x, y, yaw, gx, gy):
    """TODO 3 (Bug 0): True if nothing blocks the way toward the goal.

    Steps:
      1. the direction of the goal SEEN FROM THE ROBOT, in degrees:
             a = math.degrees(angle_wrap(math.atan2(gy - y, gx - x) - yaw))
         (0 = straight ahead, + = to the left -- the same angles as the laser)
      2. the nearest obstacle in a 40-degree cone around it:
             nearest = sector_min(scan, a - 20, a + 20)
         (if a - 20 < -180 or a + 20 > 180 this misses a few beams; ignore it)
      3. it is clear if that obstacle is farther than CLEAR_AHEAD,
         OR farther than the goal itself (an obstacle BEHIND the goal does not matter):
             return nearest > min(CLEAR_AHEAD, distance to the goal)
    """
    raise NotImplementedError('TODO 3: goal_direction_clear')


def distance_to_mline(sx, sy, gx, gy, x, y):
    """TODO 4 (Bug 2): the distance from the point (x, y) to the straight
    line through the start (sx, sy) and the goal (gx, gy).

    The formula (the area of a parallelogram divided by its base):

        | (gx - sx) * (sy - y)  -  (sx - x) * (gy - sy) |
        -------------------------------------------------
                  distance from start to goal

    Use abs(...) for | |, and math.hypot(gx - sx, gy - sy) for the bottom.
    Check: start (0,0), goal (4,0), point (2,1)  ->  1.0
    """
    raise NotImplementedError('TODO 4: distance_to_mline')


# ---- the node ------------------------------------------------------------------

class Bug(EasyRobot):

    def __init__(self, gx, gy, algorithm):
        super().__init__('l3_bug')
        self.gx, self.gy = gx, gy
        self.algorithm = algorithm
        self.state = 'GO_TO_GOAL'
        self.sx = self.sy = None       # the start: one end of the m-line
        self.hit_x = self.hit_y = None  # where we hit the obstacle
        self.hit_dist = math.inf        # how far the goal was at the hit point
        self.done = False
        self.ticks = 0

    def switch(self, front, dist):
        """TODO 5: change self.state when needed. Returns nothing.

        front = nearest obstacle ahead (m),  dist = distance to the goal (m).
        The robot is at self.x, self.y; the goal is self.gx, self.gy.

        - In 'GO_TO_GOAL': if front < HIT_DIST, this is a HIT POINT:
              self.state = 'FOLLOW_WALL'
              remember it:   self.hit_x, self.hit_y = self.x, self.y
                             self.hit_dist = dist
              print('  HIT ...') so you can follow what happens

        - In 'FOLLOW_WALL': first, ignore the first 0.3 m after the hit point
          (we are still standing at it):  if math.hypot(self.x - self.hit_x,
          self.y - self.hit_y) < 0.3: return
          Then use the LEAVE rule of self.algorithm:
              'bug0':  goal_direction_clear(self.scan, self.x, self.y, self.yaw, self.gx, self.gy)
              'bug2':  distance_to_mline(self.sx, self.sy, self.gx, self.gy, self.x, self.y)
                         < MLINE_TOL
                       and dist < self.hit_dist - 0.1
          If the rule says leave:  self.state = 'GO_TO_GOAL'  and print('  LEAVE ...')
        """
        raise NotImplementedError('TODO 5: switch')

    def step(self):
        if self.x is None or self.scan is None:
            return
        if self.sx is None:
            self.sx, self.sy = self.x, self.y          # the start of the m-line
        dist = math.hypot(self.gx - self.x, self.gy - self.y)
        if dist < GOAL_TOL:
            self.stop()
            print(f'\n  GOAL reached with {self.algorithm}: {dist * 100:.0f} cm away, '
                  f'{self.distance:.2f} m driven.')
            self.done = True
            return

        front = sector_min(self.scan, -30.0, 30.0)
        self.switch(front, dist)
        if self.state == 'GO_TO_GOAL':
            v, w = go_to_goal_command(self.x, self.y, self.yaw, self.gx, self.gy)
        else:
            v, w = follow_wall(self.scan)
        self.drive(v, w)

        self.ticks += 1
        if self.ticks % 10 == 0:
            print(f'  {self.state:<11} at ({self.x:+.2f}, {self.y:+.2f})   goal {dist:.2f} m'
                  f'   front {front:.2f} m')


def main():
    algorithm = 'bug2' if '--algorithm' not in sys.argv else sys.argv[sys.argv.index('--algorithm') + 1]
    if algorithm not in ('bug0', 'bug2'):
        raise SystemExit('--algorithm must be bug0 or bug2')
    gx, gy = read_goal(default=(3.0, 0.0))
    init()
    print(f'\n  {algorithm.upper()} to ({gx}, {gy}) in the odom frame. Ctrl-C to stop.\n')
    run(Bug(gx, gy, algorithm))


if __name__ == '__main__':
    main()

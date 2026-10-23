#!/usr/bin/env python3
"""Lab 1, Part C -- a robot that wanders around the house without hitting anything.

    terminal 1:   ./lab sim
    terminal 2:   ros2 run ee414_house_lab l1_wander
    terminal 3:   ./lab monitor 1          (measures your run for the report)

This is REACTIVE navigation: no map, no goal, no memory. Every 0.1 s the
robot looks at the latest scan and chooses a command. Three steps, always
the same:

    SENSE   read three distances: front, left, right  (your sector_min from Part B)
    DECIDE  choose (v, w)                              <-- TODO 3, your work
    ACT     self.drive(v, w)

The DECIDE step is a small STATE MACHINE with two states:

         front < STOP_DIST
    +---------+  ------------------>  +--------+
    | FORWARD |                       |  TURN  |
    +---------+  <------------------  +--------+
         front > CLEAR_DIST

    FORWARD: drive forward, and steer a little toward the more open side.
    TURN:    stand still and rotate, always in the SAME direction, until the
             front is clear again.

Two details make it work:

  1. TWO thresholds, not one (STOP_DIST < CLEAR_DIST). With one threshold
     the robot stops turning the moment the front is "just" clear, drives
     off, and is back at the threshold a moment later: stop, go, stop, go.
     A home thermostat uses the same trick.

  2. The turn direction is chosen ONCE, when the turn starts. If you choose
     it again every 0.1 s, a symmetric obstacle (a wall straight ahead)
     makes the robot turn left, right, left, right ... for ever.

YOUR TASK:  TODO 3 below (two parts, 3a and 3b).
Test it without the simulator:   ./lab check 1
"""

import random

from ee414_house_lab.easy_robot import EasyRobot, clamp, init, run
from ee414_house_lab.l1_scan_reader import sector_min

# ---- the numbers you will tune (Task C3) --------------------------------
STOP_DIST = 0.45      # m    front closer than this  -> start turning
CLEAR_DIST = 0.65     # m    front farther than this -> drive again
FORWARD_SPEED = 0.18  # m/s  (the Burger's maximum is 0.22)
TURN_SPEED = 0.6      # rad/s  (faster turns make the wheels slip: /odom drifts)
SIDE_GAIN = 0.8       # how strongly to steer toward the open side

# The three sectors, in degrees (0 = front, + = left).
FRONT = (-25.0, 25.0)
LEFT = (25.0, 70.0)
RIGHT = (-70.0, -25.0)

SCAN_TIMEOUT = 1.0    # s    no new scan for this long -> the robot is blind: stop


class Wanderer(EasyRobot):

    def __init__(self):
        super().__init__('l1_wander')
        self.state = 'FORWARD'
        self.turn_dir = 1.0       # +1 = turn left, -1 = turn right
        self.ticks = 0

    def decide(self, front, left, right):
        """TODO 3: one decision. Distances in, (v, w) out.

        front, left, right are your sector_min values (math.inf = clear).

        3a. Change the state if needed:
            - if state is 'FORWARD' and front < STOP_DIST:
                  state = 'TURN'
                  choose turn_dir ONCE: +1.0 (left) if left > right, else -1.0
                  (if left and right are almost equal -- within 0.1 m, or both
                  inf -- pick +1.0 or -1.0 at random: random.choice([1.0, -1.0]))
            - if state is 'TURN' and front > CLEAR_DIST:
                  state = 'FORWARD'

        3b. Choose the command for the current state:
            - TURN:     v = 0,  w = turn_dir * TURN_SPEED
            - FORWARD:  v = FORWARD_SPEED
                        w = SIDE_GAIN * (L - R), where L and R are left and right
                        with inf replaced by 3.5 (use min(left, 3.5)), so that the
                        robot steers toward the side with more room.
                        Limit w to +-TURN_SPEED with clamp(w, TURN_SPEED).

        Return (v, w). Keep the state in self.state and the direction in self.turn_dir.
        """
        raise NotImplementedError('TODO 3: decide')

    def step(self):
        scan = self.scan
        # Blind rule: no new scan for SCAN_TIMEOUT seconds -> do not move.
        if scan is None or self.scan_age() > SCAN_TIMEOUT:
            self.drive(0.0, 0.0)
            return

        # SENSE
        front = sector_min(scan, *FRONT)
        left = sector_min(scan, *LEFT)
        right = sector_min(scan, *RIGHT)
        # DECIDE
        v, w = self.decide(front, left, right)
        # ACT
        self.drive(v, w)

        self.ticks += 1
        if self.ticks % 10 == 0:          # print once per second
            print(f'  front {front:5.2f}  left {left:5.2f}  right {right:5.2f}'
                  f'   {self.state:<8} v={v:.2f}  w={w:+.2f}')


def main():
    init()
    print(f'\n  Wandering. STOP_DIST={STOP_DIST} m, CLEAR_DIST={CLEAR_DIST} m. Ctrl-C to stop.\n')
    run(Wanderer())


if __name__ == '__main__':
    main()

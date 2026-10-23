#!/usr/bin/env python3
"""Lab 1, Part B -- read the laser scanner.

    terminal 1:   ./lab sim
    terminal 2:   ./lab teleop                       (drive the robot around)
    terminal 3:   ros2 run ee414_house_lab l1_scan_reader

Once per second this prints how far the nearest obstacle is in front,
to the left, to the right and behind the robot.

THE LASER SCAN IN ONE PICTURE (TurtleBot3, seen from above)

                    90 deg (LEFT)
                         |
       180 deg  ---- [ robot ] ---->  0 deg (FRONT)
                         |
                   -90 deg (RIGHT)

  scan.ranges is a list of 360 numbers. ranges[i] is the distance (m)
  measured by beam i, and beam i points at the angle

        angle_i = scan.angle_min + i * scan.angle_increment     (radians)

  On the TurtleBot3, angle_min = 0 and angle_increment = 1 degree, so beam 0
  looks straight ahead and beam 90 looks left. But do NOT write "beam 90 is
  the left" in your code: on another robot it is not. Always use the formula.

  Not every number in ranges is a distance:
        inf        nothing was hit within range_max (3.5 m): FREE SPACE
        nan        no usable reading
        < 0.12 m   closer than range_min: the sensor cannot measure it
  A reading is VALID only if it is a finite number between range_min and
  range_max.

YOUR TASKS:  TODO 1 and TODO 2 below.
Test them without the simulator:   ./lab check 1
"""

import math

import rclpy

from ee414_house_lab.easy_robot import EasyRobot, init, run


def beam_angle_deg(scan, i):
    """TODO 1: the angle of beam i, in DEGREES, between -180 and +180.

    0 is straight ahead, +90 is left, -90 is right.

    Steps:
      1. angle = scan.angle_min + i * scan.angle_increment     (radians)
      2. convert to degrees:  math.degrees(angle)
      3. bring it into (-180, 180]:  while above 180 subtract 360,
                                     while at or below -180 add 360
    Example: on the TurtleBot3 beam 270 is at 270 deg, which is -90 deg (right).
    """
    raise NotImplementedError('TODO 1: beam_angle_deg')


def is_valid(scan, r):
    """True if r is a real distance the scanner measured (see the top of the file)."""
    return math.isfinite(r) and scan.range_min <= r <= scan.range_max


def sector_min(scan, from_deg, to_deg):
    """TODO 2: the nearest VALID reading with an angle between from_deg and to_deg.

    Return math.inf if there is no valid reading in that sector -- for the
    TurtleBot3 this means "nothing closer than 3.5 m": the sector is clear.

    Steps:
      nearest = math.inf
      for every beam i (use: for i, r in enumerate(scan.ranges)):
          if its angle (TODO 1) is between from_deg and to_deg,
          and is_valid(scan, r):
              nearest = min(nearest, r)
      return nearest

    Why the MINIMUM and not the average? A chair leg may fill only 3 of the
    40 beams in the sector. The average hides it. The nearest thing is the
    thing you will hit.
    """
    raise NotImplementedError('TODO 2: sector_min')


def back_min(scan):
    """The nearest reading behind the robot. 'Behind' crosses the +-180 line,
    so it is two sectors: 160..180 and -180..-160."""
    return min(sector_min(scan, 160.0, 180.0), sector_min(scan, -180.0, -160.0))


def closest(scan):
    """(distance, angle in degrees) of the nearest valid reading."""
    best_r, best_a = math.inf, 0.0
    for i, r in enumerate(scan.ranges):
        if is_valid(scan, r) and r < best_r:
            best_r, best_a = r, beam_angle_deg(scan, i)
    return best_r, best_a


def show(r):
    """A distance as text: 'inf' (free space) or e.g. '1.23'."""
    return '  inf' if math.isinf(r) else f'{r:5.2f}'


class ScanReader(EasyRobot):

    def __init__(self):
        super().__init__('l1_scan_reader', rate_hz=1.0)   # print once per second
        print('\n  Waiting for /scan ...  (is ./lab sim running?)\n')

    def step(self):
        scan = self.scan
        if scan is None:
            return
        front = sector_min(scan, -20.0, 20.0)
        left = sector_min(scan, 60.0, 120.0)
        right = sector_min(scan, -120.0, -60.0)
        back = back_min(scan)
        near_r, near_a = closest(scan)
        n_inf = sum(1 for r in scan.ranges if math.isinf(r))

        print(f'  FRONT {show(front)}   LEFT {show(left)}   RIGHT {show(right)}'
              f'   BACK {show(back)}   | nearest {show(near_r)} m at {near_a:+5.0f} deg'
              f'   | {n_inf:3d} of {len(scan.ranges)} beams see nothing (inf)')

    def stop(self):
        pass          # this program never drives, so it must not send stop either:
                      # that would fight with teleop


def main():
    init()
    run(ScanReader())


if __name__ == '__main__':
    main()

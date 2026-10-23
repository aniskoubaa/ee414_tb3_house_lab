"""Shared helpers for the lab checks. Run them with:  ./lab check 1   (or 2, 3)"""
import math
import os
import pathlib
import sys

# Import the lab code straight from this repository (no build needed).
# (EE414_CODE_DIR lets the instructor check the solution copy instead.)
sys.path.insert(0, os.environ.get('EE414_CODE_DIR',
                                  str(pathlib.Path(__file__).resolve().parents[1] / 'ee414_house_lab')))


class FakeScan:
    """A LaserScan without ROS: 360 beams, 1 degree apart, starting straight ahead,
    exactly like the TurtleBot3. Every beam sees `default` unless told otherwise."""

    def __init__(self, default=math.inf, n=360, angle_min=0.0):
        self.angle_min = angle_min
        self.angle_increment = 2 * math.pi / n
        self.range_min = 0.12
        self.range_max = 3.5
        self.ranges = [default] * n

    def put(self, from_deg, to_deg, r):
        """Make every beam whose angle is in [from_deg, to_deg] read r."""
        for i in range(len(self.ranges)):
            a = math.degrees(self.angle_min + i * self.angle_increment)
            a = (a + 180.0) % 360.0 - 180.0
            if from_deg <= a <= to_deg:
                self.ranges[i] = r
        return self

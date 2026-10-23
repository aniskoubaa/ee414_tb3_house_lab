"""Lab 2 checks: TODO 1 (polar_to_xy), TODO 2 (looks_like_cylinder), TODO 3 (cylinder_centre).
TODO 4 (to_odom) needs TF, so it is checked in the simulator: the markers must not move."""
import math

import pytest
from conftest import FakeScan

from ee414_house_lab import l2_object_finder as finder


def test_todo1_front():
    assert finder.polar_to_xy(2.0, 0.0) == pytest.approx((2.0, 0.0)), '2 m straight ahead is the point (2, 0)'


def test_todo1_left():
    assert finder.polar_to_xy(1.0, math.pi / 2) == pytest.approx((0.0, 1.0), abs=1e-9), \
        '1 m to the left (pi/2) is the point (0, 1): x = r cos(a), y = r sin(a)'


def test_todo1_diagonal_right():
    x, y = finder.polar_to_xy(math.sqrt(2), -math.pi / 4)
    assert (x, y) == pytest.approx((1.0, -1.0)), 'sqrt(2) m at -45 deg is the point (1, -1)'


def arc(cx, cy, radius, n=7, spread_deg=120):
    """Points on the side of a circle that faces the origin (what a laser sees)."""
    facing = math.atan2(-cy, -cx)
    return [(cx + radius * math.cos(facing + math.radians(a)),
             cy + radius * math.sin(facing + math.radians(a)))
            for a in [(-spread_deg / 2 + k * spread_deg / (n - 1)) for k in range(n)]]


def test_todo2_cylinder_yes():
    assert finder.looks_like_cylinder(arc(1.5, 0.3, 0.12)), 'a 0.12 m radius arc is a cylinder'


def test_todo2_wall_no():
    wall = [(1.0, y / 10) for y in range(-10, 11)]          # 2 m wide
    assert not finder.looks_like_cylinder(wall), 'a 2 m wide cluster is a wall, not a cylinder'


def test_todo2_table_leg_no():
    leg = arc(1.0, 0.0, 0.02, n=4)                          # 4 cm wide
    assert not finder.looks_like_cylinder(leg), 'a 4 cm cluster is a table leg, not a cylinder'


def test_todo2_too_few_points():
    two = [(1.0, 0.0), (1.0, 0.2)]
    assert not finder.looks_like_cylinder(two), f'fewer than MIN_POINTS={finder.MIN_POINTS} points'


def test_todo3_centre_is_behind_the_surface():
    for cx, cy in [(1.5, 0.0), (2.0, 1.0), (-1.0, -1.2)]:
        x, y = finder.cylinder_centre(arc(cx, cy, finder.CYLINDER_RADIUS, n=9, spread_deg=100))
        err = math.dist((x, y), (cx, cy))
        assert err < 0.04, (f'true centre ({cx}, {cy}), you found ({x:.3f}, {y:.3f}): '
                            'did you push the average point one radius further away?')


def test_todo3_average_alone_is_not_enough():
    pts = arc(2.0, 0.0, finder.CYLINDER_RADIUS, n=9, spread_deg=100)
    x, _ = finder.cylinder_centre(pts)
    assert x > 1.95, 'the average of the points is ~0.1 m too close: push it out by one radius'


def test_clusters_whole_pipeline():
    scan = FakeScan(3.4).put(-60, 60, math.inf)     # open in front ...
    scan.put(5, 14, 1.40)                           # ... a 0.24 m wide object ~10 deg left
    points = finder.scan_points(scan)
    clusters = [[points[i] for i in beams] for beams in finder.find_clusters(points)]
    found = [c for c in clusters if finder.looks_like_cylinder(c)]
    assert len(found) == 1, 'polar_to_xy + looks_like_cylinder should find exactly the one object'
    x, y = finder.cylinder_centre(found[0])
    assert 1.4 < math.hypot(x, y) < 1.6 and 0 < y, 'its centre should be ~1.5 m away, a little to the left'

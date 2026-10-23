"""Lab 1 checks: TODO 1 (beam_angle_deg), TODO 2 (sector_min), TODO 3 (decide)."""
import math

import pytest
from conftest import FakeScan

from ee414_house_lab import l1_scan_reader as reader
from ee414_house_lab import l1_wander as wander


# ---- TODO 1 -----------------------------------------------------------------
def test_todo1_front_is_zero():
    assert reader.beam_angle_deg(FakeScan(), 0) == pytest.approx(0.0), 'beam 0 points straight ahead: 0 deg'


def test_todo1_left_is_plus_90():
    assert reader.beam_angle_deg(FakeScan(), 90) == pytest.approx(90.0), \
        'beam 90 points to the LEFT: +90 deg (did you convert radians to degrees?)'


def test_todo1_right_is_minus_90_not_270():
    assert reader.beam_angle_deg(FakeScan(), 270) == pytest.approx(-90.0), \
        'beam 270 points to the RIGHT: it must be -90, not 270 (wrap into -180..180)'


def test_todo1_uses_angle_min():
    scan = FakeScan(angle_min=-math.pi)          # a scanner whose beam 0 points backwards
    assert abs(reader.beam_angle_deg(scan, 0)) == pytest.approx(180.0), \
        'this scanner starts at angle_min = -pi: its beam 0 points BACKWARDS (180 deg)'
    assert reader.beam_angle_deg(scan, 180) == pytest.approx(0.0), \
        'use scan.angle_min + i * scan.angle_increment, do not assume beam 0 is the front'


# ---- TODO 2 -----------------------------------------------------------------
def test_todo2_finds_the_nearest():
    scan = FakeScan(2.0).put(-5, 5, 1.0).put(-1, 1, 0.6)
    assert reader.sector_min(scan, -20, 20) == pytest.approx(0.6), \
        'readings 2.0, 1.0 and 0.6 in the front sector: the nearest is 0.6'


def test_todo2_only_looks_inside_the_sector():
    scan = FakeScan(2.0).put(85, 95, 0.3)        # something close on the LEFT
    assert reader.sector_min(scan, -20, 20) == pytest.approx(2.0), \
        'an obstacle on the left must not appear in the front sector'
    assert reader.sector_min(scan, 60, 120) == pytest.approx(0.3), 'the obstacle at +90 deg is 0.3 m away'


def test_todo2_right_side_negative_angles():
    scan = FakeScan(2.0).put(-95, -85, 0.5)
    assert reader.sector_min(scan, -120, -60) == pytest.approx(0.5), \
        'an obstacle on the RIGHT (-90 deg) must be found in the sector -120..-60 (check TODO 1 first)'


def test_todo2_all_inf_means_clear():
    assert math.isinf(reader.sector_min(FakeScan(), -20, 20)), \
        'no valid reading in the sector: return math.inf'


def test_todo2_ignores_invalid_readings():
    scan = FakeScan(2.0)
    scan.ranges[0] = 0.0            # below range_min: not a distance
    scan.ranges[1] = float('nan')   # no reading
    scan.ranges[2] = 0.05           # below range_min (0.12)
    assert reader.sector_min(scan, -20, 20) == pytest.approx(2.0), \
        'readings that are nan, 0.0 or below range_min are NOT distances: skip them (is_valid)'


# ---- TODO 3 -----------------------------------------------------------------
INF = math.inf


def fresh():
    w = wander.Wanderer.__new__(wander.Wanderer)     # no ROS needed for decide()
    w.state, w.turn_dir = 'FORWARD', 1.0
    return w


def test_todo3_clear_means_forward():
    w = fresh()
    v, _ = w.decide(INF, INF, INF)
    assert w.state == 'FORWARD' and v == pytest.approx(wander.FORWARD_SPEED), \
        'nothing in front: stay FORWARD and drive at FORWARD_SPEED'


def test_todo3_blocked_means_turn_in_place():
    w = fresh()
    v, omega = w.decide(0.3, 2.0, 1.0)
    assert w.state == 'TURN', 'front < STOP_DIST must switch to TURN'
    assert v == pytest.approx(0.0), 'while turning, v must be 0'
    assert omega > 0, 'more room on the LEFT (2.0 > 1.0): turn left (w > 0)'


def test_todo3_turns_toward_the_open_side():
    w = fresh()
    _, omega = w.decide(0.3, 0.5, 2.5)
    assert omega < 0, 'more room on the RIGHT: turn right (w < 0)'


def test_todo3_direction_chosen_once():
    w = fresh()
    w.decide(0.3, 2.0, 1.0)                  # starts turning left
    _, omega = w.decide(0.4, 0.8, 2.5)       # now the right looks better ...
    assert omega > 0, 'keep turning the SAME way until the front is clear (choose once)'


def test_todo3_two_thresholds():
    w = fresh()
    w.decide(0.3, 2.0, 1.0)                              # TURN
    between = (wander.STOP_DIST + wander.CLEAR_DIST) / 2
    w.decide(between, 2.0, 1.0)
    assert w.state == 'TURN', 'between STOP_DIST and CLEAR_DIST: keep turning'
    w.decide(wander.CLEAR_DIST + 0.1, 2.0, 1.0)
    assert w.state == 'FORWARD', 'front > CLEAR_DIST: drive again'


def test_todo3_forward_steers_to_open_side():
    w = fresh()
    _, omega = w.decide(INF, 3.0, 1.0)
    assert omega > 0, 'driving: more room on the left -> steer left (w > 0)'
    _, omega = w.decide(INF, INF, INF)
    assert omega == pytest.approx(0.0), 'inf on both sides: count both as 3.5 -> w = 0'
    _, omega = w.decide(INF, 3.5, 0.2)
    assert abs(omega) <= wander.TURN_SPEED + 1e-9, 'limit w with clamp(w, TURN_SPEED)'

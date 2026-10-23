"""Lab 3 checks: TODO 1-2 (go to goal), TODO 3-5 (Bug)."""
import math

import pytest
from conftest import FakeScan

from ee414_house_lab import l3_bug as bug
from ee414_house_lab import l3_go_to_goal as g2g


# ---- TODO 1 -----------------------------------------------------------------
@pytest.mark.parametrize('a, expected', [
    (0.0, 0.0), (math.pi / 2, math.pi / 2), (3 * math.pi / 2, -math.pi / 2),
    (-3 * math.pi / 2, math.pi / 2), (4 * math.pi + 0.1, 0.1)])
def test_todo1_angle_wrap(a, expected):
    assert g2g.angle_wrap(a) == pytest.approx(expected), \
        f'angle_wrap({a:.3f}) must be {expected:.3f}: the same angle, between -pi and +pi'


# ---- TODO 2 -----------------------------------------------------------------
def test_todo2_straight_ahead():
    v, w = g2g.go_to_goal_command(0, 0, 0, 2.0, 0.0)
    assert v == pytest.approx(g2g.MAX_SPEED), 'far away and facing it: full speed (limited)'
    assert w == pytest.approx(0.0, abs=1e-9), 'facing the goal: no turning, w = 0'


def test_todo2_goal_on_the_left_turns_left():
    v, w = g2g.go_to_goal_command(0, 0, 0, 0.0, 2.0)
    assert w > 0, 'goal on the left: turn left (w > 0)'
    assert v == pytest.approx(0.0), 'heading error 90 deg > AIM_FIRST: turn first, v = 0'


def test_todo2_slows_down_near_goal():
    v, _ = g2g.go_to_goal_command(0, 0, 0, 0.1, 0.0)
    assert v == pytest.approx(g2g.K_DRIVE * 0.1), 'near the goal: v = K_DRIVE * distance'


def test_todo2_wraps_the_error():
    # Robot faces 170 deg, goal is at -170 deg: turn LEFT a little, not right a lot.
    yaw = math.radians(170)
    gx, gy = math.cos(math.radians(-170)), math.sin(math.radians(-170))
    _, w = g2g.go_to_goal_command(0, 0, yaw, gx, gy)
    assert w > 0, 'heading error must be wrapped with angle_wrap (it is +20 deg, not -340 deg)'
    assert w == pytest.approx(g2g.K_TURN * math.radians(20), rel=1e-3), \
        'w must be K_TURN * (wrapped heading error) = K_TURN * 20 deg in radians'


def test_todo2_turn_is_limited():
    _, w = g2g.go_to_goal_command(0, 0, 0, -1.0, 0.01)
    assert abs(w) <= g2g.MAX_TURN + 1e-9, 'limit w to MAX_TURN with clamp'


# ---- TODO 3 -----------------------------------------------------------------
def test_todo3_clear_when_nothing_there():
    assert bug.goal_direction_clear(FakeScan(), 0, 0, 0, 3.0, 0.0), 'nothing anywhere: the way is clear'


def test_todo3_blocked_ahead():
    scan = FakeScan().put(-10, 10, 0.5)
    assert not bug.goal_direction_clear(scan, 0, 0, 0, 3.0, 0.0), \
        'an obstacle 0.5 m straight ahead, goal straight ahead: NOT clear'


def test_todo3_looks_toward_the_goal_not_ahead():
    scan = FakeScan().put(-10, 10, 0.5)      # blocked straight AHEAD ...
    assert bug.goal_direction_clear(scan, 0, 0, 0, 0.0, 3.0), \
        'the goal is to the LEFT (90 deg) and that way is free: clear'
    scan = FakeScan().put(80, 100, 0.5)      # ... blocked to the left
    assert not bug.goal_direction_clear(scan, 0, 0, 0, 0.0, 3.0), \
        'the goal is to the LEFT and an obstacle is there: NOT clear'


def test_todo3_uses_robot_heading():
    scan = FakeScan().put(-10, 10, 0.5)      # blocked ahead of the robot
    # Robot faces +y (yaw 90 deg), goal is at +y: the goal is AHEAD, and ahead is blocked.
    assert not bug.goal_direction_clear(scan, 0, 0, math.pi / 2, 0.0, 3.0), \
        'subtract the robot yaw: the goal direction must be measured from where the robot faces'


def test_todo3_obstacle_behind_goal_does_not_matter():
    scan = FakeScan().put(-10, 10, 0.8)
    assert bug.goal_direction_clear(scan, 0, 0, 0, 0.5, 0.0), \
        'the goal is 0.5 m away, the obstacle 0.8 m: it is behind the goal, so the way is clear'


# ---- TODO 4 -----------------------------------------------------------------
def test_todo4_example():
    assert bug.distance_to_mline(0, 0, 4, 0, 2, 1) == pytest.approx(1.0), \
        'start (0,0), goal (4,0), point (2,1): the distance is 1'


def test_todo4_on_the_line():
    assert bug.distance_to_mline(0, 0, 3, 3, 1, 1) == pytest.approx(0.0, abs=1e-9), \
        'the point (1,1) is ON the line from (0,0) to (3,3): distance 0'


def test_todo4_never_negative():
    assert bug.distance_to_mline(0, 0, 4, 0, 2, -1) == pytest.approx(1.0), \
        'a distance is never negative: use abs()'


def test_todo4_any_start():
    assert bug.distance_to_mline(1, 1, 1, 5, 4, 3) == pytest.approx(3.0), \
        'start (1,1), goal (1,5), point (4,3): the distance is 3 (does your formula use the start?)'


# ---- TODO 5 -----------------------------------------------------------------
def robot(algorithm, x=0.0, y=0.0):
    b = bug.Bug.__new__(bug.Bug)
    b.gx, b.gy, b.algorithm = 3.0, 0.0, algorithm
    b.state, b.sx, b.sy = 'GO_TO_GOAL', 0.0, 0.0
    b.hit_x = b.hit_y = None
    b.hit_dist = math.inf
    b.x, b.y, b.yaw = x, y, 0.0
    b.scan = FakeScan()
    return b


def test_todo5_hit():
    b = robot('bug2', 1.0, 0.0)
    b.switch(0.3, 2.0)
    assert b.state == 'FOLLOW_WALL', 'front < HIT_DIST: switch to FOLLOW_WALL'
    assert (b.hit_x, b.hit_y) == (1.0, 0.0) and b.hit_dist == pytest.approx(2.0), \
        'remember the hit point and the goal distance there'


def test_todo5_no_hit_when_clear():
    b = robot('bug2')
    b.switch(2.0, 3.0)
    assert b.state == 'GO_TO_GOAL', 'front is clear (2 m > HIT_DIST): stay in GO_TO_GOAL'


def test_todo5b_bug2_leaves_on_mline_closer():
    b = robot('bug2', 1.0, 0.0)
    b.switch(0.3, 2.0)                       # hit at (1, 0), 2 m from the goal
    b.x, b.y = 1.6, 0.03                     # back on the m-line, 1.4 m from the goal
    b.switch(1.0, 1.4)
    assert b.state == 'GO_TO_GOAL', 'Bug 2: on the m-line and closer than at the hit: leave'


def test_todo5b_bug2_stays_off_mline():
    b = robot('bug2', 1.0, 0.0)
    b.switch(0.3, 2.0)
    b.x, b.y = 1.5, 0.6                      # beside the obstacle, off the m-line
    b.switch(1.0, 1.6)
    assert b.state == 'FOLLOW_WALL', 'Bug 2: not on the m-line: keep following the wall'


def test_todo5b_bug2_not_closer_stays():
    b = robot('bug2', 1.0, 0.0)
    b.switch(0.3, 2.0)
    b.x, b.y = 0.5, 0.02                     # on the m-line but FARTHER than the hit
    b.switch(1.0, 2.5)
    assert b.state == 'FOLLOW_WALL', 'Bug 2: on the m-line but not closer: keep following'


def test_todo5_ignores_hit_point_itself():
    b = robot('bug0', 1.0, 0.0)
    b.switch(0.3, 2.0)
    b.x = 1.1                                # only 10 cm from the hit point
    b.switch(1.0, 1.9)
    assert b.state == 'FOLLOW_WALL', 'within 0.3 m of the hit point: do not leave yet'


def test_todo5_bug0_leaves_when_clear():
    b = robot('bug0', 1.0, 0.0)
    b.switch(0.3, 2.0)
    b.x, b.y = 1.2, 0.6                      # moved along the wall; nothing toward the goal
    b.switch(1.0, 1.9)
    assert b.state == 'GO_TO_GOAL', 'Bug 0: the way to the goal is clear: leave'

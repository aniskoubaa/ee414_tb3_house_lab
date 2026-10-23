# EE 414 House Lab: Lab 3 report

**Name:** _[answer]_
**Student ID:** _[answer]_
**Date:** _[answer]_

Replace every `_[answer]_`. Short answers are fine: one to three sentences.

---

## Part A: go to a goal

**A0.** `./lab check 3`: did TODO 1 and TODO 2 pass? _[answer]_

**A1.** Monitor summary for the goal (1.0, 1.0):

```
_[answer]_
```

The straight-line distance was 1.41 m. How much farther did the robot drive, and why?
_[answer]_

**A2.** Goal (3.0, 0.0) with go-to-goal only. Copy the monitor summary:

```
_[answer]_
```

What really happened? Did your program print `GOAL reached`? If yes, why did it believe it had
arrived (look at `odom error at end`)? Why can this controller never reach this goal?
_[answer]_

**A3.** Why must the heading error be wrapped? Give a numeric example where it matters.
_[answer]_

---

## Part B: Bug 0

**B0.** `./lab check 3`: did TODO 3 and TODO 5 (Bug 0) pass? _[answer]_

**B1.** The `HIT` / `LEAVE` lines and the monitor summary:

```
_[answer]_
```

What did the robot do around the box (use the path picture)? _[answer]_

---

## Part C: Bug 2

**C0.** `./lab check 3`: does everything pass? _[answer]_

**C1.** The `HIT` / `LEAVE` lines and the monitor summary:

```
_[answer]_
```

Did Bug 2 reach the goal with 0 bumps? _[answer]_

**C2.** In your run, where was the robot when Bug 2 left the wall? Why there and not earlier?
_[answer]_

---

## Part D: comparison

| Run | reached? | time (s) | distance driven (m) | min clearance (m) | bumps |
|---|---|---|---|---|---|
| go-to-goal (3, 0) | _[answer]_ | _[answer]_ | _[answer]_ | _[answer]_ | _[answer]_ |
| Bug 0 | _[answer]_ | _[answer]_ | _[answer]_ | _[answer]_ | _[answer]_ |
| Bug 2 | _[answer]_ | _[answer]_ | _[answer]_ | _[answer]_ | _[answer]_ |

**D1.** Which one drove the shorter path here, and why? _[answer]_

**D2.** Draw an obstacle where Bug 0 loops for ever but Bug 2 succeeds. Save it as
`submission/lab3/bug0_trap.png` and explain it in two sentences. _[answer]_

**D3 (bonus).** Cylinder position (odom), your goal, the final robot-to-cylinder distance, and
the monitor's odom error: _[answer]_

---

## Think

**T1.** The goals are in the **odom** frame. If odometry drifted by 30 cm during the run, where
would the robot stop? How would the monitor show it? _[answer]_

**T2.** Bug algorithms need no map. What do they cost in exchange, compared with a planner that
has a map (Week 11)? _[answer]_

# EE 414 House Lab: Lab 1 report

**Name:** _[answer]_
**Student ID:** _[answer]_
**Date:** _[answer]_

Replace every `_[answer]_`. Short answers are fine: one to three sentences.

---

## Part A: the robot's topics

**A3.** Fill in from the commands in the guide:

| Question | Your answer |
|---|---|
| Five topics from `ros2 topic list` | _[answer]_ |
| Type of `/cmd_vel` | _[answer]_ |
| Rate of `/scan` (Hz) | _[answer]_ |
| `angle_min`, `angle_increment` (rad) | _[answer]_ |
| `range_min`, `range_max` (m) | _[answer]_ |
| How many beams per scan, and how many degrees between beams? | _[answer]_ |

**A4.** About `easy_robot.py`:

1. Topic it publishes, and the message type: _[answer]_
2. Topics it subscribes to: _[answer]_
3. How many times per second `step()` is called: _[answer]_
4. Why `stop()` sends the command 5 times: _[answer]_

---

## Part B: reading the laser

**B1.** `./lab check 1`: did TODO 1 and TODO 2 pass? _[answer]_

**B2.** One line of `l1_scan_reader` output at each place:

| Place | FRONT | LEFT | RIGHT | BACK | nearest (m, deg) | beams with inf |
|---|---|---|---|---|---|---|
| start | _[answer]_ | _[answer]_ | _[answer]_ | _[answer]_ | _[answer]_ | _[answer]_ |
| at the table | _[answer]_ | _[answer]_ | _[answer]_ | _[answer]_ | _[answer]_ | _[answer]_ |
| hallway | _[answer]_ | _[answer]_ | _[answer]_ | _[answer]_ | _[answer]_ | _[answer]_ |

**B3.** At the table, what did the laser "see" of the table, and why? _[answer]_

**B4.** At the start, many beams read `inf`. Is there really nothing there? What does `inf` mean
for this sensor? _[answer]_

**B5.** Why does `sector_min` return the **minimum** of the sector and not the **average**?
_[answer]_

---

## Part C: the wanderer

**C1.** `./lab check 1`: did all three TODOs pass? _[answer]_

**C2.** Copy the monitor summary of your 3-minute run (`submission/lab1/lab1_run_*.txt`):

```
_[answer]_
```

Did you reach the checkpoint (3 min, 0 bumps, 2 or more rooms)? _[answer]_

**C3.** Look at `lab1_run_*.png`. Which line is where the robot really went, and which is what
`/odom` believes? What was your `odom error at end`? What makes the two lines separate (if
yours did not, look at a D-run where the robot bumped)? _[answer]_

---

## Part D: experiments

| Run | Change | min clearance (m) | close calls | bumps | rooms | distance (m) |
|---|---|---|---|---|---|---|
| C2 | default (0.45 / 0.65) | _[answer]_ | _[answer]_ | _[answer]_ | _[answer]_ | _[answer]_ |
| D1 | 0.25 / 0.35 | _[answer]_ | _[answer]_ | _[answer]_ | _[answer]_ | _[answer]_ |
| D2 | 0.70 / 0.90 | _[answer]_ | _[answer]_ | _[answer]_ | _[answer]_ | _[answer]_ |
| D3 | CLEAR_DIST = STOP_DIST | _[answer]_ | _[answer]_ | _[answer]_ | _[answer]_ | _[answer]_ |

**D1.** What changed when the thresholds were small, and why? _[answer]_

**D2.** What changed when the thresholds were large, and why? _[answer]_

**D3.** With one threshold, what did the robot do while turning? Use the terminal output. Why do
two thresholds fix it? _[answer]_

---

## Think

**T1.** The monitor may count a **bump** while `min clearance` stays above 0.3 m: the robot
pushes against something the laser never saw. Where in the house could this happen? (Hint: the
laser sees one horizontal slice, 17 cm above the floor. Look at the big room in Gazebo.)
_[answer]_

**T2.** Your wanderer has no map and no memory. Does it visit every room if you give it enough
time? What would it need to explore the house on purpose? _[answer]_

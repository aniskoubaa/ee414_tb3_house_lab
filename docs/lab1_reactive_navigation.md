# Lab 1: the laser scanner, and a robot that wanders without hitting anything

**Goal:** by the end of this lab, your TurtleBot3 drives around the house for 3 minutes on its
own, through several rooms, without touching anything.

**You will write:** three small functions (TODO 1, 2, 3).
**You will submit:** `submission/lab1/REPORT.md`, your monitor results, and your code
(`./lab submit 1 <ID>`), **before Lecture 2**.

| Part | What | Time |
|---|---|---|
| A | Start the robot and look at its topics | 20 min |
| B | Read the laser: TODO 1, TODO 2 | 30 min |
| C | Wander: TODO 3, then run and measure | 40 min |
| D | Tune, experiment, and answer the questions | 30 min |

---

## Part A: start the robot (20 min)

### A1. Start the house

```bash
cd ~/ee414_tb3_house_lab
./lab sim
```

Gazebo opens with the house. The small black robot is in the **living room**, facing the
**orange box**. You will also see three coloured cylinders (red, green, blue). Lab 2 uses them.

> **First start is slow** (up to a minute). If your PC is weak, use `./lab sim nogui`: the
> simulation runs without the 3D window, and everything else works the same.

### A2. Drive it yourself

Open a **second terminal** and run:

```bash
./lab teleop
```

Click on this terminal, then press keys: `w` faster, `x` slower (or backwards), `a` / `d` turn,
`s` **stop**. Each key press changes the speed a little; the robot keeps going until you change
it again. Drive into the hallway and back. Then press `s`.

### A3. Look at the topics

Open a **third terminal**. Run each command and **write the answers in your report (Part A)**:

```bash
ros2 topic list                  # which topics exist?
ros2 topic type /cmd_vel         # which message type drives the robot?
ros2 topic hz /scan              # how many scans per second? (Ctrl-C to stop)
ros2 topic echo /scan --once     # one scan: look at the first lines
```

From the scan, write down `angle_min`, `angle_increment`, `range_min` and `range_max`.

> **The silent trap of Week 4.** On ROS 2 Jazzy the robot listens for `TwistStamped`, not
> `Twist`. If you publish a `Twist`, nothing happens and **no error is shown**. All the lab
> programs send `TwistStamped` for you.

### A4. Read `easy_robot.py`

Open `ee414_house_lab/ee414_house_lab/easy_robot.py`. It is the base of every program you will
run. You do not change it, but read it: it is exactly the node you wrote in Weeks 3 and 4. Answer
in your report:

1. Which topic does it **publish**, with which message type?
2. Which topics does it **subscribe** to?
3. How many times per second is `step()` called?
4. Why does `stop()` send the stop command 5 times?

---

## Part B: read the laser (30 min)

### What a LaserScan is

```
                    90° (LEFT)
                        |
     180° (BACK) ---- robot ----> 0° (FRONT)
                        |
                  -90° (RIGHT)
```

`scan.ranges` is a list of **360 numbers**: `ranges[i]` is the distance measured by beam `i`.
Beam `i` points at the angle

```
angle_i = scan.angle_min + i * scan.angle_increment        (radians)
```

Not every number is a distance:

| Value | Meaning |
|---|---|
| `inf` | nothing was hit within `range_max` (3.5 m): **free space** |
| `nan` | no usable reading |
| below `range_min` (0.12 m) | too close for the sensor to measure |

A reading is **valid** only if it is a finite number between `range_min` and `range_max`.

### B1. TODO 1 and TODO 2

Open `ee414_house_lab/ee414_house_lab/l1_scan_reader.py`. Complete:

- **TODO 1** `beam_angle_deg(scan, i)`: the angle of beam `i` in degrees, between −180 and +180.
- **TODO 2** `sector_min(scan, from_deg, to_deg)`: the nearest **valid** reading between two
  angles, or `math.inf` if there is none.

The docstring of each function gives the steps. Then test **without the simulator**:

```bash
./lab check 1
```

```
  PASS  TODO 1   4/4 checks
  PASS  TODO 2   5/5 checks
  FAIL  TODO 3   0/6 checks -- not written yet (TODO 3: decide)     <- that is Part C
```

Fix any FAIL line about TODO 1 or 2 before you continue. Each line says what went wrong.

### B2. Look around with your own code

With `./lab sim` and `./lab teleop` running:

```bash
./lab run l1_scan_reader
```

Once per second it prints the nearest obstacle FRONT, LEFT, RIGHT and BACK, the nearest point
overall, and how many beams see nothing (`inf`). Drive with teleop to the **three places** below.
At each one, stop and copy one line into the table in your report:

1. the start position (just restart `./lab sim` to go back there),
2. **under or next to the table** in the living room (the brown table with 4 legs),
3. in the hallway, between the two long walls.

> At place 2, look at the robot in Gazebo, then at the numbers. **What does the laser see of the
> table?** The laser is 17 cm above the floor: it sees a horizontal slice of the world at that
> height and nothing else. Your report asks about this.

---

## Part C: wander without hitting anything (40 min)

### The idea: sense, decide, act, 10 times per second

```
SENSE   front, left, right = three sector_min values      (your TODO 2)
DECIDE  choose (v, w)                                      (your TODO 3)
ACT     self.drive(v, w)
```

DECIDE is a **state machine** with two states:

```
                  front < STOP_DIST
     +---------+ ------------------>  +------+
     | FORWARD |                      | TURN |
     +---------+ <------------------  +------+
                  front > CLEAR_DIST
```

- **FORWARD**: drive at `FORWARD_SPEED` and steer a little toward the side with more room.
- **TURN**: stand still and rotate until the front is clear, **always in the same direction**.

Two details make it work. Both are in your report.

1. **Two thresholds** (`STOP_DIST = 0.45` < `CLEAR_DIST = 0.65`). The robot starts turning at
   0.45 m but does not drive again until the front is clear beyond 0.65 m. A home thermostat
   does the same thing (heating on at 20 °C, off at 22 °C) so it does not switch on and off every
   second.
2. **The turn direction is chosen once**, when the turn starts. If you choose it again every
   0.1 s, a wall straight ahead makes the robot turn left, right, left, right, for ever.

### C1. TODO 3

Open `l1_wander.py` and complete `decide(front, left, right)`. Follow the steps 3a and 3b in the
docstring. Then:

```bash
./lab check 1          # all three TODOs must PASS
```

### C2. Run it and measure it

Restart the simulator so the robot starts from the same place. **Close teleop**: two programs
sending speeds to the same robot fight each other.

```bash
./lab sim                  # terminal 1 (restart it)
./lab monitor 1            # terminal 2: records for 3 minutes, then saves
./lab run l1_wander        # terminal 3: start it right after the monitor
```

The monitor prints a line when the robot reaches a new room, and warns you about every
**close call** (something nearer than 0.20 m) and every **bump** (the robot was told to drive but
did not really move). After 3 minutes it prints a summary and saves three files in
`submission/lab1/`:

| File | Content |
|---|---|
| `lab1_run_<time>.txt` | the summary: copy these numbers into your report |
| `lab1_run_<time>.csv` | the whole run, one line every 0.2 s |
| `lab1_run_<time>.png` | the path, drawn on the floor plan |

Then stop the wanderer with Ctrl-C.

**Checkpoint C:** 3 minutes, **0 bumps**, at least **2 rooms** reached. Show the summary to the
instructor.

> **Two paths in the picture?** The purple line is where the robot **really** went (Gazebo knows).
> The grey dashed line is where `/odom` **thinks** it went: odometry only counts wheel turns.
> In a clean run the two lines lie almost on top of each other (a few centimetres apart after
> 30 m). When the robot bumps into something, or its wheels slip, `/odom` does not notice, and
> from that moment the two lines separate. This is **odometry drift**, and Weeks 9–10 deal
> with it. The summary line `odom error at end` measures it.

---

## Part D: tune and experiment (30 min)

For each experiment: change the number at the top of `l1_wander.py`, restart `./lab sim`, run
`./lab monitor 1 --minutes 2` and the wanderer, and copy the summary into the table in your report.
**Put the number back afterwards.**

| Run | Change | What to look for |
|---|---|---|
| D1 | `STOP_DIST = 0.25`, `CLEAR_DIST = 0.35` | min clearance, close calls, bumps |
| D2 | `STOP_DIST = 0.70`, `CLEAR_DIST = 0.90` | rooms reached: can it still pass through doors? |
| D3 | `CLEAR_DIST = STOP_DIST` (one threshold) | watch the terminal: how does TURN behave? |

---

## What you submit (before Lecture 2)

1. Fill in `submission/lab1/REPORT.md`. Replace every `_[answer]_`.
2. Make sure `submission/lab1/` has your monitor files from C2 and D1–D3.
3. Run `./lab submit 1 <your student ID>`, and upload `~/EE414_lab1_<ID>.zip`.

### Grading (10 points)

| Points | For |
|---|---|
| 2 | Part A answers |
| 2 | TODO 1 and TODO 2 pass, and the scan table in B2 is filled in and explained |
| 3 | TODO 3 passes, and the C2 run reaches the checkpoint (3 min, 0 bumps, 2+ rooms) |
| 2 | Part D table and the explanation of each result |
| 1 | The two "think" questions |

# Lab 2: where is that object? The laser and TF2

**Goal:** your robot finds the three cylinders in the living room with its laser. It puts each
one on the map (in RViz) and publishes it as a TF frame (`object_0`, `object_1`, ...). While
the robot drives, the markers must **stay exactly where the cylinders are**.

**You will write:** four small functions (TODO 1–4) in `l2_object_finder.py`.
**You will submit:** `submission/lab2/REPORT.md`, your `l2_check` results, an RViz screenshot,
and your code (`./lab submit 2 <ID>`), **before Lecture 3**.

| Part | What | Time |
|---|---|---|
| A | Explore the TF tree of the robot | 20 min |
| B | From laser readings to cylinders: TODO 1, 2, 3 | 35 min |
| C | From the robot's frame to the map: TODO 4 (TF2) | 30 min |
| D | Compare with the truth: the `world → odom` transform | 25 min |

---

## Why this lab matters

The laser says "something at 1.8 m, 30° to my left". That is a position **in the robot's frame**,
and the robot moves. One second later the same cylinder is at a different distance and angle,
but the cylinder has not moved. To put objects on a map, to remember them, or to drive back to
them (Lab 3), you must express them in a frame that does **not** move with the robot. That is
what TF2 is for.

```
odom            the frame where the robot started. It does not move.
 └─ base_footprint   the robot, on the floor        (published by Gazebo's wheel odometry)
     └─ base_link     the robot body                (robot_state_publisher)
         └─ base_scan  the laser, 17 cm up          (robot_state_publisher)
```

---

## Part A: explore the TF tree (20 min)

Start the simulator **with RViz**:

```bash
./lab sim rviz
```

In RViz you see the robot, the red laser points, and the TF frames as small axes (red = x,
green = y). The **fixed frame** (top left, Global Options) is `odom`.

In a second terminal:

```bash
ros2 run tf2_tools view_frames          # writes frames_<date>.pdf in this folder
```

Open the PDF. **A1** (report): draw or copy the tree, and for every arrow write who publishes it.

```bash
ros2 run tf2_ros tf2_echo base_link base_scan
```

**A2:** what is the translation? Where is the laser on the robot, and how high?
(Ctrl-C to stop.)

```bash
ros2 run tf2_ros tf2_echo odom base_footprint
```

Now drive with `./lab teleop` in a third terminal while watching `tf2_echo`. **A3:** which numbers
change when you drive forward? Which ones change when you turn? Why does `base_link → base_scan`
never change?

---

## Part B: from laser readings to cylinders (35 min)

Open `ee414_house_lab/ee414_house_lab/l2_object_finder.py`. The method has four steps:

```
 1. POINTS     each valid reading (r, angle) -> a point (x, y) in base_scan      TODO 1
 2. CLUSTERS   neighbouring points closer than 10 cm form one object             (written for you)
 3. CYLINDER?  keep clusters 0.12-0.36 m wide that stand alone; find the centre  TODO 2, TODO 3
 4. TF2        the centre in base_scan -> the centre in odom                     TODO 4 (Part C)
```

### TODO 1: `polar_to_xy(r, angle)`

The laser frame `base_scan`: **x forward, y left**. `x = r cos(angle)`, `y = r sin(angle)`.

### TODO 2: `looks_like_cylinder(cluster)`

What does each object look like in the scan?

| Object | What the laser sees | Width of the cluster |
|---|---|---|
| a cylinder, radius 0.12 m | the front half of a circle | ≈ 0.20–0.24 m |
| a table leg | a tiny arc | ≈ 0.03 m |
| a wall | a long straight line | metres |

So keep a cluster if it has at least `MIN_POINTS` points and its width (first point to last
point) is between `MIN_WIDTH` and `MAX_WIDTH`.

Width alone is not quite enough. A short piece of wall, seen between two door frames, can also be
20 cm wide. One more rule is already written for you, `stands_alone`: a cylinder stands **in
front of** the background, so the beams just beside it see something **farther away**. On a
recorded test drive this rule removed every false detection. Read it, because the report asks
about it (B2).

### TODO 3: `cylinder_centre(cluster)`: the one idea to think about

The **average** of the points is **not** the centre of the cylinder. The laser sees only the
side facing the robot, so all the points lie on the surface, about one radius too close:

```
   robot o - - - - - - - - - - ->  ( . )
                                   ^  ^
                     the points    |  the true centre is one radius further
```

So you push the average point **one radius further** along the same direction.
**B1 (report):** explain, in your own words or with a sketch, why the push is along the line
from the robot to the point, and why it is one radius.

Test TODO 1–3 without the simulator:

```bash
./lab check 2
```

---

## Part C: from the robot's frame to the map with TF2 (30 min)

### TODO 4: `to_odom(x, y, stamp)`

Three lines, exactly as in Lecture 7B:

```python
t = self.tf_buffer.lookup_transform('odom', 'base_scan', stamp, timeout=Duration(seconds=0.2))
q = do_transform_point(p, t)
return q.point.x, q.point.y
```

The one line to remember from Week 7:

```
lookup_transform(TARGET, SOURCE, time)  ->  the transform that takes SOURCE coordinates to TARGET
```

We have the point **in** `base_scan` and want it **in** `odom`, so `odom` is the target.

`stamp` is the time **the scan was taken**. The robot may have moved since then, and TF2 gives
the robot's position **at that moment**. For the first second TF2 may answer "extrapolation into
the future" or "frame does not exist". That is normal, and the code skips that scan.

### C1. Run it

```bash
./lab sim rviz                      # terminal 1 (RViz shows /objects)
./lab run l2_object_finder          # terminal 2
./lab teleop                        # terminal 3: drive SLOWLY (2-3 presses of w)
```

Drive around the living room. Turn on the spot near each cylinder. When a cylinder has been seen
5 times, the finder prints `NEW OBJECT object_N` and a yellow cylinder with a label appears in
RViz.

**Checkpoint C:** all three cylinders are found, and while you drive and turn, **the yellow
markers stay on the cylinders**. Take a screenshot of RViz and save it as
`submission/lab2/rviz.png`.

### C2. Break it on purpose (5 min)

In `to_odom`, **swap** the two frame names: `lookup_transform('base_scan', 'odom', ...)`. Run the
finder again and drive. **C2 (report):** what do the markers do? Why? Then swap them back.

> Ctrl-C the finder: it prints every object it found, in the odom frame. Keep this list for Part D.

---

## Part D: compare with the truth (25 min)

Gazebo put the cylinders at known positions in the **world** frame:

| Cylinder | world x | world y |
|---|---|---|
| red | −3.00 | 3.60 |
| green | −1.00 | 2.00 |
| blue | −4.30 | 2.40 |

Start the finder again (`./lab run l2_object_finder`; keep the simulator running) and drive
slowly around the living room with teleop, as in C1, until it has found all three cylinders.
(The finder ignores anything farther than 3 m, so from the start position it sees only the blue
one.) Then, in another terminal:

```bash
ros2 run ee414_house_lab l2_check
```

It compares your `object_N` frames with the true positions. The first time, the errors are
about **4 m**. **D1 (report):** why? (Hint: where is the origin of `odom`, and where is the origin
of `world`?)

The robot starts at world position **(−4.0, 0.5)**, facing +x. So `odom` sits at (−4.0, 0.5) in
`world`, with no rotation. Tell TF2 by publishing a **static transform** (Lecture 7B), in a new
terminal, and leave it running:

```bash
ros2 run tf2_ros static_transform_publisher --x -4.0 --y 0.5 --frame-id world --child-frame-id odom
```

Run `ros2 run ee414_house_lab l2_check` again. Now TF2 can chain
`world → odom → object_N`.

**Checkpoint D:** every cylinder within **10 cm** of the truth. Both `l2_check` results are saved
in `submission/lab2/`.

> **Looking ahead (Weeks 9–10).** Here we could write `world → odom` by hand because we know where
> the robot started and odometry barely drifts in 2 minutes. A real robot does not know either.
> A localization system (AMCL, SLAM) estimates the frame `map` and keeps correcting `map → odom`
> as odometry drifts. That is the same tree you just built.

---

## What you submit (before Lecture 3)

1. `submission/lab2/REPORT.md`, with every `_[answer]_` replaced.
2. In `submission/lab2/`: both `lab2_check_*.txt` files (without and with `world → odom`) and
   `rviz.png`.
3. `./lab submit 2 <your student ID>`, then upload `~/EE414_lab2_<ID>.zip`.

### Grading (10 points)

| Points | For |
|---|---|
| 2 | Part A: the TF tree with its publishers, A2 and A3 |
| 3 | TODO 1–3 pass, and B1 is explained |
| 2 | TODO 4 works: the RViz screenshot shows the markers on the cylinders, and C2 is explained |
| 2 | Part D: both check results, D1 explained, every error < 10 cm |
| 1 | The "think" questions |

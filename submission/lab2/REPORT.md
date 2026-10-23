# EE 414 House Lab: Lab 2 report

**Name:** _[answer]_
**Student ID:** _[answer]_
**Date:** _[answer]_

Replace every `_[answer]_`. Short answers are fine: one to three sentences.

---

## Part A: the TF tree

**A1.** The tree from `view_frames`. For every arrow (parent → child), who publishes it?

| Parent → child | Published by | Static or moving? |
|---|---|---|
| _[answer]_ | _[answer]_ | _[answer]_ |
| _[answer]_ | _[answer]_ | _[answer]_ |
| _[answer]_ | _[answer]_ | _[answer]_ |
| _[answer]_ | _[answer]_ | _[answer]_ |

**A2.** `tf2_echo base_link base_scan`: translation = _[answer]_.
Where is the laser on the robot, and how high above the floor? _[answer]_

**A3.** `tf2_echo odom base_footprint` while driving: which numbers change when you drive forward,
and which when you turn? Why does `base_link → base_scan` never change? _[answer]_

---

## Part B: laser readings to cylinders

**B0.** `./lab check 2`: did TODO 1–3 pass? _[answer]_

**B1.** Why must the average of the points be pushed **one radius further, along the line from
the robot**? A sketch (photo) is welcome: save it as `submission/lab2/sketch.png`. _[answer]_

**B2.** Why are the table legs not detected as cylinders? Why are the walls not? What does
`stands_alone` add, and what would be detected without it? _[answer]_

---

## Part C: TF2

**C1.** The objects found (Ctrl-C output of `l2_object_finder`):

```
_[answer]_
```

Screenshot saved as `submission/lab2/rviz.png`? _[answer]_

**C2.** With the frames swapped in `lookup_transform`, what did the markers do while you drove?
Why? _[answer]_

**C3.** `to_odom` uses the **time the scan was taken** (`stamp`), not "now". What would go wrong
with "now" while the robot is turning fast? _[answer]_

---

## Part D: comparison with the truth

**D1.** Copy the `l2_check` table **without** `world → odom`:

```
_[answer]_
```

Why are the errors so large? _[answer]_

**D2.** The command you used to publish `world → odom`: _[answer]_

**D3.** Copy the `l2_check` table **with** `world → odom`:

```
_[answer]_
```

Are all objects within 10 cm? If not, what could cause the error? _[answer]_

---

## Think

**T1.** We knew `world → odom` because we knew where the robot started. A real robot in a real
house does not. What would you need to publish that transform? Which frame does ROS use for it?
_[answer]_

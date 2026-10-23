# Troubleshooting

Start with `./lab doctor`. It checks everything and tells you how to fix each FAIL line.

| Symptom | Cause | Fix |
|---|---|---|
| `./lab sim`: the Gazebo window is black, or never opens | graphics driver, WSL2, Wayland | `./lab stop`, then `./lab sim nogui` and watch in `./lab rviz`. Everything else works the same |
| The first `./lab sim` takes a minute | Gazebo loads the house the first time | wait; later starts are faster |
| The robot does not move with teleop | you clicked another window | click the **teleop terminal**, then press keys |
| The robot does not move with your program | teleop is still running and sends 0 | close teleop (Ctrl-C) |
| Your program prints nothing | the simulator is not running | start `./lab sim` first, and wait until the robot is visible |
| `./lab check 1` says `not written yet (TODO 2 ...)` | that TODO still has `raise NotImplementedError` | write the function, and delete the `raise` line |
| `./lab check` says `could not run at all` | a Python syntax error in your file | run `python3 -m py_compile ee414_house_lab/ee414_house_lab/l1_wander.py` and read the line number |
| `KeyError: 'TURTLEBOT3_MODEL'` | this terminal was opened before `./install.sh` | open a new terminal |
| `Package 'ee414_house_lab' not found` | the lab is not built, or old terminal | `./lab build`, then open a new terminal |
| `No module named 'em'` or `rclpy` errors | conda is active | `conda deactivate` |
| Two robots, or someone else's robot moves | old programs still running | `./lab stop`, then start again |
| TF warnings at the start of `l2_object_finder` | TF is not ready during the first second | normal; it keeps going |
| `l2_check` errors of about 4 m | no `world -> odom` transform yet | that is Lab 2, Part D: publish it |
| The robot stays on the spot, turning | it is in TURN state and the front never clears (a corner) | normal for a few seconds; if it lasts, check your two thresholds |
| The monitor saves nothing | the simulator was not running when it started | start `./lab sim` first, then the monitor |

## Start again from a clean state

```bash
./lab stop
./lab sim
```

Restarting the simulator puts the robot back at the start and resets `/odom` to (0, 0).

## Still stuck?

Copy the full output of `./lab doctor` and the error message, and bring them to the lab session
or post them in the course forum.

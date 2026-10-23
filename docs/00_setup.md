# Setup: install once, before Lab 1

You need a computer with **Ubuntu 24.04**, about **10 GB free disk**, and **8 GB RAM** or more.
The installation downloads about 3 GB, so do it at home before the first lab session.

## Option 1: Ubuntu 24.04 installed on your laptop (best)

```bash
sudo apt install -y git
cd ~
git clone https://github.com/aniskoubaa/ee414_tb3_house_lab.git
cd ee414_tb3_house_lab
./install.sh
```

## Option 2: Windows 11 with WSL2

WSL2 runs Ubuntu inside Windows, and Gazebo's window works through WSLg.

1. Open **PowerShell as administrator** and run: `wsl --install -d Ubuntu-24.04`. Restart when asked.
2. Open **Ubuntu 24.04** from the Start menu, and choose a user name and password.
3. In that Ubuntu window, run the commands of Option 1.

If the Gazebo window stays black in WSL2, use `./lab sim nogui`. Everything works, and you watch
the robot in RViz (`./lab rviz`) instead.

## Option 3: the lab PCs

The lab PCs are already installed. Clone the repository into your home folder and run
`./install.sh` anyway: it only builds the lab (one minute) and checks it.

## What `./install.sh` does

| Step | What |
|---|---|
| 1 | asks for your password once |
| 2 | adds the official ROS 2 package repository |
| 3 | installs ROS 2 Jazzy, Gazebo Harmonic, TurtleBot3, TF2 tools, colcon, pytest, matplotlib |
| 4 | builds the lab in `~/ee414_ws` (the repository is linked there, not copied) |
| 5 | adds **one line** to `~/.bashrc` so every new terminal is ready |
| 6 | runs `./check_setup.sh` |

`check_setup.sh` does more than look for files. It **starts the simulator, drives the robot
forward, and checks that it moved**. The installation is ready when it ends with:

```
  ALL GOOD.  Start the lab with:  ./lab sim
```

Then **close the terminal and open a new one**, so the new `~/.bashrc` line takes effect.

## Check again at any time

```bash
./lab doctor              # the same check
./lab doctor --quick      # without the simulator test (5 seconds)
```

## If you use conda (Anaconda, Miniconda)

Conda's Python is not the Python that ROS 2 was built for. Before the lab, run
`conda deactivate` until the prompt shows no `(base)`. To stop conda from turning itself on in
every new terminal: `conda config --set auto_activate_base false`.

## What the line in `~/.bashrc` does

```bash
source ~/ee414_tb3_house_lab/scripts/lab_env.sh   # EE 414 House Lab
```

- loads ROS 2 Jazzy and the lab workspace,
- sets `TURTLEBOT3_MODEL=burger`,
- keeps ROS 2 and Gazebo traffic **inside your computer**, so on a shared network you never
  drive your neighbour's robot (`ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST`, `GZ_IP=127.0.0.1`),
- adds the `lab` shortcut.

To remove it after the course, delete that line from `~/.bashrc`.

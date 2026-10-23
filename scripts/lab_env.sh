# EE 414 House Lab -- the environment every terminal needs.
#
# install.sh adds one line to ~/.bashrc that sources this file, so every new
# terminal is ready. You can also source it by hand:
#     source ~/ee414_tb3_house_lab/scripts/lab_env.sh

EE414_LAB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export EE414_LAB_DIR
export EE414_WS="${EE414_WS:-$HOME/ee414_ws}"

# ROS 2 Jazzy, then our workspace on top of it.
if [ -f /opt/ros/jazzy/setup.bash ] && [ "${ROS_DISTRO:-}" != "jazzy" ]; then
  source /opt/ros/jazzy/setup.bash
fi
if [ -f "$EE414_WS/install/setup.bash" ]; then
  source "$EE414_WS/install/setup.bash"
fi

# One robot for the whole lab. TurtleBot3's own programs crash without this.
export TURTLEBOT3_MODEL=burger

# Keep ROS 2 and Gazebo traffic INSIDE this computer. In a lab room with 30
# PCs on one network, without these lines your teleop can drive your
# neighbour's robot, and their /scan appears in your RViz.
export ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST
export GZ_IP=127.0.0.1

# The `lab` helper, from any folder.
alias lab="$EE414_LAB_DIR/lab"

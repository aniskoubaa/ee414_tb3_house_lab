#!/usr/bin/env bash
# EE 414 House Lab -- check that everything is installed AND works.
#
#   ./check_setup.sh           all checks, including a 1-minute test drive in the simulator
#   ./check_setup.sh --quick   skip the simulator test
#
# Every line says PASS or FAIL. A FAIL line says how to fix it.
# Show the whole output to the instructor if you are stuck.

LAB_DIR="$(cd "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")" && pwd)"
QUICK=0
[[ "${1:-}" == "--quick" ]] && QUICK=1
FAILS=0

pass() { printf '  \033[32mPASS\033[0m  %s\n' "$1"; }
fail() { printf '  \033[31mFAIL\033[0m  %s\n        fix: %s\n' "$1" "$2"; FAILS=$((FAILS + 1)); }
info() { printf '  \033[34m....\033[0m  %s\n' "$1"; }

echo
echo "  EE 414 House Lab -- setup check   ($(date '+%Y-%m-%d %H:%M'))"
echo

# ---- the computer ------------------------------------------------------------
# shellcheck disable=SC1091
source /etc/os-release
if [[ "$VERSION_ID" == 24.04 ]]; then pass "Ubuntu 24.04"
else fail "Ubuntu 24.04 (you have ${PRETTY_NAME})" "this lab needs Ubuntu 24.04"; fi
if grep -qi microsoft /proc/version 2>/dev/null; then info "running inside WSL2 (Windows): fine, Gazebo uses WSLg"; fi
mem=$(awk '/MemTotal/ {printf "%d", $2/1024/1024}' /proc/meminfo)
if (( mem >= 7 )); then pass "memory: ${mem} GB"
else info "memory: ${mem} GB -- tight. Use ./lab sim nogui and close the browser."; fi

# ---- ROS 2 and packages --------------------------------------------------------
if [ -f /opt/ros/jazzy/setup.bash ]; then pass "ROS 2 Jazzy installed"
else fail "ROS 2 Jazzy installed" "run ./install.sh"; echo; exit 1; fi

# A clean environment, the same one ./lab uses.
for v in $(env | cut -d= -f1 | grep -E '^(AMENT_|COLCON_|CMAKE_PREFIX_PATH|PYTHONPATH|LD_LIBRARY_PATH|CONDA|ROS_DISTRO|ROS_VERSION|ROS_PYTHON_VERSION)'); do unset "$v"; done
export PATH="$(echo "$PATH" | tr ':' '\n' | grep -v -E 'conda|anaconda|miniforge|/snap/' | paste -sd: -)"
# shellcheck disable=SC1091
source "$LAB_DIR/scripts/lab_env.sh"

missing=""
for p in turtlebot3_gazebo turtlebot3_teleop turtlebot3_description ros_gz_sim ros_gz_bridge \
         robot_state_publisher tf2_ros tf2_tools tf2_geometry_msgs rviz2; do
  ros2 pkg prefix "$p" >/dev/null 2>&1 || missing="$missing $p"
done
if [ -z "$missing" ]; then pass "ROS packages: TurtleBot3, Gazebo bridge, TF2, RViz"
else fail "ROS packages missing:$missing" "run ./install.sh"; fi

if gz sim --versions >/dev/null 2>&1; then pass "Gazebo $(gz sim --versions 2>/dev/null | head -1)"
else fail "Gazebo (gz sim)" "run ./install.sh (package ros-jazzy-ros-gz)"; fi

if python3 -c "import rclpy, tf2_ros, tf2_geometry_msgs, matplotlib, pytest" 2>/dev/null; then
  pass "Python modules: rclpy, tf2, matplotlib, pytest"
else
  fail "Python modules" "run ./install.sh. If you use conda: 'conda deactivate' and try again"
fi

# ---- the lab ---------------------------------------------------------------
if ros2 pkg prefix ee414_house_lab >/dev/null 2>&1; then pass "lab package built in $EE414_WS"
else fail "lab package built" "run ./lab build  (or ./install.sh)"; fi

if grep -q 'EE 414 House Lab' "$HOME/.bashrc" 2>/dev/null; then pass "new terminals are set up (~/.bashrc)"
else info "~/.bashrc has no lab line: in each new terminal run  source $LAB_DIR/scripts/lab_env.sh"; fi

if [[ "$(python3 -c 'import sys; print(sys.executable)')" == /usr/bin/python3* ]]; then
  pass "python3 is the system Python (not conda)"
else
  fail "python3 is $(command -v python3)" "conda is active: run 'conda deactivate', or 'conda config --set auto_activate_base false'"
fi

# ---- a real test drive --------------------------------------------------------
if (( QUICK )); then
  info "simulator test skipped (--quick)"
elif (( FAILS > 0 )); then
  info "simulator test skipped: fix the FAIL lines first"
else
  info "simulator test: starting the house without a window (up to 90 s) ..."
  # Our own private Gazebo and ROS channel, so a simulator you already have
  # open is not disturbed (and does not fool the test).
  export GZ_PARTITION="ee414_check_$$" ROS_DOMAIN_ID=$(( ($$ % 100) + 101 ))
  log="$(mktemp)"
  setsid ros2 launch ee414_house_lab house.launch.py gui:=false >"$log" 2>&1 &
  sim=$!
  t0=$(date +%s); up=0
  for _ in $(seq 1 90); do
    if timeout 3 ros2 topic echo --once /scan >/dev/null 2>&1; then up=1; break; fi
    sleep 1
  done
  if (( up )); then
    pass "simulator started in $(( $(date +%s) - t0 )) s, the laser publishes /scan"
    type=$(ros2 topic type /cmd_vel 2>/dev/null)
    if [[ "$type" == geometry_msgs/msg/TwistStamped ]]; then pass "/cmd_vel takes TwistStamped"
    else fail "/cmd_vel type is '$type'" "show this output to the instructor"; fi
    if timeout 5 ros2 topic echo --once /ground_truth >/dev/null 2>&1; then pass "/ground_truth (used by the lab monitor)"
    else fail "/ground_truth missing" "show this output to the instructor"; fi
    moved=$(timeout 25 python3 - <<'PY' 2>/dev/null
import time, rclpy
from geometry_msgs.msg import TwistStamped
from nav_msgs.msg import Odometry
rclpy.init()
n = rclpy.create_node('ee414_check')
pos = {}
n.create_subscription(Odometry, '/odom', lambda m: pos.update(x=m.pose.pose.position.x), 10)
pub = n.create_publisher(TwistStamped, '/cmd_vel', 10)
end = time.time() + 5
while 'x' not in pos and time.time() < end:
    rclpy.spin_once(n, timeout_sec=0.1)
x0 = pos.get('x', 0.0)
end = time.time() + 2.5
while time.time() < end:
    m = TwistStamped(); m.twist.linear.x = 0.15
    pub.publish(m); rclpy.spin_once(n, timeout_sec=0.05)
for _ in range(10):
    pub.publish(TwistStamped()); rclpy.spin_once(n, timeout_sec=0.05)
print(f"{pos.get('x', 0.0) - x0:.2f}")
PY
)
    if [[ -n "$moved" ]] && awk "BEGIN {exit !($moved > 0.15)}"; then
      pass "test drive: the robot drove ${moved} m forward"
    else
      fail "test drive: the robot did not move (moved='${moved}')" "show this output to the instructor"
    fi
  else
    fail "simulator did not start within 90 s" "see the log below; try again once (the first start is slow)"
    grep -iE 'error|fatal|died' "$log" | head -8 | sed 's/^/        /'
  fi
  kill -INT -- -"$sim" 2>/dev/null; sleep 3; kill -9 -- -"$sim" 2>/dev/null
  rm -f "$log"
fi

echo
if (( FAILS == 0 )); then
  printf '  \033[1;32mALL GOOD.\033[0m  Start the lab with:  ./lab sim\n\n'
else
  printf '  \033[1;31m%d problem(s).\033[0m Fix the FAIL lines (top first), then run ./check_setup.sh again.\n\n' "$FAILS"
  exit 1
fi

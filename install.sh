#!/usr/bin/env bash
# EE 414 House Lab -- install everything, build the lab, and check it.
#
#   ./install.sh              install + build + full check (takes 10-40 min the first time)
#   ./install.sh --no-shell   do not add the lab line to ~/.bashrc
#   ./install.sh --check      only run the check (installs nothing)
#
# What it installs (with apt, from the official ROS 2 repository):
#   ROS 2 Jazzy (desktop), Gazebo Harmonic + the ROS bridge, TurtleBot3 (robot,
#   simulation, teleop), TF2 tools, colcon, pytest, matplotlib.
# Then it builds the lab in ~/ee414_ws and runs ./check_setup.sh.
#
# Already have ROS 2 Jazzy (for example from the agentic_robotics repository)?
# Run it anyway: apt skips what is already there, and only the missing
# TurtleBot3 pieces are added.
#
# Supported: Ubuntu 24.04 (native, or WSL2 on Windows 11). Safe to run again.

set -euo pipefail
LAB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EE414_WS="${EE414_WS:-$HOME/ee414_ws}"
DO_SHELL=1

for arg in "$@"; do
  case "$arg" in
    --no-shell) DO_SHELL=0 ;;
    --check) exec "$LAB_DIR/check_setup.sh" ;;
    -h|--help) sed -n '2,17p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "Unknown option: $arg  (try --help)" >&2; exit 2 ;;
  esac
done

say()  { printf '\n\033[1;34m==> %s\033[0m\n' "$*"; }
fail() { printf '\n\033[1;31m✗ %s\033[0m\n' "$*" >&2; exit 1; }
trap 'printf "\n\033[1;31m✗ The installer stopped at line %s. Read the error above, fix it, and run ./install.sh again.\033[0m\n" "$LINENO" >&2' ERR

# ---- 0. the right computer --------------------------------------------------
[[ $EUID -ne 0 ]] || fail "Run as your normal user, WITHOUT sudo:  ./install.sh"
# shellcheck disable=SC1091
source /etc/os-release
[[ "${ID:-}" == ubuntu && "${VERSION_ID:-}" == 24.04 ]] || \
  fail "This lab needs Ubuntu 24.04. You have: ${PRETTY_NAME:-unknown}."
command -v sudo >/dev/null || fail "sudo is missing."

say "1/5  Asking for your password once (needed for apt)"
sudo -v

# ---- 1. the ROS 2 apt repository --------------------------------------------
# sudo drops environment variables, so DEBIAN_FRONTEND goes on the command line:
# without it, a first-time tzdata install stops and waits for a keyboard answer.
APT="sudo DEBIAN_FRONTEND=noninteractive apt-get"
say "2/5  Adding the ROS 2 package repository"
$APT update -q
$APT install -y -q software-properties-common curl ca-certificates locales git
sudo locale-gen en_US en_US.UTF-8 >/dev/null
sudo add-apt-repository -y universe >/dev/null
if ! dpkg -s ros2-apt-source >/dev/null 2>&1 && ! grep -rqs 'packages.ros.org/ros2' /etc/apt/sources.list.d/; then
  # The official way: a small package that owns the repository key and keeps it up to date.
  ver="$(curl -fsSL --retry 3 https://api.github.com/repos/ros-infrastructure/ros-apt-source/releases/latest \
        | grep -F '"tag_name"' | head -1 | cut -d'"' -f4 || true)"
  if [ -n "$ver" ]; then
    deb="$(mktemp --suffix=.deb)"
    curl -fL --retry 3 -o "$deb" \
      "https://github.com/ros-infrastructure/ros-apt-source/releases/download/${ver}/ros2-apt-source_${ver}.$(. /etc/os-release && echo "$VERSION_CODENAME")_all.deb"
    sudo dpkg -i "$deb"
    rm -f "$deb"
  else
    # GitHub API unreachable (rate limit, proxy): the classic key + list file.
    sudo curl -fsSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
      -o /usr/share/keyrings/ros-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu noble main" \
      | sudo tee /etc/apt/sources.list.d/ros2.list >/dev/null
  fi
fi

# ---- 2. the packages ---------------------------------------------------------
say "3/5  Installing ROS 2 Jazzy, Gazebo and TurtleBot3 (the long step: ~3 GB)"
$APT update -q
$APT install -y -q --no-install-recommends \
  ros-jazzy-desktop \
  ros-jazzy-ros-gz \
  ros-jazzy-turtlebot3 \
  ros-jazzy-turtlebot3-simulations \
  ros-jazzy-tf2-tools \
  ros-jazzy-tf2-geometry-msgs \
  python3-colcon-common-extensions \
  python3-pytest \
  python3-matplotlib \
  zip

# ---- 3. the workspace --------------------------------------------------------
say "4/5  Building the lab in $EE414_WS"
mkdir -p "$EE414_WS/src"
link="$EE414_WS/src/ee414_tb3_house_lab"
if [ -L "$link" ] && [ "$(readlink -f "$link")" != "$LAB_DIR" ]; then
  rm "$link"                     # the repository moved: point at the new place
fi
[ -e "$link" ] || ln -s "$LAB_DIR" "$link"
# A clean environment: conda or another ROS workspace in this shell breaks the build.
( cd "$EE414_WS" && env -i HOME="$HOME" USER="${USER:-$(id -un)}" PATH=/usr/sbin:/usr/bin:/sbin:/bin \
    bash -c 'source /opt/ros/jazzy/setup.bash && colcon build --symlink-install --packages-select ee414_house_lab' )

# ---- 4. every new terminal ready ---------------------------------------------
if (( DO_SHELL )); then
  say "5/5  Making every new terminal ready (one line in ~/.bashrc)"
  marker='# EE 414 House Lab'
  sed -i "/$marker/d" "$HOME/.bashrc"
  echo "source \"$LAB_DIR/scripts/lab_env.sh\"  $marker" >> "$HOME/.bashrc"
else
  say "5/5  Skipping ~/.bashrc (--no-shell). In each terminal run:  source $LAB_DIR/scripts/lab_env.sh"
fi

trap - ERR
say "Installed. Now checking that everything really works ..."
"$LAB_DIR/check_setup.sh" || exit 1
printf '\n\033[1;32m✓ Done. Close this terminal and open a NEW one, then:  cd %s && ./lab sim\033[0m\n\n' "$LAB_DIR"

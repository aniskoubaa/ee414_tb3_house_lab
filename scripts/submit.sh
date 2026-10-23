#!/usr/bin/env bash
# Pack one lab for submission:   ./lab submit 1 <your student ID>
#
# The zip contains:
#   submission/labN/       your REPORT.md, the monitor results (.txt .csv .png)
#                          and any screenshots you saved there
#   your code for that lab (the l<N>_*.py files)
set -o pipefail   # (no -u: ROS setup.bash reads unset variables)
LAB_DIR="$(cd "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")/.." && pwd)"
n="${1:-}"; id="${2:-}"
if [[ ! "$n" =~ ^[123]$ || -z "$id" ]]; then
  echo "  usage: ./lab submit <lab number> <student ID>     e.g.  ./lab submit 1 220012345"
  exit 1
fi
dir="$LAB_DIR/submission/lab$n"
report="$dir/REPORT.md"

problems=0
if [ ! -f "$report" ]; then
  echo "  ✗ $report is missing."; exit 1
fi
if grep -q '_\[answer\]_' "$report"; then
  echo "  ! REPORT.md still has $(grep -c '_\[answer\]_' "$report") unanswered _[answer]_ place(s)."
  problems=1
fi
if ! ls "$dir"/lab"$n"_*.txt >/dev/null 2>&1; then
  echo "  ! no monitor/check results in $dir (lab${n}_*.txt). Did you run them? (see the guide)"
  problems=1
fi
if (( problems )); then
  read -r -p "  Submit anyway? [y/N] " ans
  [[ "$ans" == y || "$ans" == Y ]] || { echo "  Not submitted."; exit 1; }
fi

out="$HOME/EE414_lab${n}_${id}.zip"
rm -f "$out"
cd "$LAB_DIR" || exit 1
zip -q -r "$out" "submission/lab$n" ee414_house_lab/ee414_house_lab/l"$n"_*.py
if [[ "$n" == 3 ]]; then   # Lab 3 reuses your Lab 1 sector_min
  zip -q "$out" ee414_house_lab/ee414_house_lab/l1_scan_reader.py
fi
echo
echo "  Created: $out"
unzip -l "$out" | tail -n +4 | head -n -2 | awk '{print "     " $4}'
echo
echo "  Upload this file to the course page (Moodle/Blackboard) before the next lecture."

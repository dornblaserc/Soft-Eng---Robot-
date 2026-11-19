#!/usr/bin/env bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cleanup() {
    echo ""
    echo "Shutting down LIMO drivers and Python sequence..."
    kill $(jobs -p) 2>/dev/null || true
    wait 2>/dev/null || true
    echo "Clean shutdown complete."
}
trap cleanup EXIT INT TERM

source /opt/ros/noetic/setup.bash
source /home/agilex/agilex_ws/devel/setup.bash 2>/dev/null || true

unset ROS_IPV6
export ROS_IP=127.0.0.1
export ROS_MASTER_URI=http://127.0.0.1:11311

echo "[1/4] Launching LIMO base drivers..."
roslaunch limo_bringup limo_start.launch > /dev/null 2>&1 &

echo "[2/4] Waiting for base driver (/cmd_vel)..."
until rostopic list 2>/dev/null | grep -q "/cmd_vel"; do
    sleep 0.5
done
echo "Base driver active."

echo "[3/4] Launching Orbbec DaBai camera..."
roslaunch astra_camera dabai_u3.launch > /dev/null 2>&1 &

until rostopic list 2>/dev/null | grep -Eq "/camera/(rgb|color)/image_raw"; do
    sleep 0.5
done
echo "Camera driver active."

# echo "[4/4] Running execution sequence..."
python3 -u "src/Tests/in_progress/main.py"
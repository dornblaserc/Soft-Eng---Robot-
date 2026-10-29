#!/usr/bin/env bash

# Terminate all child processes on Ctrl+C or script exit
cleanup() {
    echo ""
    echo "Shutting down LIMO base drivers and Python sequence..."
    kill $(jobs -p) 2>/dev/null || true
    wait 2>/dev/null || true
    echo "Clean shutdown complete."
}
trap cleanup EXIT INT TERM

# Ensure environment is sourced
source /opt/ros/noetic/setup.bash
source /home/agilex/agilex_ws/devel/setup.bash 2>/dev/null || true

unset ROS_IPV6
export ROS_IP=127.0.0.1
export ROS_MASTER_URI=http://127.0.0.1:11311

echo "[1/3] Launching LIMO hardware drivers..."
roslaunch limo_bringup limo_start.launch > /dev/null 2>&1 &

echo "[2/3] Waiting for base driver to initialize..."
until rostopic list 2>/dev/null | grep -q "/cmd_vel"; do
    sleep 0.5
done
echo "Base driver active."

echo "[3/3] Running execution sequence..."
python3 src/Tests/in_progress/main.py
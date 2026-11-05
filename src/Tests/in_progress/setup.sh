#!/usr/bin/env bash

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

echo "[2/4] Launching Orbbec DaBai depth camera..."
roslaunch astra_camera dabai.launch depth_registration:=true > /dev/null 2>&1 &

echo "[3/4] Waiting for base and camera topics..."
until rostopic list 2>/dev/null | grep -q "/cmd_vel" && rostopic list 2>/dev/null | grep -q "/camera/color/image_raw"; do
    sleep 0.5
done
echo "Drivers active."

echo "[4/4] Running execution sequence..."
python3 src/Tests/in_progress/main.py
#!/usr/bin/env bash
# ==============================================================================
# File: setup.sh
# Description:
#   Master startup script for the AgileX LIMO pick-and-place system.
#   1. Registers a cleanup trap so background ROS nodes terminate cleanly on exit.
#   2. Sources the ROS 1 Noetic environment and the local AgileX workspace.
#   3. Launches the LIMO chassis driver and Orbbec DaBai RGB-D camera driver.
#   4. Polls ROS topics until hardware communication is verified.
#   5. Runs the main Python pick-and-place state machine.
# ==============================================================================

# Terminate all background child processes if the user presses Ctrl+C or the script exits
cleanup() {
    echo ""
    echo "Shutting down LIMO drivers and Python sequence..."
    kill $(jobs -p) 2>/dev/null || true
    wait 2>/dev/null || true
    echo "Clean shutdown complete."
}
trap cleanup EXIT INT TERM

# Load ROS 1 Noetic core packages and custom AgileX LIMO workspace packages
source /opt/ros/noetic/setup.bash
source /home/agilex/agilex_ws/devel/setup.bash 2>/dev/null || true

# Configure ROS networking to run locally on the robot's onboard computer
unset ROS_IPV6
export ROS_IP=127.0.0.1
export ROS_MASTER_URI=http://127.0.0.1:11311

echo "[1/4] Launching LIMO base drivers..."
# Starts serial communication with the LIMO wheels/motors in the background
roslaunch limo_bringup limo_start.launch > /dev/null 2>&1 &

echo "[2/4] Launching Orbbec DaBai depth camera..."
# Starts the RGB-D camera driver.
# depth_registration:=true aligns the depth map pixel-for-pixel with the RGB color image.
roslaunch astra_camera dabai.launch depth_registration:=true > /dev/null 2>&1 &

echo "[3/4] Waiting for base and camera topics..."
# Block execution until both the wheel velocity topic and color camera topic are live
until rostopic list 2>/dev/null | grep -q "/cmd_vel" && rostopic list 2>/dev/null | grep -q "/camera/color/image_raw"; do
    sleep 0.5
done
echo "Drivers active."

echo "[4/4] Running execution sequence..."
python3 src/Tests/in_progress/drive.py
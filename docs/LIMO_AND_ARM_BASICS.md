# Driver Information and Starter Commands 

This document shows the relevant commands for both the LIMO driving robot and the elephant arm with info on the ROS driver we needed to use.

## Terminal

The terminal that is on the AgileX LIMO 2 is a linux terminal and asks you which version of ROS do you want to use. ROS means Robot Operating System and it tells you to either enter a 1 or a 2. For this project we only used Noetic ROS 1 commands.

## Driver

To run programs that control the LIMO 2 you will need to start up the roslaunch driver. 

```
roslaunch limo_bringup limo_start.launch pub_odom_tf:=false
```


## LIMO (ROS Noetic, Python `rospy`)

| Function | What it does |
|---|---|
| `rospy.init_node("name")` | Registers your script as a ROS node. Must be called before anything else. |
| `rospy.Publisher("/cmd_vel", Twist, queue_size=10)` | Opens a channel to the driver's velocity topic. |
| `Twist()` | The message type. Set `cmd.linear.x` (forward speed, m/s) and `cmd.angular.z` (turn rate, rad/s). |
| `pub.publish(cmd)` | Sends the velocity command. Must be repeated, because the driver treats silence as a stop. |
| `rospy.Rate(10)` and `rate.sleep()` | Keeps the loop at 10 messages per second. |
| `rospy.sleep(1)` | Waits for the publisher to connect before sending. |
| `rospy.Time.now()` and `rospy.Duration(2)` | Used to run a motion for a fixed time. |
| `rospy.is_shutdown()` | Lets the loop exit cleanly on Ctrl+C. |
| `pub.publish(Twist())` | Sends all zeros, which stops the robot. |

### Command-line tools

- `roslaunch limo_bringup limo_start.launch pub_odom_tf:=false` starts the driver.
- `rosnode list` shows running nodes.
- `rostopic echo /cmd_vel` shows whether commands are arriving for debugging


## Elephant Robotics 280 M5 arm (Python `pymycobot`)

| Function | What it does |
|---|---|
| `MyCobot280("/dev/ttyACM0",115200)` | Opens the serial connection to the arm. |
| `mc.power_on()` | Powers the servos. |
| `mc.focus_all_servos()` | Energizes all servos so they hold position. |
| `mc.send_angle(id, degree, speed)` | Moves one joint (1 to 6). |
| `mc.send_angles([a1..a6], speed)` | Moves all six joints at once. |
| `mc.get_angles()` | Reads the current joint angles. Returns -1 if there is no communication. |
| `mc.is_moving()` | Reports whether the arm is in motion. |
| `mc.is_power_on()`, `mc.is_all_servo_enable()`, `mc.get_servo_status()` | Diagnostics for power and servo state. |
| `mc.get_system_version()` | Reads the firmware version. Useful as a connection check. |
| `time.sleep(n)` | Needed after move commands, since they return immediately. |
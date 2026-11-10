"""
File: arm_controller.py
Description:
  Controls the 6-DOF Elephant Robotics MyCobot 280 robotic arm and adaptive gripper.
  Combines Inverse Kinematics (send_coords) for reaching dynamic 3D ball positions
  with fixed Joint Angles (send_angles) for safe transit and box drop-off poses.
"""

import time
from pymycobot import MyCobot280


class ArmController:
  """Manages motion sequences and gripper actuation for the MyCobot 280 arm."""

  def __init__(self, port="/dev/ttyACM0", baudrate=115200):
    """Connects to the MyCobot 280 over USB serial and powers on the servos.

    Args:
      port (str): Linux serial device path for the arm (typically /dev/ttyACM0).
      baudrate (int): Serial communication speed (115200 baud for MyCobot 280).
    """
    self.mc = MyCobot280(port, baudrate)
    self.mc.power_on()
    time.sleep(1)

    # Initialize gripper into active state
    self.mc.set_gripper_state(0, 50)
    time.sleep(2)

    # Safe folded joint angles [J1, J2, J3, J4, J5, J6] in degrees.
    # Keeps the arm tucked back so it does not block the camera or hit obstacles while driving.
    self.TUCK_POSE = [0, 20, -80, 0, 60, 0]

    # End-effector tool orientation [Rx, Ry, Rz] in degrees that points the gripper
    # straight down toward the bin. Can be fine-tuned using teach_angles.py.
    self.GRIP_ORIENTATION = [-180, 0, 0]

  def reset_and_tuck(self, speed=50):
    """Closes the gripper and folds the arm into its safe driving posture.

    Args:
      speed (int): Movement speed from 1 (slowest) to 100 (fastest).
    """
    # Gripper value scale: 0 = completely closed, 100 = completely open
    self.mc.set_gripper_value(0, speed)
    self.mc.send_angles(self.TUCK_POSE, speed)
    time.sleep(3)

  def pick_at_xyz(self, x_mm, y_mm, z_mm, speed=40):
    """Grasps a ball at the specified 3D coordinate using onboard Inverse Kinematics.

    To avoid colliding with the walls of the box, the gripper first moves to a
    hover point 50 mm directly above the ball, descends vertically to grasp it,
    and lifts straight back up.

    Args:
      x_mm (float): Forward distance from arm base center in millimeters.
      y_mm (float): Left (+Y) or Right (-Y) distance from arm base center in millimeters.
      z_mm (float): Vertical height relative to arm base in millimeters.
      speed (int): Arm travel speed (1-100).
    """
    # 1. Open the gripper jaws fully (100 = full open) before approaching
    self.mc.set_gripper_value(100, 50)
    time.sleep(2)

    # 2. Hover 50 mm above the target ball.
    # Mode 1 instructs the MyCobot firmware to interpolate in a straight line.
    hover_coords = [x_mm, y_mm, z_mm + 50.0] + self.GRIP_ORIENTATION
    self.mc.send_coords(hover_coords, speed, 1)
    time.sleep(3)

    # 3. Descend straight down onto the ball
    pick_coords = [x_mm, y_mm, z_mm] + self.GRIP_ORIENTATION
    self.mc.send_coords(pick_coords, speed, 1)
    time.sleep(2)

    # 4. Close the gripper onto the 40 mm ping pong ball (15 = calibrated grip closure)
    self.mc.set_gripper_value(15, 50)
    time.sleep(2)

    # 5. Retract straight up to clear the bin walls before swinging the base
    self.mc.send_coords(hover_coords, speed, 1)
    time.sleep(2)

  def place_in_box(self, side="left", speed=50):
    """Swings the arm to the left or right collection tray, drops the ball, and tucks back.

    Args:
      side (str): Target drop side, either 'left' (+16 deg base yaw) or 'right' (-16 deg).
      speed (int): Arm travel speed (1-100).
    """
    # Joint 1 controls base rotation (positive angle swings left, negative swings right)
    j1_angle = 16 if side == "left" else -16

    # Move to the calibrated drop-off joint pose [J1, J2, J3, J4, J5, J6]
    self.mc.send_angles([j1_angle, 110, -25, 0, 135, 0], speed)
    time.sleep(5)

    # Open gripper jaws (100 = full open) to release the ball into the box
    self.mc.set_gripper_value(100, 50)
    time.sleep(2)

    # Return to the safe folded pose
    self.mc.send_angles(self.TUCK_POSE, speed)
    time.sleep(3)
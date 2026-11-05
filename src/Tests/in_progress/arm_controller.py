import time
from pymycobot import MyCobot280


class ArmController:

  def __init__(self, port="/dev/ttyACM0", baudrate=115200):
    self.mc = MyCobot280(port, baudrate)
    self.mc.power_on()
    time.sleep(1)
    self.mc.set_gripper_state(0, 50)
    time.sleep(2)

    # Safe driving pose
    self.TUCK_POSE = [0, 20, -80, 0, 60, 0]

    # Gripper orientation pointing downward [Rx, Ry, Rz]
    # Run mc.get_coords()[3:] at your pickup pose from teach_angles.py to verify
    self.GRIP_ORIENTATION = [-180, 0, 0]

  def reset_and_tuck(self, speed=30):
    self.mc.set_gripper_value(0, speed)
    self.mc.send_angles(self.TUCK_POSE, speed)
    time.sleep(3)

  def pick_at_xyz(self, x_mm, y_mm, z_mm, speed=30):
    """Moves gripper to [x_mm, y_mm, z_mm] in arm base frame using MyCobot IK."""
    # 1. Open gripper fully (from grableft.py)
    self.mc.set_gripper_value(100, 50)
    time.sleep(2)

    # 2. Approach 50mm above the ball to clear the box walls
    hover_coords = [x_mm, y_mm, z_mm + 50.0] + self.GRIP_ORIENTATION
    self.mc.send_coords(hover_coords, speed, 1)  # mode 1 = linear path
    time.sleep(3)

    # 3. Descend onto the ball
    pick_coords = [x_mm, y_mm, z_mm] + self.GRIP_ORIENTATION
    self.mc.send_coords(pick_coords, speed, 1)
    time.sleep(2)

    # 4. Close gripper onto ping pong ball (15 = grip value from grableft.py)
    self.mc.set_gripper_value(15, 50)
    time.sleep(2)

    # 5. Lift vertically out of the box
    self.mc.send_coords(hover_coords, speed, 1)
    time.sleep(2)

  def place_in_box(self, side="left", speed=30):
    """Places ball using the exact joint pose from grableft.py (mirrored on J1 for right)."""
    j1_angle = 16 if side == "left" else -16
    self.mc.send_angles([j1_angle, 110, -25, 0, 135, 0], speed)
    time.sleep(5)

    self.mc.set_gripper_value(100, 50)
    time.sleep(2)
    self.mc.send_angles(self.TUCK_POSE, speed)
    time.sleep(3)
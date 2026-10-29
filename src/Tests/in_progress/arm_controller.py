import time
from pymycobot import MyCobot280


class ArmController:

  def __init__(self, port="/dev/ttyACM0", baudrate=115200):
    self.mc = MyCobot280(port, baudrate)
    self.mc.power_on()
    time.sleep(1)

    # Safe transit angles [J1, J2, J3, J4, J5, J6]
    self.TUCK_POSE = [0, 20, -80, 0, 60, 0]
    # Replace with your recorded pickup angles
    self.PICKUP_POSE = [0, -30, -60, 0, 0, 0]

  def tuck(self, speed=30):
    self.mc.send_angles(self.TUCK_POSE, speed)
    time.sleep(3)

  def reach_pickup(self, speed=20):
    self.mc.send_angles(self.PICKUP_POSE, speed)
    time.sleep(4)

  def set_gripper(self, state, speed=50):
    # 0 = open, 1 = close
    self.mc.set_gripper_state(state, speed)
    time.sleep(2)
from arm_controller import ArmController
from robot_base import LimoBase
import rospy


def main():
  rospy.init_node("limo_pickup_sequence", anonymous=True)

  arm = ArmController(port="/dev/ttyACM0")
  base = LimoBase()

  # 1. Prepare arm
  arm.tuck()
  arm.set_gripper(state=0)  # Open

  # 2. Drive to ball (distance in meters)
  base.drive_forward(distance=0.3, speed=0.1)

  # 3. Grasp and lift
  arm.reach_pickup()
  arm.set_gripper(state=1)  # Close
  arm.tuck()


if __name__ == "__main__":
  try:
    main()
  except rospy.ROSInterruptException:
    pass
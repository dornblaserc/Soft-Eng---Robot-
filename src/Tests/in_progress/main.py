from arm_controller import ArmController
from robot_base import LimoBase
import rospy


def main():
  rospy.init_node("limo_pickup_sequence", anonymous=True)

  rospy.loginfo("Connecting to LIMO base and MyCobot arm...")
  base = LimoBase()
  arm = ArmController(port="/dev/ttyACM0")

  # 1. Preparation: Tuck arm into safe transit posture and open gripper
  rospy.loginfo("Setting arm to transit pose and opening gripper...")
  arm.tuck()
  arm.set_gripper(state=0)  # 0 = open

  # 2. Base Movement: Drive designated distance to object
  target_distance = 0.3  # meters
  drive_speed = 0.1  # m/s
  rospy.loginfo(f"Driving {target_distance}m at {drive_speed} m/s...")
  base.drive_forward(distance=target_distance, speed=drive_speed)

  # 3. Grasp: Lower to pickup coordinates, close gripper, and lift
  rospy.loginfo("Lowering arm to pickup target...")
  arm.reach_pickup()

  rospy.loginfo("Closing gripper...")
  arm.set_gripper(state=1)  # 1 = close

  rospy.loginfo("Lifting payload back to transit pose...")
  arm.tuck()

  rospy.loginfo("Pickup sequence complete.")


if __name__ == "__main__":
  try:
    main()
  except rospy.ROSInterruptException:
    pass
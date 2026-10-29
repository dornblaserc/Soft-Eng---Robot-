from arm_controller import ArmController
from robot_base import LimoBase
from grableft import StartGrab
import rospy


def main():
  rospy.init_node("limo_pickup_sequence", anonymous=True)

  rospy.loginfo("Connecting to LIMO base and MyCobot arm...")
  base = LimoBase()
  arm = ArmController(port="/dev/ttyACM0")


  # 2. Base Movement: Drive designated distance to object
  target_distance = 0.3  # meters
  drive_speed = 0.1  # m/s
  rospy.loginfo(f"Driving {target_distance}m at {drive_speed} m/s...")
  base.drive_forward(distance=target_distance, speed=drive_speed)

  # 3. Grasp: Lower to pickup coordinates, close gripper, and lift
  StartGrab()


if __name__ == "__main__":
  try:
    main()
  except rospy.ROSInterruptException:
    pass
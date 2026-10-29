from grableft import start_grab
from robot_base import LimoBase
import rospy


def main():
  rospy.init_node("limo_pickup_sequence", anonymous=True)

  base = LimoBase()

  # 1. Drive to object
  target_distance = 0.3  # meters
  drive_speed = 0.1  # m/s
  rospy.loginfo(f"Driving {target_distance}m at {drive_speed} m/s...")
  base.drive_forward(distance=target_distance, speed=drive_speed)

  # 2. Execute pick-and-place
  rospy.loginfo("Starting pickup routine...")
  start_grab(port="/dev/ttyACM0")
  rospy.loginfo("Sequence completed.")


if __name__ == "__main__":
  try:
    main()
  except rospy.ROSInterruptException:
    pass
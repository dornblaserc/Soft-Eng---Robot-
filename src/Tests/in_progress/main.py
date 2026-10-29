from robot_base import LimoBase
import rospy


def main():
  rospy.init_node("limo_movement_test", anonymous=True)
  base = LimoBase()

  rospy.loginfo("Starting movement test: driving forward 0.3m at 0.1 m/s...")
  base.drive_forward(distance=0.3, speed=0.1)
  rospy.loginfo("Movement test complete.")


if __name__ == "__main__":
  try:
    main()
  except rospy.ROSInterruptException:
    pass
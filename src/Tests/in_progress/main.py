from arm_controller import ArmController
from robot_base import LimoBase
import rospy
from vision_detector import BallDetector

# Measured offset (dx, dy, dz) in mm from MyCobot base to Orbbec camera lens
CAM_TO_ARM_OFFSET_MM = (80.0, 0.0, -45.0)


def wait_for_target(detector, timeout=5.0):
  """Polls the synchronized RGB-D detector until a valid 3D ball coordinate is locked."""
  end_time = rospy.Time.now() + rospy.Duration(timeout)
  rate = rospy.Rate(10)
  while not rospy.is_shutdown() and rospy.Time.now() < end_time:
    coords = detector.get_target_arm_coords(CAM_TO_ARM_OFFSET_MM)
    if coords is not None:
      return coords
    rate.sleep()
  return None


def main():
  rospy.init_node("limo_pickup_sequence", anonymous=True)

  base = LimoBase()
  arm = ArmController(port="/dev/ttyACM0")
  detector = BallDetector(model_path="ping_pong_seg.pt", target_class_id=0)

  # 1. Tuck arm so it does not block the depth camera
  arm.reset_and_tuck()

  # 2. Drive to the bin
  target_distance = 0.3
  drive_speed = 0.1
  rospy.loginfo(f"Driving {target_distance}m at {drive_speed} m/s...")
  base.drive_forward(distance=target_distance, speed=drive_speed)

  # 3. Acquire 3D ball coordinates from RGB-D camera
  rospy.loginfo("Acquiring 3D target coordinates from depth camera...")
  target_xyz = wait_for_target(detector, timeout=5.0)

  if target_xyz is None:
    rospy.logerr("No valid ball detected in depth range. Aborting pick.")
    return

  x_mm, y_mm, z_mm = target_xyz
  rospy.loginfo(
      f"Picking ball at arm coords: X={x_mm:.1f}mm, Y={y_mm:.1f}mm, Z={z_mm:.1f}mm"
  )

  # 4. Execute IK pick and place
  arm.pick_at_xyz(x_mm, y_mm, z_mm)
  arm.place_in_box(side="left")
  rospy.loginfo("Sequence completed.")


if __name__ == "__main__":
  try:
    main()
  except rospy.ROSInterruptException:
    pass
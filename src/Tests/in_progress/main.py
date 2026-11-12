<<<<<<< HEAD
from Tests.grableft import start_grab
=======
"""
File: main.py
Description:
  Main execution entry point for the AgileX LIMO autonomous ball-picking sequence.
  Coordinates the mobile base, RGB-D vision detector, and MyCobot 280 robotic arm:
    Step 1: Folds the arm out of the camera's field of view.
    Step 2: Drives the LIMO forward to the ball bin.
    Step 3: Queries the depth camera + YOLO detector for the topmost ball's 3D coordinates.
    Step 4: Commands the arm to pick the ball via Inverse Kinematics and place it in a box.
"""

from arm_controller import ArmController
>>>>>>> dd1aa8534d39ef1713816d9f6c39ee04abf47eef
from robot_base import LimoBase
import rospy
from vision_detector import BallDetector

# Physical mounting offset (dx, dy, dz) in millimeters from the center of the
# MyCobot base to the Orbbec camera lens:
#   dx (+X): How many mm the camera lens sits in front of the arm base center (e.g. 80.0 mm)
#   dy (+Y): How many mm the camera lens sits left/right of the arm centerline (e.g. 0.0 mm)
#   dz (+Z): How many mm the camera lens sits above/below the arm base (e.g. -45.0 mm)
CAM_TO_ARM_OFFSET_MM = (80.0, 0.0, -45.0)


def wait_for_target(detector, timeout=5.0):
  """Polls the vision detector until a valid 3D ball coordinate is found or timeout expires.

  Args:
    detector (BallDetector): Initialized RGB-D YOLO detector instance.
    timeout (float): Maximum time in seconds to wait for a valid detection.

  Returns:
    tuple: (x_mm, y_mm, z_mm) target coordinates in the arm base frame, or None on timeout.
  """
  end_time = rospy.Time.now() + rospy.Duration(timeout)
  rate = rospy.Rate(10)

  while not rospy.is_shutdown() and rospy.Time.now() < end_time:
    coords = detector.get_target_arm_coords(CAM_TO_ARM_OFFSET_MM)
    if coords is not None:
      return coords
    rate.sleep()

  return None


def main():
  # Initialize the ROS 1 node for this process
  rospy.init_node("limo_pickup_sequence", anonymous=True)

  # Instantiate hardware controllers and the vision pipeline
  base = LimoBase()
  arm = ArmController(port="/dev/ttyACM0")
  detector = BallDetector(model_path="best.pt", target_class_id=0)

  # 1. Tuck the arm so it does not obstruct the depth camera while approaching
  rospy.loginfo("Folding arm into safe transit pose...")
  arm.reset_and_tuck()

  # 2. Drive the LIMO forward to the bin
  target_distance = 0.3  # meters
  drive_speed = 0.1      # meters per second
  rospy.loginfo(f"Driving {target_distance}m at {drive_speed} m/s...")
  base.drive_forward(distance=target_distance, speed=drive_speed)

  # 3. Locate the topmost target ball in 3D space
  rospy.loginfo("Acquiring 3D target coordinates from depth camera...")
  target_xyz = wait_for_target(detector, timeout=5.0)

  if target_xyz is None:
    rospy.logerr("No valid ball detected within depth range. Aborting pick.")
    return

  x_mm, y_mm, z_mm = target_xyz
  rospy.loginfo(
      f"Picking ball at arm coords: X={x_mm:.1f}mm, Y={y_mm:.1f}mm, Z={z_mm:.1f}mm"
  )

  # 4. Execute Inverse Kinematics pick and deposit into the left collection box
  arm.pick_at_xyz(x_mm, y_mm, z_mm)
  arm.place_in_box(side="left")
  rospy.loginfo("Sequence completed.")


if __name__ == "__main__":
  try:
    main()
  except rospy.ROSInterruptException:
    pass
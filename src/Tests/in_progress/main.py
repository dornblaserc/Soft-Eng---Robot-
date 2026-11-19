"""
File: main.py
Description:
  Main execution entry point for the AgileX LIMO autonomous ball-picking sequence.
  Coordinates the mobile base, HSV + RGB-D vision detector, and MyCobot 280 arm:
    Step 1: Folds the arm out of the camera's field of view.
    Step 2: Drives the LIMO forward to the ball bin.
    Step 3: Displays a resizable live camera feed and locks the topmost ball's 3D coordinates.
    Step 4: Commands the arm to pick the ball via Inverse Kinematics and place it in a box.
"""

from arm_controller import ArmController
import cv2
from robot_base import LimoBase
import rospy
from vision_detector import BallDetector

# Physical mounting offset (dx, dy, dz) in millimeters from the center of the
# MyCobot base to the Orbbec camera lens:
#   dx (+X): How many mm the camera lens sits in front of the arm base center
#   dy (+Y): How many mm the camera lens sits left/right of the arm centerline
#   dz (+Z): How many mm the camera lens sits above/below the arm base
CAM_TO_ARM_OFFSET_MM = (80.0, 0.0, -45.0)


def wait_for_target(detector, auto_pick=False, timeout=5.0):
  """Displays a resizable live feed and returns locked 3D arm coordinates.

  Args:
    detector (BallDetector): Initialized HSV + RGB-D detector instance.
    auto_pick (bool): If True, locks the first valid detection within `timeout`.
      If False, keeps the window open until Space is pressed to pick or 'q' to quit.
    timeout (float): Maximum seconds to wait when `auto_pick=True`.

  Returns:
    tuple: (x_mm, y_mm, z_mm) target coordinates in the arm base frame, or None.
  """
  window_name = "LIMO Camera Feed"
  cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
  cv2.resizeWindow(window_name, 800, 600)

  end_time = rospy.Time.now() + rospy.Duration(timeout) if auto_pick else None
  rate = rospy.Rate(30)
  locked_coords = None

  while not rospy.is_shutdown():
    if end_time is not None and rospy.Time.now() >= end_time:
      break

    coords = detector.get_target_arm_coords(CAM_TO_ARM_OFFSET_MM)

    if detector.latest_annotated_frame is not None:
      frame = detector.latest_annotated_frame.copy()

      if coords is not None:
        status = (
            f"[{detector.color_name.upper()}] Arm Target: "
            f"X={coords[0]:.0f} Y={coords[1]:.0f} Z={coords[2]:.0f}mm"
        )
        hint = "Press SPACE to pick | 'q' to abort"
      else:
        status = f"[{detector.color_name.upper()}] Searching for ball..."
        hint = "Move ball into view | 'q' to abort"

      cv2.putText(
          frame, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 0, 0), 2
      )
      if not auto_pick:
        cv2.putText(
            frame, hint, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 0, 0), 2
        )

      cv2.imshow(window_name, frame)

    key = cv2.waitKey(1) & 0xFF
    if key in (ord("q"), 27):  # 'q' or ESC aborts
      locked_coords = None
      break
    elif key == ord("b"):
      detector.set_color("blue")
    elif key == ord("o"):
      detector.set_color("orange")
    elif key == ord("w"):
      detector.set_color("white")
    elif key == ord("y"):
      detector.set_color("yellow")
    elif key == ord("g"):
      detector.set_color("green")

    if auto_pick and coords is not None:
      locked_coords = coords
      cv2.waitKey(500)
      break
    elif not auto_pick and key == ord(" ") and coords is not None:
      locked_coords = coords
      break

    rate.sleep()

  return locked_coords


def main():
  # Initialize the ROS 1 node for this process
  rospy.init_node("limo_pickup_sequence", anonymous=True)

  # Instantiate hardware controllers and the HSV + RGB-D vision pipeline
  base = LimoBase()
  arm = ArmController(port="/dev/ttyACM0")
  detector = BallDetector(color="blue")

  # 1. Tuck the arm so it does not obstruct the depth camera while approaching
 
  rospy.loginfo("Loading YOLO Model...")
  script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
  model_file = os.path.join(script_dir,"/home/agilex/limo_ros2_ws/src/Soft-Eng---Robot-/best.pt")
  rospy.loginfo("Folding arm into safe transit pose...")
  detector = BallDetector(model_path=model_file, target_class_id=0)
  arm.reset_and_tuck()

  # 2. Drive the LIMO forward to the bin
  target_distance = 0.3  # meters
  drive_speed = 0.1      # meters per second
  rospy.loginfo(f"Driving {target_distance}m at {drive_speed} m/s...")
  base.drive_forward(distance=target_distance, speed=drive_speed)

  # 3. Locate the topmost target ball in 3D space (live resizable window)
  rospy.loginfo(
      "Camera preview open. Position ball and press SPACE to pick (or 'q' to quit)."
  )
  target_xyz = wait_for_target(detector, auto_pick=False, timeout=5.0)

  if target_xyz is None:
    rospy.logerr("No valid ball locked within depth range. Aborting pick.")
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
  finally:
    cv2.destroyAllWindows()
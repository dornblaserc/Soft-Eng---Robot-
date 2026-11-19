"""
File: main.py
Description:
  Main execution sequence for the AgileX LIMO autonomous ball-picking task.
"""

from arm_controller import ArmController
import cv2
from robot_base import LimoBase
import rospy
from vision_detector import BallDetector

# Physical mounting offset (dx, dy, dz) in mm from MyCobot base to camera lens
CAM_TO_ARM_OFFSET_MM = (80.0, 0.0, -45.0)


def wait_for_target(detector, auto_pick=False, timeout=5.0):
  window_name = "LIMO Camera Feed (Resizable)"
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
        dist_cm = detector.latest_target_cam_mm[2] / 10.0
        status = (
            f"[{detector.color_name.upper()}] Dist: {dist_cm:.1f}cm | "
            f"Arm: X={coords[0]:.0f} Y={coords[1]:.0f} Z={coords[2]:.0f}mm"
        )
        hint = "SPACE to pick | 'q' to quit"
      else:
        status = f"[{detector.color_name.upper()}] Searching..."
        hint = "Move ball into view | 'q' to quit"

      cv2.putText(frame, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
      if not auto_pick:
        cv2.putText(frame, hint, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 0, 0), 2)

      cv2.imshow(window_name, frame)

    key = cv2.waitKey(1) & 0xFF
    if key in (ord("q"), 27):
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
  rospy.init_node("limo_pickup_sequence", anonymous=True)

  base = LimoBase()
  arm = ArmController(port="/dev/ttyACM0")
  detector = BallDetector(color="blue")

  rospy.loginfo("Folding arm into safe transit pose...")
  arm.reset_and_tuck()

  target_distance = 0.3
  drive_speed = 0.1
  rospy.loginfo(f"Driving {target_distance}m at {drive_speed} m/s...")
  base.drive_forward(distance=target_distance, speed=drive_speed)

  rospy.loginfo("Camera preview open. Press SPACE to pick or 'q' to quit.")
  target_xyz = wait_for_target(detector, auto_pick=False, timeout=5.0)

  if target_xyz is None:
    rospy.logerr("No valid ball locked. Aborting pick.")
    return

  x_mm, y_mm, z_mm = target_xyz
  rospy.loginfo(
      f"Picking ball at arm coords: X={x_mm:.1f}mm, Y={y_mm:.1f}mm, Z={z_mm:.1f}mm"
  )

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
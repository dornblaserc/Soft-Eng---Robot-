"""
File: main.py
Description:
  Closed-loop visual servoing and ball-picking sequence for the AgileX LIMO:
    1. Folds the MyCobot 280 arm out of the camera's field of view.
    2. Tracks the target ball in a live resizable window, steering and driving
       toward it until it reaches pickup range without hitting it.
    3. Locks final 3D coordinates, picks the ball, and places it in the box.
"""

import math
from arm_controller import ArmController
import cv2
from Tests.in_progress.robot_base import LimoBase
import rospy
from vision_detector import BallDetector

# Physical mounting offset (dx, dy, dz) in mm from MyCobot base to camera lens
CAM_TO_ARM_OFFSET_MM = (80.0, 0.0, -45.0)

# Approach tuning parameters
STOP_DISTANCE_MM = 160.0   # Stop 16 cm from camera (~24 cm from arm base)
MAX_LINEAR_SPEED = 0.16    # m/s when far from target
MIN_LINEAR_SPEED = 0.07    # m/s when close to target
KP_ANGULAR = 1.6           # Steering proportional gain
MAX_ANGULAR_SPEED = 0.65   # rad/s steering clamp
LOST_TARGET_TIMEOUT = 0.6  # Seconds to hold still if ball briefly drops out


def approach_and_lock_target(base, detector):
  """Steers and drives the LIMO up to the ball, stopping at pickup distance."""
  window_name = "LIMO Camera Feed (Resizable)"
  cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
  cv2.resizeWindow(window_name, 800, 600)

  rate = rospy.Rate(20)
  last_seen_time = None
  locked_arm_coords = None

  while not rospy.is_shutdown():
    cam_coords = detector.latest_target_cam_mm
    arm_coords = detector.get_target_arm_coords(CAM_TO_ARM_OFFSET_MM)
    now = rospy.Time.now()

    linear_x = 0.0
    angular_z = 0.0

    if cam_coords is not None and arm_coords is not None:
      last_seen_time = now
      x_cam, _, z_cam = cam_coords

      # Bearing angle: +angle = ball is left (+angular.z), -angle = right (-angular.z)
      angle_rad = math.atan2(-x_cam, z_cam)
      angular_z = max(-MAX_ANGULAR_SPEED, min(MAX_ANGULAR_SPEED, KP_ANGULAR * angle_rad))

      if z_cam <= STOP_DISTANCE_MM and abs(angle_rad) < 0.20:
        # Close enough and centered—stop and settle chassis before picking
        base.stop()
        rospy.sleep(0.5)
        locked_arm_coords = detector.get_target_arm_coords(CAM_TO_ARM_OFFSET_MM) or arm_coords
        status = f"[{detector.color_name.upper()}] LOCKED at {z_cam / 10.0:.1f}cm - Picking!"
      else:
        # Slow down if turning sharply or getting close to the ball
        turn_scale = max(0.25, 1.0 - (abs(angle_rad) / 0.7))
        dist_scale = min(1.0, max(0.0, (z_cam - STOP_DISTANCE_MM) / 350.0))
        raw_speed = MIN_LINEAR_SPEED + (MAX_LINEAR_SPEED - MIN_LINEAR_SPEED) * dist_scale
        linear_x = raw_speed * turn_scale if z_cam > STOP_DISTANCE_MM else 0.0

        base.set_velocity(linear_x=linear_x, angular_z=angular_z)
        status = (
            f"[{detector.color_name.upper()}] Dist: {z_cam / 10.0:.1f}cm | "
            f"Lin: {linear_x:.2f} Ang: {angular_z:+.2f}"
        )
    else:
      base.stop()
      if last_seen_time is not None and (now - last_seen_time).to_sec() < LOST_TARGET_TIMEOUT:
        status = f"[{detector.color_name.upper()}] Re-acquiring..."
      else:
        status = f"[{detector.color_name.upper()}] Searching for ball..."

    if detector.latest_annotated_frame is not None:
      frame = detector.latest_annotated_frame.copy()
      cv2.putText(frame, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
      cv2.putText(
          frame,
          "Keys: b/o/w/y/g = Color | 'q' = Stop & Quit",
          (10, 60),
          cv2.FONT_HERSHEY_SIMPLEX,
          0.5,
          (255, 0, 0),
          2,
      )
      cv2.imshow(window_name, frame)

    key = cv2.waitKey(1) & 0xFF
    if key in (ord("q"), 27):
      base.stop()
      return None
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

    if locked_arm_coords is not None:
      break

    rate.sleep()

  base.stop()
  return locked_arm_coords


def main():
  rospy.init_node("limo_pickup_sequence", anonymous=True)

  base = LimoBase()
  arm = ArmController(port="/dev/ttyACM0")
  detector = BallDetector(color="blue")

  rospy.loginfo("Folding arm into safe transit pose...")
  arm.reset_and_tuck()

  rospy.loginfo("Searching and driving to ball...")
  target_xyz = approach_and_lock_target(base, detector)

  if target_xyz is None:
    rospy.logerr("Aborted before reaching ball.")
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
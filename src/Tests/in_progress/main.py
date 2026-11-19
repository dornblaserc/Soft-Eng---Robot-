"""
File: main.py
Description:
  Two-stage visual servoing and blind final roll-in for the AgileX LIMO:
    1. Steers and drives toward the ball while it is in the camera's vertical FOV.
    2. Once the ball reaches the lower FOV handoff distance (36 cm), locks its 3D
       position and drives straight forward the remaining distance to pickup range.
    3. Picks the ball with the MyCobot 280 and places it in the left box.
"""

import math
from arm_controller import ArmController
import cv2
from Tests.in_progress.robot_base import LimoBase
import rospy
from vision_detector import BallDetector

# Physical mounting offset (dx, dy, dz) in mm from MyCobot base to camera lens
CAM_TO_ARM_OFFSET_MM = (80.0, 0.0, -45.0)

# Approach and handoff tuning parameters
HANDOFF_DISTANCE_MM = 360.0  # Distance (mm) before ball exits bottom of camera FOV
STOP_DISTANCE_MM = 160.0     # Final pickup distance (mm) from camera lens
MAX_LINEAR_SPEED = 0.16      # m/s when far from target
MIN_LINEAR_SPEED = 0.07      # m/s when close to target
KP_ANGULAR = 1.6             # Steering proportional gain
MAX_ANGULAR_SPEED = 0.65     # rad/s steering clamp
LOST_TARGET_TIMEOUT = 0.5    # Seconds to wait before assuming ball exited bottom FOV


def cam_to_arm_coords(x_cam, y_cam, z_cam):
  ox, oy, oz = CAM_TO_ARM_OFFSET_MM
  return (z_cam + ox, -x_cam + oy, -y_cam + oz)


def approach_and_lock_target(base, detector):
  """Steers up to the handoff line, then drives the remaining blind distance."""
  window_name = "LIMO Camera Feed (Resizable)"
  cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
  cv2.resizeWindow(window_name, 800, 600)

  rate = rospy.Rate(20)
  last_valid_cam = None
  last_seen_time = None
  handoff_cam = None

  while not rospy.is_shutdown():
    cam_coords = detector.latest_target_cam_mm
    now = rospy.Time.now()

    if cam_coords is not None:
      x_cam, y_cam, z_cam = cam_coords
      last_valid_cam = (x_cam, y_cam, z_cam)
      last_seen_time = now

      angle_rad = math.atan2(-x_cam, z_cam)
      angular_z = max(-MAX_ANGULAR_SPEED, min(MAX_ANGULAR_SPEED, KP_ANGULAR * angle_rad))

      if z_cam <= HANDOFF_DISTANCE_MM and abs(angle_rad) < 0.20:
        base.stop()
        handoff_cam = (x_cam, y_cam, z_cam)
        status = f"[{detector.color_name.upper()}] Handoff at {z_cam / 10.0:.1f}cm - Rolling in..."
      else:
        turn_scale = max(0.25, 1.0 - (abs(angle_rad) / 0.7))
        dist_scale = min(1.0, max(0.0, (z_cam - HANDOFF_DISTANCE_MM) / 350.0))
        raw_speed = MIN_LINEAR_SPEED + (MAX_LINEAR_SPEED - MIN_LINEAR_SPEED) * dist_scale
        linear_x = raw_speed * turn_scale if z_cam > HANDOFF_DISTANCE_MM else 0.0

        base.set_velocity(linear_x=linear_x, angular_z=angular_z)
        status = (
            f"[{detector.color_name.upper()}] Dist: {z_cam / 10.0:.1f}cm | "
            f"Lin: {linear_x:.2f} Ang: {angular_z:+.2f}"
        )
    else:
      base.stop()
      # If the ball was close and centered right before dropping below the FOV, finish roll-in
      if (
          last_valid_cam is not None
          and last_valid_cam[2] < 500.0
          and last_seen_time is not None
          and (now - last_seen_time).to_sec() >= LOST_TARGET_TIMEOUT
      ):
        handoff_cam = last_valid_cam
        status = f"[{detector.color_name.upper()}] Exited bottom FOV - Rolling in..."
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

    if handoff_cam is not None:
      break

    rate.sleep()

  base.stop()
  if handoff_cam is None:
    return None

  # Drive straight forward the remaining distance after the ball exits the camera FOV
  hx, hy, hz = handoff_cam
  remaining_mm = max(0.0, hz - STOP_DISTANCE_MM)
  rospy.loginfo(f"Driving final {remaining_mm / 10.0:.1f} cm to pickup position...")
  base.drive_forward(distance=remaining_mm / 1000.0, speed=0.08)
  rospy.sleep(0.4)

  final_z_cam = hz - remaining_mm
  return cam_to_arm_coords(hx, hy, final_z_cam)


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
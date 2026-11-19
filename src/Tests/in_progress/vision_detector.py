"""
File: vision_detector.py
Description:
  Detects ping pong balls using HSV color segmentation, contour circularity,
  and 40 mm known-size pinhole distance estimation (eliminates the IR depth blind spot).

  Standalone live test:
    python3 src/Tests/in_progress/vision_detector.py
"""

import cv2
from cv_bridge import CvBridge
import numpy as np
import rospy
from sensor_msgs.msg import CameraInfo, Image


class BallDetector:
  """Detects ping pong balls and estimates 3D position from RGB + CameraInfo."""

  BALL_DIAMETER_MM = 40.0  # Standard ping pong ball diameter in mm

  COLOR_PRESETS = {
      "blue": ((95, 100, 70), (130, 255, 255)),
      "orange": ((5, 110, 100), (22, 255, 255)),
      "yellow": ((20, 90, 100), (35, 255, 255)),
      "white": ((0, 0, 185), (180, 45, 255)),
      "green": ((36, 80, 70), (85, 255, 255)),
  }

  def __init__(self, model_path=None, target_class_id=0, color="blue"):
    self.bridge = CvBridge()
    self.color_name = color if color in self.COLOR_PRESETS else "blue"
    self.hsv_lower, self.hsv_upper = self.COLOR_PRESETS[self.color_name]

    self.intrinsics = None            # (fx, fy, cx, cy)
    self.latest_target_cam_mm = None  # (X_cam, Y_cam, Z_cam) in mm
    self.latest_annotated_frame = None

    published = [t[0] for t in rospy.get_published_topics()]
    cam_ns = "/camera/color" if "/camera/color/image_raw" in published else "/camera/rgb"

    self.info_sub = rospy.Subscriber(
        f"{cam_ns}/camera_info", CameraInfo, self._info_cb
    )
    self.color_sub = rospy.Subscriber(
        f"{cam_ns}/image_raw", Image, self._image_cb, queue_size=1
    )

  def set_color(self, color_name):
    if color_name in self.COLOR_PRESETS:
      self.color_name = color_name
      self.hsv_lower, self.hsv_upper = self.COLOR_PRESETS[color_name]
      rospy.loginfo(f"Switched ball detection color to: {color_name}")

  def _info_cb(self, msg):
    if self.intrinsics is None:
      self.intrinsics = (msg.K[0], msg.K[4], msg.K[2], msg.K[5])
      self.info_sub.unregister()

  def _image_cb(self, color_msg):
    color_frame = self.bridge.imgmsg_to_cv2(color_msg, desired_encoding="bgr8")
    display_frame = color_frame.copy()

    if self.intrinsics is None:
      self.latest_annotated_frame = display_frame
      return

    # 1. Blur and convert BGR to HSV
    blurred = cv2.GaussianBlur(color_frame, (5, 5), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    # 2. Color threshold + light morphology so distant balls are not erased
    mask = cv2.inRange(hsv, np.array(self.hsv_lower), np.array(self.hsv_upper))
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    fx, fy, cx, cy = self.intrinsics
    best_target = None

    for cnt in contours:
      area = cv2.contourArea(cnt)
      if area < 40:
        continue

      perimeter = cv2.arcLength(cnt, True)
      if perimeter == 0:
        continue

      # Relaxed circularity handles glare highlights on plastic balls
      circularity = (4.0 * np.pi * area) / (perimeter * perimeter)
      if circularity < 0.40:
        continue

      bx, by, bw, bh = cv2.boundingRect(cnt)
      aspect_ratio = float(bw) / float(bh)
      if not (0.55 <= aspect_ratio <= 1.75):
        continue

      # Enclosing circle gives accurate center and diameter even with partial glare
      (center_x, center_y), radius = cv2.minEnclosingCircle(cnt)
      diameter_px = 2.0 * radius
      if diameter_px < 8.0:
        continue

      # Distance from known 40 mm ball diameter: Z = (real_diameter * fx) / pixel_diameter
      z_mm = (self.BALL_DIAMETER_MM * fx) / diameter_px
      if z_mm < 50.0 or z_mm > 2000.0:
        continue

      u, v = int(center_x), int(center_y)
      x_mm = (u - cx) * z_mm / fx
      y_mm = (v - cy) * z_mm / fy

      # Draw blue bounding box (BGR: 255, 0, 0), center dot, and distance label
      cv2.rectangle(display_frame, (bx, by), (bx + bw, by + bh), (255, 0, 0), 2)
      cv2.circle(display_frame, (u, v), 4, (255, 0, 0), -1)
      cv2.putText(
          display_frame,
          f"{z_mm / 10.0:.1f} cm",
          (bx, max(20, by - 8)),
          cv2.FONT_HERSHEY_SIMPLEX,
          0.6,
          (255, 0, 0),
          2,
      )

      if best_target is None or z_mm < best_target[2]:
        best_target = (x_mm, y_mm, z_mm)

    self.latest_target_cam_mm = best_target
    self.latest_annotated_frame = display_frame

  def get_target_arm_coords(self, cam_to_arm_offset_mm=(80.0, 0.0, -45.0)):
    """Transforms 3D camera coordinates (mm) into MyCobot base coordinates (mm)."""
    if self.latest_target_cam_mm is None:
      return None

    x_cam, y_cam, z_cam = self.latest_target_cam_mm
    ox, oy, oz = cam_to_arm_offset_mm
    return (z_cam + ox, -x_cam + oy, -y_cam + oz)


if __name__ == "__main__":
  rospy.init_node("vision_detector_standalone", anonymous=True)
  detector = BallDetector(color="blue")

  window_name = "LIMO Ball Detector (Resizable)"
  cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
  cv2.resizeWindow(window_name, 800, 600)

  print("Keys: 'b'=Blue | 'o'=Orange | 'w'=White | 'y'=Yellow | 'g'=Green | 'q'=Quit")

  rate = rospy.Rate(30)
  while not rospy.is_shutdown():
    if detector.latest_annotated_frame is not None:
      frame = detector.latest_annotated_frame.copy()
      arm_coords = detector.get_target_arm_coords()

      if arm_coords is not None:
        dist_cm = detector.latest_target_cam_mm[2] / 10.0
        status = (
            f"[{detector.color_name.upper()}] Dist: {dist_cm:.1f}cm | "
            f"Arm: X={arm_coords[0]:.0f} Y={arm_coords[1]:.0f} Z={arm_coords[2]:.0f}mm"
        )
      else:
        status = f"[{detector.color_name.upper()}] Searching..."

      cv2.putText(frame, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
      cv2.imshow(window_name, frame)

    key = cv2.waitKey(1) & 0xFF
    if key in (ord("q"), 27):
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

    rate.sleep()

  cv2.destroyAllWindows()
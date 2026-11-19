#!/usr/bin/env python3
"""File: vision_detector.py
Description:
  Detects ping pong balls using OpenCV HSV color segmentation, contour circularity
  filtering, and Orbbec DaBai RGB-D depth de-projection.

  Can be imported by main.py OR run directly by itself to test the camera live:
    python3 src/Tests/in_progress/vision_detector.py
    
  Can be ran on its own with: 
  source /opt/ros/noetic/setup.bash && source /home/agilex/agilex_ws/devel/setup.bash
  roslaunch astra_camera dabai_u3.launch > /dev/null 2>&1 &
  sleep 4
  python3 src/Tests/in_progress/vision_detector.py
  
  OR
  
  Changing the python3 call in setup.sh
"""

import cv2
from cv_bridge import CvBridge
import message_filters
import numpy as np
import rospy
from sensor_msgs.msg import CameraInfo, Image


class BallDetector:
  """Detects spherical ping pong balls via HSV color + circularity + RGB-D depth."""

  # Preset HSV ranges: (Lower_H, Lower_S, Lower_V), (Upper_H, Upper_S, Upper_V)
  COLOR_PRESETS = {
      "orange": ((5, 110, 100), (22, 255, 255)),
      "yellow": ((20, 90, 100), (35, 255, 255)),
      "white": ((0, 0, 185), (180, 45, 255)),
      "green": ((36, 80, 70), (85, 255, 255)),
      "blue": ((95, 100, 70), (130, 255, 255)),
  }

  def __init__(self, model_path=None, target_class_id=0, color="orange"):
    """Initializes the HSV + Depth ball detector and ROS 1 camera subscribers.

    Note: model_path and target_class_id are kept as optional parameters so existing
    calls in main.py do not break.
    """
    self.bridge = CvBridge()
    self.color_name = color if color in self.COLOR_PRESETS else "orange"
    self.hsv_lower, self.hsv_upper = self.COLOR_PRESETS[self.color_name]

    self.intrinsics = None            # (fx, fy, cx, cy)
    self.latest_target_cam_mm = None  # (X_cam, Y_cam, Z_cam) in mm
    self.latest_annotated_frame = None

    # Auto-detect whether the Orbbec driver publishes to /camera/color or /camera/rgb
    published = [t[0] for t in rospy.get_published_topics()]
    cam_ns = "/camera/color" if "/camera/color/image_raw" in published else "/camera/rgb"

    self.info_sub = rospy.Subscriber(
        f"{cam_ns}/camera_info", CameraInfo, self._info_cb
    )
    self.color_sub = message_filters.Subscriber(f"{cam_ns}/image_raw", Image)
    self.depth_sub = message_filters.Subscriber("/camera/depth/image_raw", Image)
    self.info_sub = rospy.Subscriber(
        f"{cam_ns}/camera_info", CameraInfo, self._info_cb
    )
    self.color_sub = message_filters.Subscriber(f"{cam_ns}/image_raw", Image)
    self.depth_sub = message_filters.Subscriber("/camera/depth/image_raw", Image)

    self.ts = message_filters.ApproximateTimeSynchronizer(
        [self.color_sub, self.depth_sub], queue_size=10, slop=0.05
    )
    self.ts.registerCallback(self._synced_cb)
    self.ts = message_filters.ApproximateTimeSynchronizer(
        [self.color_sub, self.depth_sub], queue_size=10, slop=0.05
    )
    self.ts.registerCallback(self._synced_cb)

  def set_color(self, color_name):
    """Switches the active ping pong ball HSV color preset."""
    if color_name in self.COLOR_PRESETS:
      self.color_name = color_name
      self.hsv_lower, self.hsv_upper = self.COLOR_PRESETS[color_name]
      rospy.loginfo(f"Switched ball detection color to: {color_name}")

  def _info_cb(self, msg):
    """Stores the camera lens focal lengths (fx, fy) and optical center (cx, cy)."""
    if self.intrinsics is None:
      self.intrinsics = (msg.K[0], msg.K[4], msg.K[2], msg.K[5])
      self.info_sub.unregister()

  def _synced_cb(self, color_msg, depth_msg):
    """Processes synchronized RGB and Depth frames to locate the topmost ball."""
    if self.intrinsics is None:
      return

    color_frame = self.bridge.imgmsg_to_cv2(color_msg, desired_encoding="bgr8")
    depth_frame = self.bridge.imgmsg_to_cv2(depth_msg, desired_encoding="passthrough")
    display_frame = color_frame.copy()

    # 1. Blur slightly and convert BGR image to HSV color space
    blurred = cv2.GaussianBlur(color_frame, (7, 7), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    # 2. Threshold for the target ball color and clean up noise with morphological ops
    mask = cv2.inRange(hsv, np.array(self.hsv_lower), np.array(self.hsv_upper))
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=2)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)

    # 3. Find external contours in the binary color mask
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    fx, fy, cx, cy = self.intrinsics
    best_target = None
    h, w = depth_frame.shape[:2]

    for cnt in contours:
      area = cv2.contourArea(cnt)
      if area < 150:  # Ignore tiny background speckles
        continue

      perimeter = cv2.arcLength(cnt, True)
      if perimeter == 0:
        continue

      # Circularity = 1.0 for a perfect circle; reject non-round shapes (< 0.60)
      circularity = (4.0 * np.pi * area) / (perimeter * perimeter)
      if circularity < 0.60:
        continue

      bx, by, bw, bh = cv2.boundingRect(cnt)
      aspect_ratio = float(bw) / float(bh)
      if not (0.65 <= aspect_ratio <= 1.45):
        continue

      # Center pixel (u, v) of the ball
      u = bx + bw // 2
      v = by + bh // 2

      # Draw blue bounding box (BGR: 255, 0, 0) and center dot
      cv2.rectangle(display_frame, (bx, by), (bx + bw, by + bh), (255, 0, 0), 2)
      cv2.circle(display_frame, (u, v), 4, (255, 0, 0), -1)

      if not (0 <= u < w and 0 <= v < h):
        continue

      # Read median depth in a 5x5 window around the ball center
      patch = depth_frame[max(0, v - 2):min(h, v + 3), max(0, u - 2):min(w, u + 3)]
      valid = patch[patch > 0]
      if len(valid) == 0:
        # Ball is detected in 2D, but too close (<15cm) for the depth sensor
        cv2.putText(
            display_frame,
            "No Depth (<15cm?)",
            (bx, max(20, by - 8)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 0, 0),
            2,
        )
        continue

      raw_depth = float(np.median(valid))
      z_mm = raw_depth * 1000.0 if depth_msg.encoding == "32FC1" else raw_depth
      if z_mm < 100.0 or z_mm > 700.0:
        continue

      # De-project 2D pixel + depth into 3D camera optical coordinates (mm)
      x_mm = (u - cx) * z_mm / fx
      y_mm = (v - cy) * z_mm / fy

      cv2.putText(
          display_frame,
          f"X:{int(x_mm)} Y:{int(y_mm)} Z:{int(z_mm)}mm",
          (bx, max(20, by - 8)),
          cv2.FONT_HERSHEY_SIMPLEX,
          0.5,
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


# ==============================================================================
# Standalone Live Testing Mode
# ==============================================================================
if __name__ == "__main__":
  rospy.init_node("vision_detector_standalone", anonymous=True)
  detector = BallDetector(color="orange")

  window_name = "LIMO Ball Detector (Resizable)"
  cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
  cv2.resizeWindow(window_name, 800, 600)

  print("==========================================================")
  print("Live Camera Feed Started!")
  print("  Press 'o' = Orange | 'w' = White | 'y' = Yellow | 'g' = Green")
  print("  Press 'q' or ESC inside the camera window to quit.")
  print("==========================================================")

  rate = rospy.Rate(30)
  while not rospy.is_shutdown():
    if detector.latest_annotated_frame is not None:
      frame = detector.latest_annotated_frame.copy()
      arm_coords = detector.get_target_arm_coords()

      # Show status banner at top of window
      status = f"Color: {detector.color_name.upper()} | "
      if arm_coords is not None:
        status += f"Arm Target: X={arm_coords[0]:.0f} Y={arm_coords[1]:.0f} Z={arm_coords[2]:.0f} mm"
      else:
        status += "Searching for ball..."

      cv2.putText(frame, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 0, 0), 2)
      cv2.imshow(window_name, frame)

    key = cv2.waitKey(1) & 0xFF
    if key in (ord("q"), 27):
      break
    elif key == ord("o"):
      detector.set_color("orange")
    elif key == ord("w"):
      detector.set_color("white")
    elif key == ord("y"):
      detector.set_color("yellow")
    elif key == ord("g"):
      detector.set_color("green")
    elif key == ord("b"):
      detector.set_color("blue")

    rate.sleep()

  cv2.destroyAllWindows()
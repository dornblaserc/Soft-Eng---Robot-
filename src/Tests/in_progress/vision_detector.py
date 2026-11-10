"""
File: vision_detector.py
Description:
  Detects ping pong balls in a bin using a YOLO instance segmentation model and
  an Orbbec DaBai RGB-D depth camera.

  How 3D localization works in this module:
    1. Camera Intrinsics: Reads lens focal lengths (fx, fy) and optical center (cx, cy).
    2. Synchronization: Pairs each RGB color frame with its matching depth frame.
    3. 2D Detection: Runs YOLO segmentation on the RGB frame to find the pixel center
       (u, v) of each ball matching the target class ID.
    4. Depth Lookup: Reads the distance Z (in millimeters) from the depth image at (u, v).
    5. 3D De-projection: Converts 2D pixel (u, v) + depth Z into 3D Camera Coordinates.
    6. Frame Transformation: Converts 3D Camera Coordinates into 3D MyCobot Arm Coordinates.
"""

import cv2
from cv_bridge import CvBridge
import message_filters
import numpy as np
import rospy
from sensor_msgs.msg import CameraInfo, Image
from ultralytics import YOLO


class BallDetector:
  """Subscribes to RGB-D camera streams and computes 3D pick coordinates for the topmost ball."""

  def __init__(self, model_path="ping_pong_seg.pt", target_class_id=0):
    """Initializes the YOLO model and ROS camera subscribers.

    Args:
      model_path (str): File path to the trained YOLO weights (.pt, .onnx, or .engine).
      target_class_id (int): Numeric class index corresponding to the desired ball color.
    """
    # CvBridge converts ROS sensor_msgs/Image packets into OpenCV numpy arrays
    self.bridge = CvBridge()
    self.model = YOLO(model_path, task="segment")
    self.target_class_id = target_class_id

    # Stores pinhole camera intrinsic parameters: (fx, fy, cx, cy)
    self.intrinsics = None

    # Stores the latest detected ball position (X_cam, Y_cam, Z_cam) in millimeters
    self.latest_target_cam_mm = None

    # Subscribe once to camera_info to retrieve the lens calibration matrix
    self.info_sub = rospy.Subscriber(
        "/camera/color/camera_info", CameraInfo, self._info_cb
    )

    # Subscribe to both the color stream and the hardware-aligned depth stream
    self.color_sub = message_filters.Subscriber("/camera/color/image_raw", Image)
    self.depth_sub = message_filters.Subscriber("/camera/depth/image_raw", Image)

    # ApproximateTimeSynchronizer pairs RGB and Depth messages whose timestamps
    # are within 50 milliseconds (slop=0.05) so moving objects do not misalign
    self.ts = message_filters.ApproximateTimeSynchronizer(
        [self.color_sub, self.depth_sub], queue_size=10, slop=0.05
    )
    self.ts.registerCallback(self._synced_cb)

  def _info_cb(self, msg):
    """Extracts lens focal lengths and optical center from the 3x3 intrinsic matrix K.

    The flattened 9-element matrix K in CameraInfo is structured as:
      [ fx,  0, cx,
         0, fy, cy,
         0,  0,  1 ]
    """
    if self.intrinsics is None:
      fx = msg.K[0]  # Horizontal focal length in pixels
      cx = msg.K[2]  # Horizontal optical center in pixels
      fy = msg.K[4]  # Vertical focal length in pixels
      cy = msg.K[5]  # Vertical optical center in pixels
      self.intrinsics = (fx, fy, cx, cy)
      # Unregister after receiving once since lens intrinsics never change
      self.info_sub.unregister()

  def _synced_cb(self, color_msg, depth_msg):
    """Callback triggered whenever a matched pair of RGB and Depth frames arrives."""
    if self.intrinsics is None:
      return

    # Convert ROS image messages into standard OpenCV matrices
    color_frame = self.bridge.imgmsg_to_cv2(color_msg, desired_encoding="bgr8")
    depth_frame = self.bridge.imgmsg_to_cv2(depth_msg, desired_encoding="passthrough")

    # Run neural network inference on the RGB image (minimum confidence 60%)
    results = self.model(color_frame, verbose=False, conf=0.6)[0]
    if results.boxes is None or len(results.boxes) == 0:
      self.latest_target_cam_mm = None
      return

    fx, fy, cx, cy = self.intrinsics
    best_target = None  # Holds (X, Y, Z) of the ball closest to the camera

    for i, box in enumerate(results.boxes):
      # Ignore balls that do not match the requested color class ID
      if int(box.cls[0]) != self.target_class_id:
        continue

      # Find the 2D pixel center (u, v) of the ball.
      # Prefer the segmentation mask centroid (accurate even if balls touch),
      # falling back to the bounding box center if masks are unavailable.
      if results.masks is not None:
        mask_pts = results.masks.xy[i]
        if len(mask_pts) == 0:
          continue
        u = int(np.mean(mask_pts[:, 0]))
        v = int(np.mean(mask_pts[:, 1]))
      else:
        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
        u = int((x1 + x2) / 2)
        v = int((y1 + y2) / 2)

      # Verify pixel (u, v) lies inside the image boundaries
      h, w = depth_frame.shape[:2]
      if not (0 <= u < w and 0 <= v < h):
        continue

      # Extract a 3x3 pixel window around (u, v) from the depth image.
      # Taking the median of non-zero pixels prevents a single dead depth pixel
      # from ruining the distance reading.
      patch = depth_frame[max(0, v - 1):min(h, v + 2), max(0, u - 1):min(w, u + 2)]
      valid = patch[patch > 0]
      if len(valid) == 0:
        continue

      raw_depth = float(np.median(valid))

      # Standardize depth Z into millimeters:
      # '16UC1' depth images are already in mm; '32FC1' depth images are in meters.
      z_mm = raw_depth * 1000.0 if depth_msg.encoding == "32FC1" else raw_depth

      # Reject noisy depth readings closer than 10 cm or farther than 60 cm
      if z_mm < 100.0 or z_mm > 600.0:
        continue

      # Pinhole Camera De-projection Math:
      # Converts 2D pixel (u, v) and depth (z_mm) into 3D Camera Optical Coordinates (mm).
      # In the standard ROS Camera Optical Frame:
      #   +Z points straight out of the lens (forward)
      #   +X points to the right of the image
      #   +Y points down toward the floor
      x_mm = (u - cx) * z_mm / fx
      y_mm = (v - cy) * z_mm / fy

      # Bin-Picking Priority:
      # Keep the ball with the smallest Z distance (closest to the camera / top of the pile)
      if best_target is None or z_mm < best_target[2]:
        best_target = (x_mm, y_mm, z_mm)

    self.latest_target_cam_mm = best_target

  def get_target_arm_coords(self, cam_to_arm_offset_mm=(80.0, 0.0, -45.0)):
    """Converts 3D Camera Optical coordinates into 3D MyCobot Base coordinates.

    Coordinate Axis Mapping:
      * Camera Optical Frame: +Z = Forward, +X = Right, +Y = Down
      * MyCobot Base Frame:   +X = Forward, +Y = Left,  +Z = Up

    Therefore:
      * Arm Forward (+X_arm) corresponds to Camera Depth (+Z_cam)
      * Arm Left    (+Y_arm) corresponds to negative Camera Right (-X_cam)
      * Arm Up      (+Z_arm) corresponds to negative Camera Down (-Y_cam)

    Args:
      cam_to_arm_offset_mm (tuple): Physical (dx, dy, dz) mounting position of the
        camera lens measured from the center of the MyCobot base in millimeters.

    Returns:
      tuple: (x_arm, y_arm, z_arm) in millimeters ready for MyCobot send_coords(),
             or None if no ball is currently detected.
    """
    if self.latest_target_cam_mm is None:
      return None

    x_cam, y_cam, z_cam = self.latest_target_cam_mm
    ox, oy, oz = cam_to_arm_offset_mm

    x_arm = z_cam + ox
    y_arm = -x_cam + oy
    z_arm = -y_cam + oz

    return x_arm, y_arm, z_arm
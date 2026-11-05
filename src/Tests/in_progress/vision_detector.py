import rospy
import cv2
import numpy as np
import message_filters
from sensor_msgs.msg import Image, CameraInfo
from cv_bridge import CvBridge
from ultralytics import YOLO


class BallDetector:

  def __init__(self, model_path="ping_pong_seg.pt", target_class_id=0):
    self.bridge = CvBridge()
    self.model = YOLO(model_path, task="segment")
    self.target_class_id = target_class_id

    self.intrinsics = None  # (fx, fy, cx, cy)
    self.latest_target_cam_mm = None  # (X_cam, Y_cam, Z_cam) in mm

    self.info_sub = rospy.Subscriber(
        "/camera/color/camera_info", CameraInfo, self._info_cb
    )

    # Synchronize RGB and hardware-registered Depth streams in ROS 1
    self.color_sub = message_filters.Subscriber("/camera/color/image_raw", Image)
    self.depth_sub = message_filters.Subscriber("/camera/depth/image_raw", Image)

    self.ts = message_filters.ApproximateTimeSynchronizer(
        [self.color_sub, self.depth_sub], queue_size=10, slop=0.05
    )
    self.ts.registerCallback(self._synced_cb)

  def _info_cb(self, msg):
    if self.intrinsics is None:
      fx = msg.K[0]
      cx = msg.K[2]
      fy = msg.K[4]
      cy = msg.K[5]
      self.intrinsics = (fx, fy, cx, cy)
      self.info_sub.unregister()

  def _synced_cb(self, color_msg, depth_msg):
    if self.intrinsics is None:
      return

    color_frame = self.bridge.imgmsg_to_cv2(color_msg, desired_encoding="bgr8")
    depth_frame = self.bridge.imgmsg_to_cv2(depth_msg, desired_encoding="passthrough")

    results = self.model(color_frame, verbose=False, conf=0.6)[0]
    if results.boxes is None or len(results.boxes) == 0:
      self.latest_target_cam_mm = None
      return

    fx, fy, cx, cy = self.intrinsics
    best_target = None

    for i, box in enumerate(results.boxes):
      if int(box.cls[0]) != self.target_class_id:
        continue

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

      h, w = depth_frame.shape[:2]
      if not (0 <= u < w and 0 <= v < h):
        continue

      # 3x3 median patch to filter depth sensor dropouts
      patch = depth_frame[max(0, v - 1):min(h, v + 2), max(0, u - 1):min(w, u + 2)]
      valid = patch[patch > 0]
      if len(valid) == 0:
        continue

      raw_depth = float(np.median(valid))
      # Convert meters to mm if encoding is 32FC1; 16UC1 is already in mm
      z_mm = raw_depth * 1000.0 if depth_msg.encoding == "32FC1" else raw_depth
      if z_mm < 100.0 or z_mm > 600.0:
        continue

      # De-project 2D pixel + depth into 3D camera optical coordinates (mm)
      # Optical frame: +Z forward, +X right, +Y down
      x_mm = (u - cx) * z_mm / fx
      y_mm = (v - cy) * z_mm / fy

      # Select ball closest to the camera (topmost in the pile)
      if best_target is None or z_mm < best_target[2]:
        best_target = (x_mm, y_mm, z_mm)

    self.latest_target_cam_mm = best_target

  def get_target_arm_coords(self, cam_to_arm_offset_mm=(80.0, 0.0, -45.0)):
    """Transforms 3D camera optical coordinates (mm) into MyCobot base coordinates (mm).

    Camera optical frame: +Z = forward, +X = right, +Y = down
    MyCobot base frame:   +X = forward, +Y = left,  +Z = up
    cam_to_arm_offset_mm: (dx, dy, dz) position of the camera lens relative to arm base.
    """
    if self.latest_target_cam_mm is None:
      return None

    x_cam, y_cam, z_cam = self.latest_target_cam_mm
    ox, oy, oz = cam_to_arm_offset_mm

    x_arm = z_cam + ox
    y_arm = -x_cam + oy
    z_arm = -y_cam + oz

    return x_arm, y_arm, z_arm
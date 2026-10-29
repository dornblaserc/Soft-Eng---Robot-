import cv2
import numpy as np


class BallDetector:

  def __init__(self, camera_index=0):
    self.cap = cv2.VideoCapture(camera_index)
    # Target frame dimensions
    self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    self.center_x = self.width // 2
    self.center_y = self.height // 2

  def get_ball_offset(self):
    """Returns (dx, dy) in pixels from the frame center, or None if no ball found."""
    ret, frame = self.cap.read()
    if not ret:
      return None

    # Example: HSV masking for an orange/red ball
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_bound = np.array([5, 120, 100])
    upper_bound = np.array([25, 255, 255])
    mask = cv2.inRange(hsv, lower_bound, upper_bound)

    contours, _ = cv2.findContours(
        mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    if contours:
      largest = max(contours, key=cv2.contourArea)
      if cv2.contourArea(largest) > 400:  # Noise threshold
        ((x, y), radius) = cv2.minEnclosingCircle(largest)
        # Error relative to image center
        dx = int(x - self.center_x)
        dy = int(y - self.center_y)
        return dx, dy

    return None

  def release(self):
    self.cap.release()
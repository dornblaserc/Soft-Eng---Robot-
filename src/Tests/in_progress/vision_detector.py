def __init__(self, model_path="ping_pong_seg.pt", target_class_id=0):
    self.bridge = CvBridge()
    self.model = YOLO(model_path, task="segment")
    self.target_class_id = target_class_id

    self.intrinsics = None
    self.latest_target_cam_mm = None

    # Auto-detect whether the driver publishes to /camera/color or /camera/rgb
    published = [t[0] for t in rospy.get_published_topics()]
    cam_ns = "/camera/color" if "/camera/color/image_raw" in published else "/camera/rgb"

    self.info_sub = rospy.Subscriber(
        f"{cam_ns}/camera_info", CameraInfo, self._info_cb
    )
    self.color_sub = message_filters.Subscriber(f"{cam_ns}/image_raw", Image)
    self.depth_sub = message_filters.Subscriber("/camera/depth/image_raw", Image)

    self.ts = message_filters.ApproximateTimeSynchronizer(
        [self.color_sub, self.depth_sub], queue_size=10, slop=0.05
    )
    self.ts.registerCallback(self._synced_cb)
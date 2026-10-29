from geometry_msgs.msg import Twist
import rospy


class LimoBase:

  def __init__(self):
    self.pub = rospy.Publisher("/cmd_vel", Twist, queue_size=10)
    self.rate = rospy.Rate(10)
    rospy.sleep(1)  # Allow publisher to register

  def drive_forward(self, distance, speed=0.1):
    cmd = Twist()
    cmd.linear.x = speed
    duration = rospy.Duration(abs(distance / speed))
    end_time = rospy.Time.now() + duration

    while not rospy.is_shutdown() and rospy.Time.now() < end_time:
      self.pub.publish(cmd)
      self.rate.sleep()

    self.stop()

  def stop(self):
    self.pub.publish(Twist())
    rospy.sleep(0.5)
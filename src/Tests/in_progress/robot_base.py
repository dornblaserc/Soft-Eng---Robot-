"""
File: robot_base.py
Description:
  Velocity and distance controller for the AgileX LIMO mobile base via /cmd_vel.
"""

from geometry_msgs.msg import Twist
import rospy


class LimoBase:
  """Publishes Twist velocity commands to /cmd_vel."""

  def __init__(self):
    self.cmd_pub = rospy.Publisher("/cmd_vel", Twist, queue_size=1)
    rospy.on_shutdown(self.stop)
    rospy.sleep(0.5)

  def set_velocity(self, linear_x=0.0, angular_z=0.0):
    """Sends continuous forward (m/s) and steering (rad/s) velocities."""
    msg = Twist()
    msg.linear.x = float(linear_x)
    msg.angular.z = float(angular_z)
    self.cmd_pub.publish(msg)

  def stop(self):
    """Immediately halts all wheel motion."""
    self.cmd_pub.publish(Twist())

  def drive_forward(self, distance, speed=0.1):
    """Drives straight forward for a fixed distance in meters."""
    if speed <= 0 or distance <= 0:
      return
    duration = distance / speed
    end_time = rospy.Time.now() + rospy.Duration(duration)
    rate = rospy.Rate(20)
    while not rospy.is_shutdown() and rospy.Time.now() < end_time:
      self.set_velocity(linear_x=speed, angular_z=0.0)
      rate.sleep()
    self.stop()

  def drive_backward(self, distance, speed=0.1):
    """Drives straight backward for a fixed distance in meters."""
    
    duration = abs(distance)/abs(speed)
    end_time = rospy.Time.now() + rospy.Duration(duration)
    rate = rospy.Rate(20)
    while not rospy.is_shutdown() and rospy.Time.now() < end_time:
      self.set_velocity(linear_x=-abs(speed), angular_z=0.0)
      rate.sleep()
    self.stop()
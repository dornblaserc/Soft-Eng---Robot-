"""
File: robot_base.py
Description:
  Provides a high-level interface for driving the AgileX LIMO rover base
  by publishing linear and angular velocity commands to the /cmd_vel ROS topic.
"""

from geometry_msgs.msg import Twist
import rospy


class LimoBase:
  """Controls forward movement and stopping for the AgileX LIMO mobile base."""

  def __init__(self):
    # Publisher that sends velocity vectors (Twist messages) to the wheel controller
    self.pub = rospy.Publisher("/cmd_vel", Twist, queue_size=10)
    # Control loop frequency of 10 Hz (10 updates per second)
    self.rate = rospy.Rate(10)
    # Brief pause to allow the ROS master to register the publisher connection
    rospy.sleep(1)

  def drive_forward(self, distance, speed=0.1):
    """Drives the robot straight ahead for a specified distance using open-loop timing.

    Args:
      distance (float): Target travel distance in meters.
      speed (float): Forward velocity in meters per second (positive = forward).
    """
    cmd = Twist()
    cmd.linear.x = speed

    # Calculate how long to publish velocity commands: time = distance / speed
    duration = rospy.Duration(abs(distance / speed))
    end_time = rospy.Time.now() + duration

    # Continuously publish the forward velocity until the target duration elapses
    while not rospy.is_shutdown() and rospy.Time.now() < end_time:
      self.pub.publish(cmd)
      self.rate.sleep()

    # Always send a zero-velocity command afterward so the robot comes to a halt
    self.stop()

  def stop(self):
    """Immediately halts all wheel motion by publishing an empty (zeroed) Twist message."""
    self.pub.publish(Twist())
    rospy.sleep(0.5)
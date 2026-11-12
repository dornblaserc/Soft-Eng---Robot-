# Test the turning ability of the LIMO ROS2 robot

import rospy
from geometry_msgs.msg import Twist


rospy.init_node("limo_turn")
pub = rospy.Publisher("/cmd_vel", Twist, queue_size=10)
rospy.sleep(1.0)  # let the publisher connect

cmd = Twist()
cmd.linear.x = 0.0     # m/s
cmd.angular.z = 0.5    # rad/s, positive = left/CCW

rate = rospy.Rate(20)
end = rospy.Time.now() + rospy.Duration(3.0)  # open-loop: turn for 3 s
while not rospy.is_shutdown() and rospy.Time.now() < end:
    pub.publish(cmd)
    rate.sleep()

pub.publish(Twist())  # stop
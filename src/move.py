#!/usr/bin/env python3
import rospy
from geometry_msgs.msg import Twist

rospy.init_node("move_test")
pub = rospy.Publisher("/cmd_vel", Twist, queue_size=10)
rospy.sleep(1) #let the publisher connect

rate = rospy.Rate(10)
cmd = Twist()
cmd.linear.x = 0.1 #m/s

end = rospy.Time.now() + rospy.Duration(5)
while not rospy.is_shutdown() and rospy.Time.now() < end:
    pub.publish(cmd)
    rate.sleep()

pub.publish(Twist()) #stop

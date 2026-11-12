# Test the turning ability of the LIMO ROS2 robot

import rospy
from geometry_msgs.msg import Twist


rospy.init_node("limo_turn")
pub = rospy.Publisher("/cmd_vel", Twist, queue_size=10)
rospy.sleep(1.0)  # let the publisher connect

# The values here can be negative to go either backwards or turn CW respectively
cmd = Twist()
cmd.linear.x = 0.1     # m/s to move the robot forward while turning. The lower the value the slower
cmd.angular.z = 0.2    # rad/s, positive = left/CCW how fast the wheels turn. The lower the value the slower

rate = rospy.Rate(20)  # rate that the loop will execute per second
end = rospy.Time.now() + rospy.Duration(3.0)  # open-loop: turn for 3 s
while not rospy.is_shutdown() and rospy.Time.now() < end:
    pub.publish(cmd)
    rate.sleep()

pub.publish(Twist())  # stop
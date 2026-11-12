import rospy
from geometry_msgs.msg import Twist

class RobotTurn:
    def turn(duration=3.0,turn_rate=20,linear_x=0.0,angular_z=0.5):
        rospy.init_node("limo_turn")
        pub = rospy.Publisher("/cmd_vel", Twist, queue_size=10)
        rospy.sleep(1.0)  # let the publisher connect

        cmd = Twist()
        cmd.linear.x = linear_x   # m/s
        cmd.angular.z = angular_z  # rad/s, positive = left/CCW

        rate = rospy.Rate(turn_rate)
        end = rospy.Time.now() + rospy.Duration(duration)  # open-loop: turn for 3 s
        while not rospy.is_shutdown() and rospy.Time.now() < end:
            pub.publish(cmd)
            rate.sleep()

        pub.publish(Twist())  # stop
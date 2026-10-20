from pymycobot.mycobot import MyCobot

mc = MyCobot("/dev/ttyACM0",115200,debug=True)

mc.get_angles()

from pymycobot import MyCobot280
import time

mc = MyCobot280("/dev/ttyACM0",115200)
#^ sets arm to ms variable
#dev/#### will have the # be different for each arm

mc.power_on() #activates arm
time.sleep(1)

mc.send_angles([0,0,0,0,0,0], 30) #default positions and speed
time.sleep(3)

mc.send_angles([0,90,-90,0,0,0], 30) #small right angle turns
time.sleep(3)

mc.send_angles([0,0,0,0,0,0,], 30) #return to start
time.sleep(3)

mc.set_gripper_state(0, 30) #activates gripper
time.sleep(3)

mc.set_gripper_value(100, 30) #100 = full open, 2nd ## = speed
time.sleep(3)

mc.set_gripper_value(0, 30) #0 = full close, 2nd ## = speed
time.sleep(3)

print(mc.get_angles()) #returns arm's current positions
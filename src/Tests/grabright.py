from pymycobot import MyCobot280
import time


mc = MyCobot280("/dev/ttyACM0",115200)
#^ sets arm to ms variable
#dev/#### will have the # be different for each arm
mc.power_on() #activates arm
time.sleep(1)
mc.set_gripper_state(0, 50) #activates gripper
time.sleep(3)

#Lines 15-18 reset the arm to a default position
mc.set_gripper_value(0, 50) #0 = full close, 2nd ## = speed
mc.send_angles([0,0,0,0,0,0,], 50) #return to start (for this file)
time.sleep(5)

mc.set_gripper_value(100, 50) #100 = full open, 2nd ## = speed
time.sleep(3)

mc.send_angles([14,0,0,0,135,0], 50) #servo 1 and 5
time.sleep(3)

mc.send_angles([14,140,-25,-15,135,0], 50) #servo 2,3,4
time.sleep(3)

mc.set_gripper_value(15, 50) #100 = full open, 2nd ## = speed
time.sleep(3)

mc.send_angles([5,-110,25,0,-45,0,], 50) #place in box
time.sleep(4)

mc.set_gripper_value(100, 50) #100 = full open, 2nd ## = speed
time.sleep(3)
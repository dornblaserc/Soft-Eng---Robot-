from pymycobot import MyCobot280
import time

mc = MyCobot280("/dev/ttyACM0",115200)
#^ sets arm to ms variable
#dev/#### will have the # be different for each arm

mc.power_on() #activates arm
time.sleep(1)

#All servo test below have a max distance of 140 degrees
#Only testing up to 120 for this file due to concerns with the
#arm possibly swinging around and banging on the LIMO Bot
#Servo 6 can turn farther, but should not extend the parameter
#of 180 degrees due to the cords in use (black & white)

mc.send_angles([0,0,0,0,0,0], 30) #default positions and speed
time.sleep(5)

mc.send_angles([120,0,0,0,0,0], 30) #servo 1 clockwise
time.sleep(5)

mc.send_angles([0,0,0,0,0,0], 30) #return to start
time.sleep(5)

mc.send_angles([-120,0,0,0,0,0], 30) #servo 1 counter-clockwise
time.sleep(5)

mc.send_angles([0,0,0,0,0,0], 30) #return to start
time.sleep(5)

mc.send_angles([0,120,0,0,0,0], 30) #servo 2 clockwise
time.sleep(5)

mc.send_angles([0,0,0,0,0,0], 30) #return to start
time.sleep(5)

mc.send_angles([0,-120,0,0,0,0], 30) #servo 2 counter-clockwise
time.sleep(5)

mc.send_angles([0,0,0,0,0,0], 30) #return to start
time.sleep(5)

mc.send_angles([0,0,120,0,0,0], 30) #servo 3 clockwise
time.sleep(5)

mc.send_angles([0,0,0,0,0,0], 30) #return to start
time.sleep(5)

mc.send_angles([0,0,-120,0,0,0], 30) #servo 3 counter-clockwise
time.sleep(5)

mc.send_angles([0,0,0,0,0,0], 30) #return to start
time.sleep(5)

mc.send_angles([0,0,0,120,0,0], 30) #servo 4 clockwise
time.sleep(5)

mc.send_angles([0,0,0,0,0,0], 30) #return to start
time.sleep(5)

mc.send_angles([0,0,0,-120,0,0], 30) #servo 4 counter-clockwise
time.sleep(5)

mc.send_angles([0,0,0,0,0,0], 30) #return to start
time.sleep(5)

mc.send_angles([0,0,0,0,120,0], 30) #servo 5 clockwise
time.sleep(5)

mc.send_angles([0,0,0,0,0,0], 30) #return to start
time.sleep(5)

mc.send_angles([0,0,0,0,-120,0], 30) #servo 5 counter-clockwise
time.sleep(5)

mc.send_angles([0,0,0,0,0,0], 30) #return to start
time.sleep(5)

mc.send_angles([0,0,0,0,0,120], 30) #servo 6 clockwise
time.sleep(5)

mc.send_angles([0,0,0,0,0,0], 30) #return to start
time.sleep(5)

mc.send_angles([0,0,0,0,0,-120], 30) #servo 6 counter-clockwise
time.sleep(5)

mc.send_angles([0,0,0,0,0,0], 30) #return to start
time.sleep(5)

print(mc.get_angles()) #returns arm's current positions
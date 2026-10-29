from pymycobot import MyCobot280
import time

"""
mc = MyCobot280("COM3", 115200)
time.sleep(2)

mc.set_color(255, 0, 0)   # LED on the arm's end should turn red
time.sleep(2)
mc.set_color(0, 0, 255)   # then blue
time.sleep(2)

mc.set_fresh_mode(1)
mc.release_all_servos()
time.sleep(1)
mc.focus_all_servos()
time.sleep(1)

mc.send_angles([20, 12, -86, 130, -6, 40], 30)
time.sleep(1)
print("moving:", mc.is_moving())
time.sleep(4)
print("angles:", mc.get_angles())
"""

mc = MyCobot280("COM3", 115200)
time.sleep(1)

mc.send_angles([100, 130, -90, 140, 20, 50], 30)
time.sleep(5)

mc.send_angles([0, 0, 0, 0, 0, 0], 30)
time.sleep(1)

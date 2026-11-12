import time
from pymycobot import MyCobot280

mc = MyCobot280("/dev/ttyACM0", 115200)
mc.power_on()
time.sleep(1)

print("Releasing servos... The arm will go limp.")
mc.release_all_servos()

input(
    "Place a ball in the pickup zone, manually position the gripper around it,\n"
    "and press Enter..."
)
mc.focus_all_servos()
time.sleep(1)

coords = mc.get_coords()
angles = mc.get_angles()
print(f"Recorded Angles: {angles}")
print(f"Recorded Coords [X, Y, Z, Rx, Ry, Rz]: {coords}")
print(f"Use GRIP_ORIENTATION = {coords[3:]} in arm_controller.py")
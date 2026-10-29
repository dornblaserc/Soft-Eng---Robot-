import time
from pymycobot import MyCobot280

mc = MyCobot280("/dev/ttyACM0", 115200)
mc.power_on()
time.sleep(1)

print("Releasing servos... The arm will go limp.")
mc.release_all_servos()

input(
    "1. Manually move the arm into the TUCKED pose.\nPress Enter when ready..."
)
tuck_angles = mc.get_angles()
print(f"TUCK_POSE = {tuck_angles}\n")

input(
    "2. Place the ball in front of the LIMO bumper.\n"
    "   Manually position the gripper around the ball.\n"
    "Press Enter when ready..."
)
pickup_angles = mc.get_angles()
print(f"PICKUP_POSE = {pickup_angles}\n")

# Re-lock servos to hold position
mc.focus_all_servos()
print("Servos locked. Calibration complete.")

'''
replace lines 12 to 14 in arm_controller.py
with the output from running python3 teach_angles.py
'''


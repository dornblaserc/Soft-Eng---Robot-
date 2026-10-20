import time
from pymycobot.mycobot import MyCobot
from pymycobot.genre import Angle


mc = MyCobot("/dev/ttyACM0", 115200)

# 控制吸泵      
def pub_pump(flag):
    if flag:
        mc.set_basic_output(2, 0)
        mc.set_basic_output(5, 0)
    else:
        mc.set_basic_output(2, 1)
        mc.set_basic_output(5, 1)

start_angles = [
    [0,0,0,0,0,0],
    [-1.05, -40.69, -146.86, 102.77, -0.14, 0],
    [-1.05, -61.20, -141.94, 116.71, 0, 0],

    [1.84, -39.28, -103.35, 57.21, -0.17, 0],
    [1.84, -57.83, -103.09, 74.88, -0.17, 0],

    [24.16, -41.22, -104.58, 59.5, -0.17, 0],
    [24.34, -56.33, -104.32, 73.38, -0.1, 0],
]

mid_angles = [
    [-73.12, -4.04, -100.45, 42.45, -0.1, -0.26],
    [-156.53, -62.84, -57.56, 40.95, -0.08, -0.26],
]

target_angles = [
    [-156.88, -76.81, -101.86, 92.19, -0.17, -0.26],
    [-156.79, -89.73, -89.03, 91.23, -0.43, -0.26],
    
    # [-156.44, -78.39, -69.78, 61.78, -5.0, -0.52],
    # [-157.14, -90.52, -61.61, 64.42, -5.09, 20],

    # [-154.42, -44.56, -110.21, 66.62, -4.21, -10.45],
    # [-154.51, -62.84, -104.58, 79.1, -4.48, 10]
    [-153.98, -39.63, -109.07, 57.56, -0.17, -0.26],
    [-153.98, -60.02, -108.98, 80.06, -0.17, -0.26],
    [-153.45, -20.03, -116.01, 48.07, -0.17, -0.26],
    [-153.36, -34.27, -114.16, 58.44, -0.17, -0.26],  
]

back_angles = [
    [-151.61, -37.52, -118.74, 66.97, -0.17, -0.26],
    [-152.05, -9.66, -118.74, 41.66, -0.17, -0.26], #抬高
    [-152.22, -66.26, -109.86, 87.71, -0.17, -0.26],
    [-155.56, -92.1, -86.66, 89.56, -0.17, -0.26],
]

def move_1():
    mc.send_angles(start_angles[0], 20)
    time.sleep(5)
    mc.send_angles(start_angles[1], 20)
    time.sleep(5)
    mc.send_angles(start_angles[2], 20)
    time.sleep(2)
    pub_pump(True)
    time.sleep(2)
    mc.send_angles(start_angles[1], 20)
    time.sleep(2)
    mc.send_angles(mid_angles[0], 20)
    time.sleep(2.5)
    mc.send_angles(target_angles[0], 20)
    time.sleep(5)
    mc.send_angles(target_angles[1], 20)
    time.sleep(2)
    pub_pump(False)
    time.sleep(3)
    mc.send_angles(target_angles[0], 20)
    time.sleep(2)

    mc.send_angles(mid_angles[0], 20)
    time.sleep(5)
    mc.send_angles(start_angles[3], 20)
    time.sleep(5)
    mc.send_angles(start_angles[4], 20)
    time.sleep(2)
    pub_pump(True)
    time.sleep(2)
    mc.send_angles(start_angles[3], 20)
    time.sleep(2)
    mc.send_angles(mid_angles[0], 20)
    time.sleep(2.5)
    mc.send_angles(mid_angles[1], 20)
    time.sleep(2.5)
    mc.send_angles(target_angles[2], 20)
    time.sleep(5)
    mc.send_angles(target_angles[3], 20)
    time.sleep(2)
    pub_pump(False)
    time.sleep(3)
    mc.send_angles(target_angles[2], 20)
    time.sleep(2)

    mc.send_angles(mid_angles[0], 20)
    time.sleep(5)
    mc.send_angles(start_angles[5], 20)
    time.sleep(6)
    mc.send_angles(start_angles[6], 20)
    time.sleep(2)
    pub_pump(True)
    time.sleep(2)
    mc.send_angles(start_angles[5], 20)
    time.sleep(2)
    mc.send_angles(mid_angles[0], 20)
    time.sleep(2.5)
    mc.send_angles(target_angles[4], 20)
    time.sleep(5)
    mc.send_angles(target_angles[5], 20)
    time.sleep(2)
    pub_pump(False)
    time.sleep(3)
    mc.send_angles(target_angles[4], 20)
    time.sleep(2)


#---------------2222
    mc.send_angles(back_angles[0], 20)
    time.sleep(2)
    pub_pump(True)
    time.sleep(2)
    mc.send_angles(back_angles[1], 20)
    time.sleep(3)
    mc.send_angles(mid_angles[0], 20)
    time.sleep(5)
    mc.send_angles(start_angles[5], 20)
    time.sleep(5)
    pub_pump(False)
    time.sleep(2)

    mc.send_angles(mid_angles[0], 20)
    time.sleep(5)
    mc.send_angles(back_angles[1], 20)
    time.sleep(3)

    mc.send_angles(back_angles[2], 20)
    time.sleep(3)
    pub_pump(True)
    time.sleep(2)
    mc.send_angles(back_angles[1], 20)
    time.sleep(3)
    mc.send_angles(mid_angles[0], 20)
    time.sleep(5)
    mc.send_angles(start_angles[3], 20)
    time.sleep(5)
    pub_pump(False)
    time.sleep(2)

    mc.send_angles(mid_angles[0], 20)
    time.sleep(5)
    mc.send_angles(back_angles[1], 20)
    time.sleep(3)

    mc.send_angles(back_angles[3], 20)
    time.sleep(3)
    pub_pump(True)
    time.sleep(2)
    mc.send_angles(back_angles[1], 20)
    time.sleep(3)
    mc.send_angles(mid_angles[0], 20)
    time.sleep(5)
    mc.send_angles(start_angles[1], 20)
    time.sleep(5)
    pub_pump(False)
    time.sleep(2)

def move_2():
    mc.send_angles(back_angles[0], 20)
    time.sleep(2)
    pub_pump(True)
    time.sleep(2)
    mc.send_angles(back_angles[1], 20)
    time.sleep(3)
    mc.send_angles(mid_angles[0], 20)
    time.sleep(5)
    mc.send_angles(start_angles[5], 20)
    time.sleep(5)
    pub_pump(False)
    time.sleep(2)

    mc.send_angles(mid_angles[0], 20)
    time.sleep(5)
    mc.send_angles(back_angles[1], 20)
    time.sleep(3)

    mc.send_angles(back_angles[2], 20)
    time.sleep(3)
    pub_pump(True)
    time.sleep(2)
    mc.send_angles(back_angles[1], 20)
    time.sleep(3)
    mc.send_angles(mid_angles[0], 20)
    time.sleep(5)
    mc.send_angles(start_angles[3], 20)
    time.sleep(5)
    pub_pump(False)
    time.sleep(2)

    mc.send_angles(mid_angles[0], 20)
    time.sleep(5)
    mc.send_angles(back_angles[1], 20)
    time.sleep(3)

    mc.send_angles(back_angles[3], 20)
    time.sleep(3)
    pub_pump(True)
    time.sleep(2)
    mc.send_angles(back_angles[1], 20)
    time.sleep(3)
    mc.send_angles(mid_angles[0], 20)
    time.sleep(5)
    mc.send_angles(start_angles[1], 20)
    time.sleep(5)
    pub_pump(False)
    time.sleep(2)


# 让机械臂放松，可以手动摆动机械臂
# mc.send_angles(start_angles[0], 20)
# time.sleep(5)
mc.release_all_servos()
time.sleep(7)
angle_datas = mc.get_angles()
print("关节角度为：")
print(angle_datas)

mc.set_servo_calibration(6)

# if __name__ =="__main__":
#     i = 99
#     while(i>0):
#         i=i-1
#         move_1()
#         time.sleep(2)
    # move_2()

    # pub_pump(False)
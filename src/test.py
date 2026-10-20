#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pymycobot.mycobot import MyCobot
import time


if __name__== "__main__":
    mc = MyCobot("/dev/ttyACM0", 115200)

    def point_orin():
        mc.send_angles([91.66, 122.78, -143.26, -19.07, -4.21, -43.59],30)    #收缩机械臂
        time.sleep(7)
        mc.send_angles([18.72, -54.49, -98.43, 65.83, -2.02, -27.68],30)    #到达目标点上方
        time.sleep(7)
        mc.send_angles([18.63, -71.98, -90.61, 74.44, -2.37, -27.24],30)    #到达夹取位置
        time.sleep(2)
        mc.set_gripper_value(50, 70)    #进行夹取
        time.sleep(3)
        mc.send_angles([91.66, 122.78, -143.26, -19.07, -4.21, -43.59],30)    #收缩机械臂
        time.sleep(7)

        #去到了目标点
        mc.send_angles([18.72, -54.49, -98.43, 65.83, -2.02, -27.68],30)    #到达投放目标点上方
        time.sleep(7)
        mc.send_angles([18.63, -71.98, -90.61, 74.44, -2.37, -27.24],30)    #到达目标投放点
        time.sleep(2)
        mc.set_gripper_value(245, 70)    #进行投放
        time.sleep(2)
        mc.send_angles([91.66, 122.78, -143.26, -19.07, -4.21, -43.59],30)    #收缩机械臂
        time.sleep(7)

    def point_nano():
        mc.send_angles([-84.63, 122.25, -143.17, -20.3, -4.83, -86.3],30)    #收缩机械臂
        time.sleep(5)
        mc.send_angles([11.25, -36.03, -128.32, 78.39, -4.13, -76.81],30)    #到达目标点上方
        time.sleep(5)
        mc.send_angles([11.6, -58.53, -121.64, 92.9, -3.51, -74.79],30)    #到达夹取位置
        time.sleep(2)
        mc.set_gripper_value(20, 70)    #进行夹取
        time.sleep(2)
        mc.send_angles([-84.63, 122.25, -143.17, -20.3, -4.83, -86.3],30)    #收缩机械臂
        time.sleep(5)

        #去到了目标点
        mc.send_angles([9.84, -85.6, -68.2, 68.02, -4.04, -75.84],30)     #到达投放目标点上方
        time.sleep(5)
        mc.send_angles([9.84, -100.45, -58.27, 75.41, -4.74, -74.79],30)    #到达目标投放点
        time.sleep(2)
        mc.set_gripper_value(245, 70)    #进行投放
        time.sleep(2)
        mc.send_angles([9.84, -85.6, -68.2, 68.02, -4.04, -75.84],20)     #到达投放目标点上方
        time.sleep(2)
        mc.send_angles([-84.63, 122.25, -143.17, -20.3, -4.83, -86.3],30)    #收缩机械臂
        time.sleep(7)

    # mc.send_angles([18.72, -54.49, -98.43, 65.83, -2.02, -27.68],30)    #到达投放目标点上方
    # time.sleep(7)
    # mc.release_all_servos()
    # time.sleep(7) 
    # angle_datas = mc.get_angles()
    # print("关节角度为：")
    # print(angle_datas)
    i=0
    while(i<100):
        i=i+1
        point_orin()
            




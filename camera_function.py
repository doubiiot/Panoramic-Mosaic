#-*- coding: utf-8 -*-
import cv2
import os
import time
from PTZ_control import *

start =False


def get_pic():
    cap = cv2.VideoCapture('rtsp://iot02:iot2015128@192.168.134.122:554//Streaming/Channels/1')
    if cap.isOpened():
        rval,frame = cap.read()
        file_name = time.strftime('%Y-%m-%d %H-%M-%S', time.localtime(time.time()))
        cv2.imwrite("tmp_data"+os.sep+file_name+".jpg", frame)
        return frame
    else:
        return False


def capture_by_step(id, dll, flag):
    pic_list = []
    count = 0
    global start
    while (start):
        count = count + 1
        print("Taking the picture " + str(count))
        frame = get_pic()
        pic_list.append(frame)  # picture list
        print("Take completed!")
        rotate_by_step(id, dll, flag)
    return pic_list


def set_start(flag):
    global start
    start = flag



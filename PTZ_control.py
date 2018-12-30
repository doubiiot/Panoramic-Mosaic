#-*- coding:utf-8 -*-
import ctypes
import threading
import time

mutex = threading.Lock()
class LPNET_DVR_DEVICEINFO_V30(ctypes.Structure):
    _fields_ = [
        ("sSerialNumber", ctypes.c_byte * 48),
        ("byAlarmInPortNum", ctypes.c_byte),
        ("byAlarmOutPortNum", ctypes.c_byte),
        ("byDiskNum", ctypes.c_byte),
        ("byDVRType", ctypes.c_byte),
        ("byChanNum", ctypes.c_byte),
        ("byStartChan", ctypes.c_byte),
        ("byAudioChanNum", ctypes.c_byte),
        ("byIPChanNum", ctypes.c_byte),
        ("byZeroChanNum", ctypes.c_byte),
        ("byMainProto", ctypes.c_byte),
        ("bySubProto", ctypes.c_byte),
        ("bySupport", ctypes.c_byte),
        ("bySupport1", ctypes.c_byte),
        ("bySupport2", ctypes.c_byte),
        ("wDevType", ctypes.c_uint16),
        ("bySupport3", ctypes.c_byte),
        ("byMultiStreamProto", ctypes.c_byte),
        ("byStartDChan", ctypes.c_byte),
        ("byStartDTalkChan", ctypes.c_byte),
        ("byHighDChanNum", ctypes.c_byte),
        ("bySupport4", ctypes.c_byte),
        ("byLanguageType", ctypes.c_byte),
        ("byVoiceInChanNum", ctypes.c_byte),
        ("byStartVoiceInChanNo", ctypes.c_byte),
        ("byRes3", ctypes.c_byte * 2),
        ("byMirrorChanNum", ctypes.c_byte),
        ("wStartMirrorChanNo", ctypes.c_uint16),
        ("byRes2", ctypes.c_byte * 2)]


mutex = threading.Lock()


def rotate_by_step(id, dll, direction):
    mutex.acquire()
    if direction == 0:
        left_rotate_start(id, dll)
        time.sleep(0.25)
        left_rotate_stop(id, dll)
    else:
        right_rotate_start(id, dll)
        time.sleep(0.25)
        right_rotate_stop(id, dll)
    time.sleep(0.2)
    mutex.release()


def left_rotate(lUserID, dll, jug):
    act = dll.NET_DVR_PTZControl_Other(lUserID, 1, 23, jug)
    if act == 0:
        print(dll.NET_DVR_GetLastError())


def right_rotate(lUserID, dll, jug):
    act = dll.NET_DVR_PTZControl_Other(lUserID, 1, 24, jug)
    if act == 0:
        print(dll.NET_DVR_GetLastError())


def up_rotate(lUserID, dll, jug):
    act = dll.NET_DVR_PTZControl_Other(lUserID, 1, 21, jug)
    if act == 0:
        print(dll.NET_DVR_GetLastError())


def down_rotate(lUserID, dll, jug):
    act = dll.NET_DVR_PTZControl_Other(lUserID, 1, 22, jug)
    if act == 0:
        print(dll.NET_DVR_GetLastError())


def zoom_in(lUserID, dll, jug):
    act = dll.NET_DVR_PTZControl_Other(lUserID, 1, 11, jug)
    if act == 0:
        print(dll.NET_DVR_GetLastError())


def zoom_out(lUserID, dll, jug):
    act = dll.NET_DVR_PTZControl_Other(lUserID, 1, 12, jug)
    if act == 0:
        print(dll.NET_DVR_GetLastError())


def focus_near(lUserID, dll, jug):
    act = dll.NET_DVR_PTZControl_Other(lUserID, 1, 13, jug)
    if act == 0:
        print(dll.NET_DVR_GetLastError())


def focus_far(lUserID, dll, jug):
    act = dll.NET_DVR_PTZControl_Other(lUserID, 1, 14, jug)
    if act == 0:
        print(dll.NET_DVR_GetLastError())

def left_rotate_start(id, dll):
    left_rotate(id, dll, 0)


def left_rotate_stop(id, dll):
    left_rotate(id, dll, 1)


def right_rotate_start(id, dll):
    right_rotate(id, dll, 0)


def right_rotate_stop(id, dll):
    right_rotate(id, dll, 1)


def up_rotate_start(id, dll):
    up_rotate(id, dll, 0)


def up_rotate_stop(id, dll):
    up_rotate(id, dll, 1)


def down_rotate_start(id, dll):
    down_rotate(id, dll, 0)


def down_rotate_stop(id, dll):
    down_rotate(id, dll, 1)


def zoom_in_start(id, dll):
    zoom_in(id, dll, 0)


def zoom_in_stop(id, dll):
    zoom_in(id, dll, 1)


def zoom_out_start(id, dll):
    zoom_out(id, dll, 0)


def zoom_out_stop(id, dll):
    zoom_out(id, dll, 1)


def focus_near_start(id, dll):
    focus_near(id, dll, 0)


def focus_near_stop(id, dll):
    focus_near(id, dll, 1)


def focus_far_start(id, dll):
    focus_far(id, dll, 0)


def focus_far_stop(id, dll):
    focus_far(id, dll, 1)

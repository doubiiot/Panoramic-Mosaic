#-*- coding:utf-8 -*-
import ctypes
from PTZ_control import *
import os
#定义结构体

libpath = "./DLLS/"
dll_list = []

def add_dll(path,so_list):
    files = os.listdir(path)
    for file in files:
        if not os.path.isdir(path+file):
            if file.endswith(".dll"): so_list.append(path+file)
        else:
            add_dll(path+file+"/",so_list)

def callCpp(func_name, *args):
    for dll_lib in dll_list:
        try:
            lib = ctypes.cdll.LoadLibrary(dll_lib)
            try:
                value = eval("lib.%s" % func_name)(*args)
                print("调用：" + dll_lib)
                return value
            except:
                continue
        except:
            continue
    print("没有找到接口！")
    return False


#用户注册设备
def NET_DVR_Login_V30(sDVRIP = "192.168.134.122",wDVRPort = 8000,sUserName = "iot02",sPassword = "iot2015128"):
    init_res = callCpp("NET_DVR_Init")#SDK初始化
    if init_res:
        print("SDK初始化成功")
    else:
        error_info = callCpp("NET_DVR_GetLastError")
        print("SDK初始化错误：" + str(error_info))
        return False

    set_overtime = callCpp("NET_DVR_SetConnectTime",5000,4)#设置超时
    if set_overtime:
        print("设置超时时间成功")
    else:
        error_info = callCpp("NET_DVR_GetLastError")
        print("设置超时错误信息：" + str(error_info))
        return False

    #用户注册设备
    #c++传递进去的是byte型数据，需要转成byte型传进去，否则会乱码
    sDVRIP = bytes(sDVRIP,"ascii")
    sUserName = bytes(sUserName,"ascii")
    sPassword = bytes(sPassword,"ascii")
    DeviceInfo = LPNET_DVR_DEVICEINFO_V30()
    DeviceInfoRef = ctypes.byref(DeviceInfo)
    lUserID = callCpp("NET_DVR_Login_V30",sDVRIP,wDVRPort,sUserName,sPassword,DeviceInfoRef)
    print("登录结果："+str(lUserID))
    if lUserID == -1:
        error_info = callCpp("NET_DVR_GetLastError")
        print("登录错误信息：" + str(error_info))
        return error_info
    else:
        return lUserID
def init():
    add_dll(libpath, dll_list)
    for i in dll_list:
        print(i)
        dll = ctypes.CDLL(i)
    dll = ctypes.CDLL("./DLLS/HCNetSDK.dll")
    login_id = NET_DVR_Login_V30()
    print(login_id)
    return login_id, dll
#left(NET_DVR_Login_V30())



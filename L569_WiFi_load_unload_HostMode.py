#!/user/bin/python
# -*- coding: utf-8 -*-

import sys
import json
import time
import serial
import os
import re
import datetime
import win32api
import win32con
import filecmp


#*******************************************************************************
def GetNowTime():
    now = datetime.datetime.now()
    Time = now.strftime("%Y-%m-%d %H:%M:%S")
    return Time

#提示窗口
def ShowForm(str_detail="OK",str_title="Result"):
    win32api.MessageBox(0,
                        str(str_detail),
                        str(str_title)+" "+GetNowTime(),
                        win32con.MB_ICONINFORMATION)

def bWritePrint(WriteInfo="",FileName="Log.txt",WriteWay='a',IsPrint=True):
    try:
        with open(FileName,WriteWay) as fl:
            fl.write(WriteInfo.replace("\r",""))
        if IsPrint:
            print WriteInfo.strip()
        return True
    except:
        return False

def opencom( port, baud=115200, timeout=1.5 ):
    try:
        com_obj = serial.Serial(port,baud,timeout=float(timeout))
        return com_obj
    except:
        print "open_port_fail"

#串口写数据
def writedata( com_obj, strs ):
    com_obj.write(strs)
    return 

#串口读数据
def readdata( com_obj ):
    rsp = com_obj.readlines( )
    return rsp

#发送AT指令
def send_at_command( at_cmd ):
    
    writedata( com_obj, at_cmd )
    writedata( com_obj, '\r\n' )
    rsp = readdata( com_obj )
    time.sleep(1)
    return rsp

#串口关闭
def closecom( com_obj ):
    com_obj.close( )
    return 




def login():
    dail_phone = "root"
    dial_state = "oelinux123"
    loginword = "Password:"
    password = "root@mdm9607-perf:~#"
    print "login 测试开始"
    writedata( com_obj, '\n\r' )
    rsp = send_at_command( dail_phone ) #输入用户名 
    read= '\n'.join([item.rstrip('\n\r') for item in rsp])
    #print read
    flag=read.find(loginword)
    #print flag
    if flag != -1:
        #print flag
        print "login ok"
        rsp = send_at_command( dial_state )     #输入密码
        read= '\n'.join([item.rstrip('\n\r') for item in rsp])
        #print read
        flag=read.find(password)
        #print flag
        if flag != -1:
            print "password pass"
        else:
            print "password error"
    else:
        print"login error"


def Reboot():
    rebootcmd="reboot"
    writedata( com_obj, '\n\r' )
    rsp = send_at_command( rebootcmd )
    read= '\n'.join([item.rstrip('\n\r') for item in rsp])
    print "设备重启中"
    time.sleep(60)
    return rebootcmd

def ifcong():
    Wlanexit="ifconfig"
    Result = "wlan0"
    rsp = send_at_command( Wlanexit )
    read= '\n'.join([item.rstrip('\n\r') for item in rsp])
    #print read
    flag=read.find(Result)
    #print flag
    if flag!=-1:
        print "wlan0 ok"
        return True
    else:
        print "wlan0 fail"
        return False
    print "end"


#功能：在cmd使用adb shell来执行指令，获得返回值
#参数：指令
#返回值：指令执行后的反馈信息
def sendCmdCommand(Command):
    adbShellCommmad='adb shell '+Command
    info=os.popen(adbShellCommmad).read()
    return info

#功能：装载加载WiFi
#参数：无
#返回值：
def CheckWifi():
    Wlanup = "ifconfig wlan0 up"
    Wlandown="ifconfig wlan0 down"
    Reboot()
    login()
    rsp = send_at_command( Wlandown )
    read= '\n'.join([item.rstrip('\n\r') for item in rsp]) #rstrip()去除字符串右边的换行和回车符。以换行符作为分隔符，把rsp的所有元素连接成一个新的字符串
    #print read
    if ifcong() == False:
        print "WIFI卸载成功"
        rsp = send_at_command( Wlanup )
        read= '\n'.join([item.rstrip('\n\r') for item in rsp])
        #print read
        if ifcong() == True:
            print "WIFI加载成功"
            return True
        else:
            
            count(1) #计算加载WiFi失败次数
            bWritePrint("********WIFI加载失败********"+'\n')
            #ShowForm("WIFI加载失败")
    else:
        count(0) #计算卸载WiFi失败次数
        bWritePrint("********WIFI卸载失败********"+'\n')
        #ShowForm("WIFI卸载失败")
        
        
#测试次数               
def Loop(nTimes = 1):
    for i in range(nTimes):
        bWritePrint(("No."+str(i+1)+" "+GetNowTime()+"**********\n"))
        CheckWifi()
    a=float(LOADFAILCOUNT)
    b=float(UNLOADFAILCOUNT)
    c=float(nTimes)
    bWritePrint('压力测试次数为： '+str(nTimes)+'  ')
    bWritePrint('WiFi加载失败率为： '+"%.2f%%"%(a/c*100)+'  ')  #计算WiFi加载失败率
    bWritePrint('WiFi卸载失败率为： '+"%.2f%%"%(b/c*100)+'  ')  #计算WiFi卸载失败率

#计算失败次数
def count(failStr):
    global LOADFAILCOUNT
    global UNLOADFAILCOUNT
    if failStr==1:   #计算加载WiFi失败次数
        LOADFAILCOUNT+=1
    else:            #计算卸载WiFi失败次数
        UNLOADFAILCOUNT+=1
    

#主函数
def main():
    Loop(1000)  #测试次数
    
#全局变量
LOADFAILCOUNT=0   #加载WiFi失败次数
UNLOADFAILCOUNT=0 #卸载WiFi失败次数
#变量
comport = "com35"
comport_timeout = 5.0
baud = 115200	
if __name__ == "__main__":
    #打开modem端口
    com_obj = opencom( comport, baud, comport_timeout )
    main()
    closecom( com_obj )


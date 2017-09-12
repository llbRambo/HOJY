#!/usr/bin/python
# -*- coding: utf-8 -*-

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

#功能：创建此脚本运行的log文件，并在脚本运行时打印信息
#参数：writeInfo：要写进log文件以及要打印的信息；logName：log文件名；writeWay：信息的写入方式；
#      printFlag：打印标志（True为要打印，False为不打印）
#返回值：函数执行成功返回True，执行异常返回False
def WriteLogPrint(writeInfo="",logName="Log.txt",writeWay='a',printFlag=True):
    try:
        with open(logName,writeWay) as fl:
            fl.write(writeInfo.replace("\r",""))
        if printFlag:
            print writeInfo.strip()
        return True
    except:
        return False

#功能：打开串口
#参数：port:端口号；baud：比特率；timeout：
def OpenCom( port, baud=115200, timeout=1.5 ):
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
    password = "root@mdm9607:~#"
    print "login 测试开始"
    writedata( com_obj, '\n\r' )
    rsp = send_at_command( dail_phone )    
    read= '\n'.join([item.rstrip('\n\r') for item in rsp])
    print read
    flag=read.find(loginword)
    print flag
    if flag != -1:
        print flag
        print "login ok"
        rsp = send_at_command( dial_state )
        read= '\n'.join([item.rstrip('\n\r') for item in rsp])
        print read
        flag=read.find(password)
        print flag
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
    print "设备重启成功"
    return rebootcmd


def adbReboot():
    os.popen('adb reboot')
    while 1==1:
        info=strSendCMD( "adb get-state " )
        flag = info.find("device") #检查设备是否开启
        if flag !=-1 :  #设备开启则停止检查，跳出循环
            break
    print 'adb state '+info
    time.sleep(30)

    
def strSendCMD(strConnect=''):
    feedbackInfo=os.popen(strConnect).read()
    return feedbackInfo

def bCheckWiFi(): #检查WiFi连接过程中是否会断开
    info=strSendCMD('netsh wlan show interface')
    print '接口状态 ',info
    flag=info.find('已连接')
    if flag!=-1:
        return True
    else:
        return False
    
    

#自动连接指定用户名的wifi并判断连接性
def bAutoConnect(strSSID="ZSYL"):
    strConnect = "netsh wlan connect " + strSSID
    strDisconnect = "netsh wlan disconnect 无线网络连接"
    for i in range(60):
        strFlag1 = strSendCMD(strConnect)
        print '连接信息：　',strFlag1
        intFlag = strFlag1.find("已成功")
        if intFlag != -1:
            WriteLogPrint("Connected.\n")
            break
        else:
            if i == 59:
                WriteLogPrint("No."+str(i+1)+" Finally Connect Failed!\n")
                return False
            else:
                WriteLogPrint("No."+str(i+1)+" Connect Failed,Try Again...\n")
                time.sleep(1)
                continue
    time.sleep(20)  
    if bCheckWiFi() == True:
        for i in range(60):
            strFlag2 = strSendCMD(strDisconnect)
            print '断开连接信息：　',strFlag2
            intFlag = strFlag2.find("已成功")   
            if intFlag != -1 or bCheckWiFi() == False:   #用命令成功断开连接或者中途WiFi自动断开
                WriteLogPrint("Disconnected succeed.\n")
                return True
            else:
                if i == 59:
                    WriteLogPrint("Disconnected Failed!\n")
                    return False
                else:
                    WriteLogPrint("Disconnected Failed,Try Again...\n")
                    time.sleep(5)
                    continue

def PingNetWork():
    Dns = "ping www.baidu.com -c 3"
    Result = "0% packet loss"
    #check_csfb_to_4g = "adb -s 861d3b58 shell at_cmd at+ctec?"
    #check_csfb_to_4g = "adb -s 34c5a747 shell at_cmd at+ctec?"
    print "PingNetWork测试开始"
    rsp = send_at_command( Dns )    
    read= '\n'.join([item.rstrip('\n\r') for item in rsp])
    print read
    flag=read.find(Result)
    print flag
    if flag!=-1:
        print "PingNetWork test ok"
        
    else:
        print"PingNetWork ERROR"
        ShowForm("Ping网路不同,请将差Wifi是否连接")
    print "end"
                    
def Loop(nTimes = 1):
    for i in range(nTimes):
        WriteLogPrint(("No."+str(i+1)+" "+GetNowTime()+"\n"))
        #Reboot()
        #login()
        adbReboot()
        bAutoConnect()
        
def main():
    Loop(10)


comport = "com11"
comport_timeout = 5.0
baud = 115200
	
if __name__ == "__main__":
    #打开modem端口
    #com_obj = opencom( comport, baud, comport_timeout )
    main()
    #closecom( com_obj )


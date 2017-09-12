#!/user/bin/python
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
    rsp = com_obj.readlines()
    #rsp = com_obj.read(1000)
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
    #print read
    
    flag=read.find(loginword)
    #print flag
    if flag != -1:
        #print flag
        print "login ok"
        rsp = send_at_command( dial_state )
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
    #read= '\n'.join([item.rstrip('\n\r') for item in rsp])
    print "设备重启中"
    time.sleep(60)
    return rebootcmd

#功能：通过cmd使用adb shell让设备重启
#参数：无
#返回值：
def adbReboot():
    SendCmdCommand('adb reboot')
    print 'adb rebooting...'
    while 1==1:
        info=SendCmdCommand( "adb get-state " )
        flag = info.find("device") #检查设备是否开启
        if flag !=-1 :  #设备开启则停止检查，跳出循环
            break
    print 'adb state '+info


#功能：获取WiFi状态
#参数：无
#返回值：WiFi状态为可用则返回1，不可用则返回0
def GetWiFiStatus():
    getWifiStatus="adb shell wifi_test get_status"      #获取WiFi状态命令行
    contrastResult = "wifi status is enable." #执行命令成功后的对比结果
    wifiStatus = SendCmdCommand( getWifiStatus ) #获取WiFi状态
    #print read
    flag=wifiStatus.find(contrastResult)  #判断WiFi是否可用
    
    if flag!=-1:   #可用返回1
        #print "wifi is enable"
        return 1
    else:          #不可用返回0
        #print"wifi is disable"
        return 0
    

#功能：在cmd使用adb shell执行命令，并获得反馈信息
#参数：指令
#返回值：命令执行后的反馈信息
def SendCmdCommand(command):
    info=os.popen(command).read()
    return info
    
    

#功能：加载卸载WiFi
#参数：无
#返回值：成功返回1，失败返回0
def LoadUnloadWifi():
    wifiUp = "adb shell wifi_test enable_ap"  #加载WiFi命令行
    wifiDown="adb shell wifi_test disable_ap" #卸载WiFi命令行
    contrastResult=' ap ok.'        #执行命令成功后的对比结果
    
    unloadFeedback=SendCmdCommand(wifiDown)   #执行卸载WiFi命令并获得反馈值
    while 1==1:                #检查命令是否执行成功
        print unloadFeedback
        flag1=unloadFeedback.find(contrastResult)
        if flag1!=-1:     #返回‘ ap ok.’，命令执行成功，停止检查，跳出循环
            break  
    
    if GetWiFiStatus() == 0:    #检测WiFi状态，如果已卸载则执行以下语句
        loadFeedback=SendCmdCommand(wifiUp)        #执行装载WiFi命令并获得反馈值
        while 1==1:           #检测命令是否执行成功
            print loadFeedback
            flag2=loadFeedback.find(contrastResult)
            if flag2!=-1:     #返回‘ ap ok.’，命令执行成功，停止检查，跳出循环
                break
        
        if GetWiFiStatus() == 1:   #WiFi装载检测，装载成功执行以下命令
            print "WIFI卸载成功  and  WIFI加载成功"
            return 1
        else:                  #装载失败执行以下命令
            print "WIFI卸载成功  but  WIFI加载失败"
            ShowForm("WIFI卸载成功  but  WIFI加载失败")
    else:
        print "WIFI卸载失败"
        ShowForm("WIFI卸载失败")
        
        
            
                    
def Loop(nTimes = 1):
    for i in range(nTimes):
        bWritePrint(("No."+str(i+1)+" "+GetNowTime()+"\n"))
        adbReboot()
        LoadUnloadWifi()
def main():
    Loop(10)


comport = "com6"
comport_timeout = 5.0
baud = 115200
	
if __name__ == "__main__":
    #打开modem端口
    #com_obj = opencom( comport, baud, comport_timeout )
    main()
    #closecom( com_obj )


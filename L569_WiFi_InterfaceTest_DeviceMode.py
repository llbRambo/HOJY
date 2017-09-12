#!/user/bin/python
# -*- coding: cp936 -*-

import sys
import json
import time
import serial
import os
import re
import string
import datetime
import win32api
import win32con
import filecmp

#*******************************************************************************

def GetNowTime():
    now = datetime.datetime.now()
    Time = now.strftime("%Y-%m-%d %H:%M:%S")
    return Time

def WriteLogPrint(WriteInfo="",FileName="InterfaceLog.txt",WriteWay='a',IsPrint=True):
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

#提示窗口
def ShowForm(str_detail="OK",str_title="Result"):
    win32api.MessageBox(0,
                        str(str_detail),
                        str(str_title)+" "+GetNowTime(),
                        win32con.MB_ICONINFORMATION)

#串口写数据
def writedata( com_obj, strs ):
    com_obj.write(strs)
    com_obj.write('\r\n')
    return 

#串口读数据
def readdata( com_obj ):
    rsp = com_obj.readlines( )
    return rsp

#发送AT指令
def send_at_command( at_cmd ):
    writedata( com_obj, '\r\n' )
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

def Ifconfig():
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

def SendCmdWaitResponse(setStr='',getStr='',response=''):    
    try:
        setSucceed=' ok.'
        print setStr
        #rsp = send_at_command( setStr ) #执行set类型接口
        rsp=os.popen(setStr)
        read=rsp.read()
        setFlag=read.find(setSucceed)  
        if setFlag!=-1:  #set类型接口生效
            
            rsp = os.popen( getStr ) #执行get类型命令
            read=rsp.read()
            getFlag=read.find(response)   #get上面set的值
            if getFlag!=-1:   #get到值，说明set指令生效，get指令生效
                print getStr+'\n'+response+'\n'
                #bWritePrint('This is valid for instructions')
                return 1      #返回1，表示这对指令有效
            else:
                WriteLogPrint(setStr+'  is ok,but get different value'+'\n')  #打印错误信息
                return 0      #set成功，却get不到set的值，表示set接口有问题
        else:            #set类型接口不生效
            WriteLogPrint('\n'+setStr+'  error\n')   #打应错误信息
            ShowForm('SendCmdWaitResponse：\n'+setStr+'  error\n')
            return 0     #返回0
    except:
        WriteLogPrint ('sendPortError',ifPrint=0)
        return 'sendPortError' 



#接口测试
def CheckInterface():
    #,'set_ht_cap'      ,'get_ht_cap'  ,'set_auth_algs'   ,'get_auth_algs'   
    set_InterList=['set_ssid','enable_hide_ssid','set_encrypt_mode','set_key_mgmt','set_password','set_country','set_hw_mode','set_sta_capacity']
    get_InterList=['get_ssid','get_hide_ssid','get_encrypt_mode','get_key_mgmt','get_password','get_country','get_hw_mode','get_sta_capacity']
    values=['liulb','1','WPA2','WPA-PSK CCMP','12312312','CN','g/n','10']
    
    for i in range(8):
        setInterStr='adb shell wifi_test '+set_InterList[i]+' '+values[i]
        getInterStr='adb shell wifi_test '+get_InterList[i]
        flag=SendCmdWaitResponse(setInterStr,getInterStr,values[i])
        if flag==1:
            continue
        else:
            ShowForm('CheckInterface:\n'+setInterStr)
    
    #重新加载配置文件
    while 1==1:
        flag=ReloadConfig()
        if flag==1:
            break
'''
#功能：检查hw_mode接口
#参数：模式b/g/n，g/n，b/n
#返回值：成功返回1，失败返回0
def CheckHwMode(hwMode=''):
    adbShell='adb shell wifi_test '
    setHwModeStr=adbShell+'set_hw_mode '+hwMode
    getHwModeStr=adbShell+'get_hw_mode '
    flag=SendCmdWaitResponse(setHwModeStr,getHwModeStr,hwMode)
    if flag==1:
        flagReload=ReloadConfig()
        if flagReload==1:
            flagHostapd=CheckHostapd()
            if flagHostapd==1:
                print 'the interface hw_mode is ok!'
            else:
                print 'the interface hw_mode is failed!'
        else:
            
        

'''

#功能：检测hostapd进程是否存在
#参数：无
#返回值：存在则返回1，不存在则返回0
def CheckHostapd():
    checkHostapd=os.popen('adb shell ps')  #打印进程
    checkHostapdInfo= checkHostapd.read()
    #print checkHostapdInfo
    checkHostapdFlag=checkHostapdInfo.count('hostapd') #计算hostapd字符串的个数
    #print 'hostapd '+str(checkHostapdFlag)+' 个'
    if checkHostapdFlag == 5:  #有5个表示hostapd进程存在
        return 1
    else:
        print 'The process hostapd is not exist!'
        return 0


#功能：加载配置文件
#参数：无
#返回值：加载成功则返回1，失败则返回0
def ReloadConfig():
    reloadConfig=os.popen('adb shell wifi_test reload_config')
    time.sleep(15)
    #检测配置文件是否加载成功
    reloadConfigInfo= reloadConfig.read()
    #print read
    reloadConfigFlag=reloadConfigInfo.find('wifi reload config ok.')
    if reloadConfigFlag!=-1:
        return 1 #配置文件加载成功
    else:
        print 'the interface reload_config is failed!'
        return 0
                    
#功能：检测mib_all文件指定字段的值是否改变
#参数：字段名，值
#返回值：改变成功则返回1，失败则返回0
def CheckMib_all(fieldName='',fieldValue=''):
    checkMiball=os.popen('adb shell cat /proc/wlan0/mib_all')
    feedBackInfo=checkMiball.read()
    
    #print 'feedBackInfo: ',feedBackInfo
    
    getValue=fieldName+':'+' (\d+)'
    number=re.findall(getValue,feedBackInfo)
    
    print 'number: ',number[0]
    
    if int(number[0])==int(fieldValue):
        return 1
    else:
        print 'mib_all file change failed'
        return 0


                
#功能：查看信道，检测信道是否修改成功
#参数：无
#返回值：无
def CheckChannel():
    
    channelNumber=['1','2','3','4','5','6','7','8','9','10','11','12','13']
    for i in range(13):
        setChannel='adb shell wifi_test set_channel '+channelNumber[i]
        getChannel='adb shell wifi_test get_channel '
        checkFlag=SendCmdWaitResponse(setChannel,getChannel,channelNumber[i])
        if checkFlag==1:   #set和get指令能够执行成功，则重新加载配置文件
            flag1=ReloadConfig()
            if flag1==1:   #加载配置文件成功，则检查hostapd进程
                flag2=CheckHostapd()
                if flag2==1: #hostapd进程没问题则检查字段
                    time.sleep(20)   #检测mib_all文件dot11channel字段是否被修改成功
                    checkMiballFlag=CheckMib_all('dot11channel',channelNumber[i])
                    if checkMiballFlag==1:
                        print 'channel change succeed!'
        else:
            WriteLogPrint('set channel failed ！')
            
        
      
            
    


#测试次数               
def Loop(nTimes = 1):
    for i in range(nTimes):
        WriteLogPrint(("**********No."+str(i+1)+" "+GetNowTime()+"**********\n"))
        #CheckChannel()
        #CheckInterface()
        reflag=ReloadConfig()
        
        if reflag==1:
            hostFlag=CheckHostapd()
            if hostFlag==1:
                print 'reload_config ok'
            else:
                ShowForm('reload_config lead to hostapd not exist')
        else:
            ShowForm('reload_config is not ok')

#主函数
def main():
    Loop(1000)  #测试次数
    '''
    a=CheckMib_all('dot11channel','13')
    if a==1:
        print 'change succeed!'
    else:
        print 'change failed!'
        '''
    
#全局变量
LOADFAILCOUNT=0   #加载WiFi失败次数
UNLOADFAILCOUNT=0 #卸载WiFi失败次数


#*******************************************************************************
#变量
comport = "com19"
comport_timeout = 5.0
baud = 115200


if __name__ == "__main__":
    #打开modem端口
    #com_obj = opencom( comport, baud, comport_timeout )
    main()
    #closecom( com_obj )
 

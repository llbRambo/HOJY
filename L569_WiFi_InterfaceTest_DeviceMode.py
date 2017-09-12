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

#��ʾ����
def ShowForm(str_detail="OK",str_title="Result"):
    win32api.MessageBox(0,
                        str(str_detail),
                        str(str_title)+" "+GetNowTime(),
                        win32con.MB_ICONINFORMATION)

#����д����
def writedata( com_obj, strs ):
    com_obj.write(strs)
    com_obj.write('\r\n')
    return 

#���ڶ�����
def readdata( com_obj ):
    rsp = com_obj.readlines( )
    return rsp

#����ATָ��
def send_at_command( at_cmd ):
    writedata( com_obj, '\r\n' )
    writedata( com_obj, at_cmd )
    writedata( com_obj, '\r\n' )
    rsp = readdata( com_obj )
    time.sleep(1)
    return rsp

#���ڹر�
def closecom( com_obj ):
    com_obj.close( )
    return 


def login():
    dail_phone = "root"
    dial_state = "oelinux123"
    loginword = "Password:"
    password = "root@mdm9607:~#"
    print "login ���Կ�ʼ"
    writedata( com_obj, '\n\r' )
    rsp = send_at_command( dail_phone ) #�����û��� 
    read= '\n'.join([item.rstrip('\n\r') for item in rsp])
    #print read
    flag=read.find(loginword)
    #print flag
    if flag != -1:
        #print flag
        print "login ok"
        rsp = send_at_command( dial_state )     #��������
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
    print "�豸������"
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
        #rsp = send_at_command( setStr ) #ִ��set���ͽӿ�
        rsp=os.popen(setStr)
        read=rsp.read()
        setFlag=read.find(setSucceed)  
        if setFlag!=-1:  #set���ͽӿ���Ч
            
            rsp = os.popen( getStr ) #ִ��get��������
            read=rsp.read()
            getFlag=read.find(response)   #get����set��ֵ
            if getFlag!=-1:   #get��ֵ��˵��setָ����Ч��getָ����Ч
                print getStr+'\n'+response+'\n'
                #bWritePrint('This is valid for instructions')
                return 1      #����1����ʾ���ָ����Ч
            else:
                WriteLogPrint(setStr+'  is ok,but get different value'+'\n')  #��ӡ������Ϣ
                return 0      #set�ɹ���ȴget����set��ֵ����ʾset�ӿ�������
        else:            #set���ͽӿڲ���Ч
            WriteLogPrint('\n'+setStr+'  error\n')   #��Ӧ������Ϣ
            ShowForm('SendCmdWaitResponse��\n'+setStr+'  error\n')
            return 0     #����0
    except:
        WriteLogPrint ('sendPortError',ifPrint=0)
        return 'sendPortError' 



#�ӿڲ���
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
    
    #���¼��������ļ�
    while 1==1:
        flag=ReloadConfig()
        if flag==1:
            break
'''
#���ܣ����hw_mode�ӿ�
#������ģʽb/g/n��g/n��b/n
#����ֵ���ɹ�����1��ʧ�ܷ���0
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

#���ܣ����hostapd�����Ƿ����
#��������
#����ֵ�������򷵻�1���������򷵻�0
def CheckHostapd():
    checkHostapd=os.popen('adb shell ps')  #��ӡ����
    checkHostapdInfo= checkHostapd.read()
    #print checkHostapdInfo
    checkHostapdFlag=checkHostapdInfo.count('hostapd') #����hostapd�ַ����ĸ���
    #print 'hostapd '+str(checkHostapdFlag)+' ��'
    if checkHostapdFlag == 5:  #��5����ʾhostapd���̴���
        return 1
    else:
        print 'The process hostapd is not exist!'
        return 0


#���ܣ����������ļ�
#��������
#����ֵ�����سɹ��򷵻�1��ʧ���򷵻�0
def ReloadConfig():
    reloadConfig=os.popen('adb shell wifi_test reload_config')
    time.sleep(15)
    #��������ļ��Ƿ���سɹ�
    reloadConfigInfo= reloadConfig.read()
    #print read
    reloadConfigFlag=reloadConfigInfo.find('wifi reload config ok.')
    if reloadConfigFlag!=-1:
        return 1 #�����ļ����سɹ�
    else:
        print 'the interface reload_config is failed!'
        return 0
                    
#���ܣ����mib_all�ļ�ָ���ֶε�ֵ�Ƿ�ı�
#�������ֶ�����ֵ
#����ֵ���ı�ɹ��򷵻�1��ʧ���򷵻�0
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


                
#���ܣ��鿴�ŵ�������ŵ��Ƿ��޸ĳɹ�
#��������
#����ֵ����
def CheckChannel():
    
    channelNumber=['1','2','3','4','5','6','7','8','9','10','11','12','13']
    for i in range(13):
        setChannel='adb shell wifi_test set_channel '+channelNumber[i]
        getChannel='adb shell wifi_test get_channel '
        checkFlag=SendCmdWaitResponse(setChannel,getChannel,channelNumber[i])
        if checkFlag==1:   #set��getָ���ܹ�ִ�гɹ��������¼��������ļ�
            flag1=ReloadConfig()
            if flag1==1:   #���������ļ��ɹ�������hostapd����
                flag2=CheckHostapd()
                if flag2==1: #hostapd����û���������ֶ�
                    time.sleep(20)   #���mib_all�ļ�dot11channel�ֶ��Ƿ��޸ĳɹ�
                    checkMiballFlag=CheckMib_all('dot11channel',channelNumber[i])
                    if checkMiballFlag==1:
                        print 'channel change succeed!'
        else:
            WriteLogPrint('set channel failed ��')
            
        
      
            
    


#���Դ���               
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

#������
def main():
    Loop(1000)  #���Դ���
    '''
    a=CheckMib_all('dot11channel','13')
    if a==1:
        print 'change succeed!'
    else:
        print 'change failed!'
        '''
    
#ȫ�ֱ���
LOADFAILCOUNT=0   #����WiFiʧ�ܴ���
UNLOADFAILCOUNT=0 #ж��WiFiʧ�ܴ���


#*******************************************************************************
#����
comport = "com19"
comport_timeout = 5.0
baud = 115200


if __name__ == "__main__":
    #��modem�˿�
    #com_obj = opencom( comport, baud, comport_timeout )
    main()
    #closecom( com_obj )
 

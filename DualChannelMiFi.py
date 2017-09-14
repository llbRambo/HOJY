#/usr/bin/python
#-*- coding:utf-8 -*-
import os
import re
import win32api
import win32con
import time
import datetime

#9x07模块类
class Module(object):
    #功能：实例化模块
    #参数：模块名，网络制式
    #返回值：无
    def __init__(self,moduleName,netType):
        self.__moduleName=moduleName  #__moduleName为私有属性
        self.__netType=netType      #__netType为私有属性
        
    #功能：给外部访问提供的方法
    #参数：self
    #返回值：模块名
    def GetName(self):
        return self.__moduleName

    #功能：给外部访问提供的方法
    #参数：self
    #返回值：网络制式
    def GetType(self):
        return self.__netType

    #功能：给外部设置提供的方法
    #参数：self
    #返回值：无
    def SetName(self,moduleName,netType):
        self.__moduleName=moduleName
        self.__netType=netType

    #功能：在cmd中执行adb shell命令，并获取反馈信息
    #参数：adb 命令
    #返回值：命令执行后的反馈信息
    def ExecuteAdbCommand(adbCommand):
        feedbackInfo=os.popen (adbCommand).read()
        return feedbackInfo
    
    #功能：重启模块并且检测设备是否开启
    #参数：无
    #返回值：已开启返回1，反之则返回0
    def RebootAndCheckAdb():
        ExecuteAdbCommand('adb reboot')
        print 'adb rebooting...'
        while 1==1:
            info=ExecuteAdbCommand('adb get-state')
            flag=info.find('device')
            if flag!=-1:
                break
        print 'adb is ready'
            
    #功能：直接ping网或者间断时间ping网
    #参数：间隔时间
    #返回值：ping网成功返回1，反之则返回0
    def PingNetwork(intervalTime=0):
        time.sleep(intervalTime)
        infoPing=ExecuteAdbCommand('adb shell ping www.qq.com -c 10')
        #利用正则表达式获取丢包率
        Regex=re.complie(r'received,(.*)%')
        mo=Regex.search(infoPing)
        lostPackage=mo.group(0)
        if lostPackage<'100':
            return 1
        else:
            return 0



#双通道MiFi类
class DualChannelMiFi(Module):
    #功能：
    #参数：
    #返回值：
    def __init__(self,projectName):
        self.projectName=projectName


    #
    def rebootDevices():
        os.popen('adb reboot')

        



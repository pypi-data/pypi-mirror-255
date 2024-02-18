"""
author: wang ying
created time: 
intro:
file:
"""
import ctypes
import datetime
import threading

from dateutil import tz
import pytz
import socket
import uuid
import random
import os
random.seed(datetime.datetime.now().timestamp())

nextSequence = 0
lastTimeFlag = 0
maxSeq = 127
MILLIS = 8*3600*1000
TICKS_AT_EPOCH = 621355968000000000
TICKS_PER_MILLISECOND = 10000
startTicks = 0
endBytes = ctypes.create_string_buffer(7)

lock = threading.Lock()

def initStartTicks():
    '''
    utc时区下， 2000, 1, 1,0,0,0的毫秒数
    Returns:
    '''
    tzinfo =tz.gettz('UTC')
    oo = datetime.datetime(2000, 1, 1,0,0,0, tzinfo=tzinfo)  #timestamp存储的时间与时区有关，变换时区数据会受影响；datetime与时间无关；

    return int(oo.timestamp()*1000)

def initData():

    serverBytes = getServerBytes()
    processId = getProcessID()
    global endBytes
    for i in range(4):
        endBytes[i] = serverBytes[i]

    # print(type(endBytes), type(endBytes[0]))
    endBytes[6] = processId & 0xff
    endBytes[5] = (processId >> 8) & 0xff
    endBytes[4] = (processId >> 16) & 0xff


def getServerBytes():
    '''
    获取ip的地址,转为bytes类型 32 bit
    Returns:
    '''

    res = socket.gethostbyname(socket.gethostname())
    ipaddress = socket.inet_aton(res)
    return ipaddress

def getProcessID():
   #当前的线程
    return os.getpid()




def createSequentialUuidBytes():
    systemtime = datetime.datetime.now().microsecond
    startTicks = initStartTicks()
    nowTimeFlag = ((systemtime + MILLIS) * TICKS_PER_MILLISECOND) + TICKS_AT_EPOCH - startTicks

    nowTimeFlag >>= 10
    nowSeq, currRandom = 0, 0
    global lastTimeFlag,nextSequence
    lock.acquire()

    if nowTimeFlag > lastTimeFlag:
        lastTimeFlag = nowTimeFlag
        nowSeq = 0
        nextSequence = 1
    elif nowTimeFlag == lastTimeFlag :
        nowSeq = nextSequence
        nextSequence += 1
        if nowSeq >= maxSeq:
            nowTimeFlag += 1
            lastTimeFlag = nowTimeFlag
            nowSeq = 0
            nextSequence = 1
    else:
        nowTimeFlag = lastTimeFlag
        nowSeq = nextSequence
        nextSequence += 1
        if nowSeq >= maxSeq:
            nowTimeFlag += 1
            lastTimeFlag = nowTimeFlag
            nowSeq = 0
            nextSequence = 1

    currRandom = random.randint(1,65535)

    lock.release()

    return buildUuidBytes(nowTimeFlag, nowSeq, currRandom)

def buildUuidBytes(nowTimeFlag, nowSeq, currRandom):

    currRandom &= 0xFF
    tmpbytes = ctypes.create_string_buffer(16)  #ctypes.c_char_Array_16

    tmpbytes[5]= nowTimeFlag & 0xFF
    # print('sss',nowTimeFlag & 0xFF)
    nowTimeFlag >>= 8
    tmpbytes[4] = nowTimeFlag & 0xFF
    nowTimeFlag >>= 8
    tmpbytes[3] = nowTimeFlag & 0xFF
    nowTimeFlag >>= 8
    tmpbytes[2] = nowTimeFlag & 0xFF
    nowTimeFlag >>= 8
    tmpbytes[1] = nowTimeFlag & 0xFF
    nowTimeFlag >>= 8
    tmpbytes[0] = nowTimeFlag & 0xFF
    tmpbytes[6] = nowSeq
    tmpbytes[7] = (currRandom >> 8) & 0xff
    tmpbytes[8] = currRandom & 0xff
    global endBytes
    tmpbytes[9:9+6] = endBytes[0:6]

    return tmpbytes


def getGuidFromByteArray(xbytes):  #{48b: time} {8b: seq} {16b: rand} {32b: serverFlag/IP}, {24b: processId}
    uuidd = uuid.UUID(bytes=bytes(xbytes))
    return uuidd

def generate():
    initData()
    uuidBytes = createSequentialUuidBytes()

    return getGuidFromByteArray(uuidBytes)

if __name__=='__main__':


    print(generate()) #a83d6602fe00

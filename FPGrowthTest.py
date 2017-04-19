# /usr/bin/env python
# -*- coding: utf-8 -*-

import FPGrowth
import generateTransDB
import os
import datetime
import Constant
import time
testPath = '50465d5aa129/2016-04-16.txt'


def  readFromFile(path=testPath):
    simpleData=[]
    with open(path) as fo:
        for line in fo:
            arr = line.strip().split(" ")
            simpleData.append(arr)
    return simpleData
    
def initSimpleData(simpleData):
    retDic = {}
    for trans in simpleData:
        retDic[frozenset(trans)] = retDic.get(frozenset(trans),0)+1
    return retDic


def minePatterns(user):
    dayFiles = [someFile for someFile in os.listdir(user) if someFile.startswith('2016') ] #and os.path.getsize(user+'/'+someFile) >0
    weekData = []
    simpleData = []
    for dayFile in sorted(dayFiles):
        simpleData = readFromFile(user+'/'+dayFile)
        weekData = weekData + simpleData
        # calculate a week patterns on every Saturday
        if weekData and datetime.datetime.strptime(dayFile.rstrip('.txt'),'%Y-%m-%d').weekday() == 5: 
            mineAndSavePatterns(user,'week-'+dayFile,weekData,7)
            weekData = []

        if not simpleData :
            continue

        dynamicSupport = Constant.dayMinSupport
        # if len(simpleData)/2 > dynamicSupport:
        #     dynamicSupport = len(simpleData)/2

        # if os.path.getsize(user+'/'+dayFile) >10000 : # greater than 1kb
        #     dynamicSupport = len(simpleData)/2 + 1
        # print dynamicSupport,len(simpleData)
        mineAndSavePatterns(user,dayFile,simpleData,dynamicSupport)


def mineAndSavePatterns(user,dayFile,simpleData,minSup):
    freqItems = []
    myFPtree, myHeaderTab = FPGrowth.createTree( initSimpleData(simpleData),minSup)
    FPGrowth.mineTree( myFPtree, myHeaderTab, minSup, set([]), freqItems)   
    savePattern(user+'/'+'pattern-'+dayFile,freqItems)


def savePattern(savePath,freqItems):
    # print savePath, len(freqItems)
    buff = ''
    for item in freqItems:
        buff = buff + str(list(item)) +'\n'
    # for item in sorted(patterns,key=lambda p: len(p)): # sorted will take a lot of time ! so give it away! remember that!
    #     buff = buff + str(item) +'\n'
    if buff:
        with open(savePath,'w') as fo:
            fo.write(buff)
    

if __name__ == '__main__':
    t1 = time.time()
    try:
        for user in Constant.users:
            minePatterns(user)
    except Exception, e:
        print e
    t2 = time.time()
    print "total time on finding every user's habibs",t2-t1
    
    
        

    
    

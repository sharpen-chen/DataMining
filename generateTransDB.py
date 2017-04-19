# usr/bin/env python
# -*- coding: utf-8 -*-
# extract 4 devices below and save into mongodb

import datetime
import os
import Constant
#users: most frequent f8db88fe5e47 100
# 00306791d6a7 100
# 18037385f9fc 119
# bc5ff43ad110 135
# f8db88fe68b1 170
# 00269ebc2fc7 238
# 50465d5aa114 240
# 50465d5aa129 244
# 50465d5aa117 291
# b8975a5dbfdf 472

mapFile = 'HostMapped.txt'
dirPath ='./MultiProcessPro0605'
upperRange = datetime.datetime.strptime('2016-05-01','%Y-%m-%d') 
lowerRange = datetime.datetime.strptime('2016-04-11','%Y-%m-%d')



# return everyday's directory, the return dirs will be used to the muliprocess args
def searchDaysDir(path=dirPath):
    rs = []
    files = os.listdir(path)
    for onefile in files:
        if str(onefile).startswith('2016'):
            dt = datetime.datetime.strptime(str(onefile).strip('.txt'),'%Y-%m-%d')
            if dt >= lowerRange and dt < upperRange:
                rs.append(onefile)
    return rs

def readSomeday(user,dayFile):
    macdic = {}
    rs = []
    with open(dirPath+'/'+dayFile) as fo:
        for line in fo:
            line = line.strip()
            dic = line.split("):")[0]
            times = line.split("):")[1]
            keylst =  dic.split(",")
            keylst = [keylst[0][1:].strip('\''),keylst[1].strip(' \''),keylst[2].strip(' \''),keylst[3].lstrip(' u').strip(' \'')]
            macdic[keylst[0]] =macdic.get(keylst[0],0)+1

            if  user in keylst[0] : 
                rs = rs + [keylst + [times]] # calculate sb's data into good format
    resultLst = {}
    hosts = []
    for item in rs:
        resultLst[item[2]] = resultLst.get(item[2],[])+[item[3]]

    for i,v in sorted(resultLst.iteritems()):
        # print i,set(v)
        hosts.append(set(v))
    return hosts

# scan every item in evert line,and encode
def generateTDB(rs,user,dayFile):
    amap = readMapFileFromDB()
    content = ''
    for items in rs:
        for item in items:
            if item not in amap:
                amap[item] = len(amap)
            content = content + str(amap[item])+ ' '
        content+= '\n'
    
    if not os.path.exists(user):
        os.mkdir(user)
    with open(user+'/'+dayFile,'w') as fo:
        fo.write(content)
    updateMapFile(amap)

def readMapFileFromDB():
    if not os.path.exists(mapFile):
        return {}
    amap = {}
    content = ''
    with open(mapFile) as fo:
        content = fo.read()

    if content is not None and len(content) > 0:
        amap = eval(content)
    return amap

def updateMapFile(amap):
    with open(mapFile,'w') as fo: 
        fo.write(str(amap))

def main():
    files = searchDaysDir()
    for dayFile in files:
        # print dayFile
        for user in Constant.users:
            rs = readSomeday(user,dayFile)
            generateTDB(rs,user,dayFile)
    
if __name__ == '__main__':
    main()



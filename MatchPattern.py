#usr/bin/env python
# -*- coding: utf-8 -*-

# users =['00306791d6a7','b8975a5dbfdf','50465d5aa129','50465d5aa117']
import os
import datetime
import Constant
# testuser = '50465d5aa129'
# dayFile = '2016-04-25'

# lowerRange = datetime.datetime.strptime('2016-04-11','%Y-%m-%d')


def searchToCompPatterns(user,testFile):
    patternfiles = [pfile for pfile in os.listdir(user) if pfile.startswith('pattern')]
    toCompareFiles = []
    for pfile in patternfiles:
        if pfile< testFile:
            toCompareFiles.append(pfile)

    patterns = ''
    for toCmpfile in toCompareFiles:
        with open(user+'/'+toCmpfile) as fo:
            patterns += fo.read()
    return patterns

    
    

def calculateHitTimes(patterns,testFile,level = 1):
    matchitems = []
    with open(testuser+'/'+testFile) as fo:
        for line in fo:
            if len(line.split(',')) == level:
                matchitems.append(line)
    hitTimes=0
    if not matchitems:
        return 0
    for matchitem in matchitems:
        if matchitem in patterns:
            # print testFile,matchitem
            hitTimes+=1
    # print '%s hit rate: %.2f%% on %s' % (user,hitTimes*1.0/len(matchitems)*100,testfile)
    return round(hitTimes*1.0/len(matchitems)*100,2)
        
def main(testuser,testStartDay,users):
    testDayFiles = [pfile for pfile in os.listdir(testuser) if pfile.startswith('pattern') and os.path.getsize(testuser+'/'+pfile) >0]
    testFiles = []
    for tfile in testDayFiles:
        if tfile.lstrip('pattern-week').rstrip('.txt') >= testStartDay:
            testFiles.append(tfile)
    rightRatio = 0
    for testfile in testFiles:
        hitSingleRatio = {}
        patterns = {}
        for user in users:
            patterns[user] = searchToCompPatterns(user,testfile)
            hitSingleRatio[user] = calculateHitTimes(patterns[user], testfile)
        # print hitSingleRatio
        # print sorted(hitSingleRatio.iteritems(),key=lambda p:p[1],reverse=True)
        levelOneResult = sorted(hitSingleRatio.iteritems(),key=lambda p:p[1],reverse=True)[0][0]
        greaterThanHalfPacent = [ value for value in hitSingleRatio.values() if value >= 50]
        # print len(greaterThanHalfPacent)
        levelMoreResult = ''
        # when matching more than one possible user, try to match second level FI(frequent items)
        if len(greaterThanHalfPacent) > 1:
            hitTwoRatio = {}
            for user in users:
                hitTwoRatio[user] = calculateHitTimes(patterns[user], testfile,2)
            # print  sorted(hitTwoRatio.iteritems(),key=lambda p:p[1],reverse=True)

            hitThreeRatio = {}
            for user in users:
                hitThreeRatio[user] = calculateHitTimes(patterns[user], testfile,3)
            # print  sorted(hitThreeRatio.iteritems(),key=lambda p:p[1],reverse=True)
            levelMoreResult = sorted(hitThreeRatio.iteritems(),key=lambda p:p[1],reverse=True)[0][0]
        result = levelMoreResult if levelMoreResult else levelOneResult
        if result == testuser:
            rightRatio+=1

    print '%s total right ratio is : %.2f%%' % (testuser,rightRatio*1.0/len(testFiles)*100)
    return rightRatio,len(testFiles)

if __name__ == '__main__':
    
    hitTimes = 0
    totalTimes =0
    for testuser in Constant.users:
        hit,total = main(testuser,Constant.testStartDay,Constant.users)
        hitTimes+=hit
        totalTimes+=total
    print 'all users total right ratio is : %.2f%%' % (hitTimes*1.0/totalTimes*100)
            



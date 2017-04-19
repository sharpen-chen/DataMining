#!/usr/bin/env python

import dpkt
import sys
import datetime
import socket
import os
import multiprocessing
import time
#import traceback

minTimes = 5
dirPath = "/tee"
savePath = '/tee2/MultiProcessPro0605'
upperRange = datetime.datetime.strptime('2016-04-14','%Y-%m-%d')
lowerRange = datetime.datetime.strptime('2016-04-12','%Y-%m-%d')

# return everyday's directory, the return dirs will be used to the muliprocess args
def searchDaysDir():
    rs = []
    files = os.listdir(dirPath)
    for onefile in files:
        if os.path.isdir(os.path.join(dirPath,onefile)):
            if '2016' in str(onefile):
	        dt = datetime.datetime.strptime(str(onefile),'%Y-%m-%d')
    	        if dt >= lowerRange and dt < upperRange :
    	            rs.append(onefile)
    return rs
    	
    

# parsing process : finished reading all pcap on a day before writing at a time , to reduce writing times             
def startParse(dayDir):
    pcaps = os.listdir(dirPath+'/'+dayDir)
    resultlst = []
    for onefile in pcaps:
        with open(dirPath+'/'+dayDir+'/'+onefile) as fo:
            pcap = dpkt.pcap.Reader(fo)
            try:
                dic = main(pcap)
                resultlst = resultlst+[dic]
            except Exception, e:
		print e
                print 'the file is wrong : '+ onefile
                continue
                #resultSet[onefile] = resultSet.get(onefile,[]) + []
    writeDayToTXT(resultlst,dayDir)
    

def writeDayToTXT(resultlst,dayDir):
    buff =''
    with open(savePath+"/"+dayDir+'.txt','w+') as fo:
        for lst in resultlst:
            for item,num  in lst.iteritems():
                if num >= minTimes:
                    buff = buff + str(item)+":"+str(num)+"\n"     
        fo.write(buff)             
    
def main(pcap):
        dic = {}
	for ts, buf in pcap:
		eth = dpkt.ethernet.Ethernet(buf)
		if not isinstance(eth.data, dpkt.ip.IP):
	 			continue
		ip = eth.data
		# print inet_to_str(ip.src)
		tcp = ip.data
		if(isinstance(tcp,dpkt.tcp.TCP)):
			if  len(tcp.data) > 0:
				try:
					http = dpkt.http.Request(tcp.data)
					if any(photoReq in http.uri for photoReq in ['jpg','png','gif']):
						continue
					arrive_time = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d-%H')
					if 'host' not in http.headers:
						continue
					host_value = http.headers['host']
					host = getSecondLevelHost(host_value)
					#lst.add(tuple([inet_to_str(ip.src),arrive_time,host]))
					mac_src = (eth.src).encode("hex")
					akey = tuple([mac_src,inet_to_str(ip.src),arrive_time,host])
					dic[akey] = dic.get(akey,0) + 1

				except (dpkt.dpkt.NeedData, dpkt.dpkt.UnpackError): 
					# print NeedData
					continue
	return dic

def inet_to_str(inet):
    """Convert inet object to a string

        Args:
            inet (inet struct): inet network address
        Returns:
            str: Printable/readable IP address
    """
    # First try ipv4 and then ipv6
    try:
        return socket.inet_ntop(socket.AF_INET, inet)
    except ValueError:
        return socket.inet_ntop(socket.AF_INET6, inet)

def getSecondLevelHost(host):
    second_level_host = ''
    # if host is DNSed ,then take second level host name
    if any(char.isalpha() for char in host):
        split_host = host.split('.')
        if len(split_host) < 2 :
            second_level_host = "".join(split_host)
        else:
            second_level_host = split_host[-2] # e.g.  www.jd.com  --> get jd
    # if host is IP:PORT then write it all 
    else:
        second_level_host = host
    return second_level_host

def writeToTXT(lst, fileName):
	with open(fileName+'.txt','w+') as fs:
		for item,num  in lst.iteritems():
		    if num >= minTimes:
		        fs.write(str(item)+":"+str(num)+"\n")

if __name__ == '__main__':
    t1 = time.time()
    try:
        
        dayDirs = searchDaysDir()
        # one process handle a whole day's pcaps
        pool = multiprocessing.Pool( processes=4 )
        for dir in dayDirs:
            pool.apply_async(startParse, (dir,)) 
        pool.close()
        tt = time.time()
        print 'after reading : ',tt-t1
        pool.join()
	print 'all stread down!'
    except Exception,e :
    	print e
    t2 = time.time()
    print 'total time :', t2-t1

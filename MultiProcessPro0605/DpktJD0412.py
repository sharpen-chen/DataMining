#!/usr/bin/env python

import dpkt
import sys
import datetime
import socket
import os
#import traceback

minTimes = 5
dirPath = "/tee"
savePath = '/tee2/201605'
upperRange = datetime.datetime.strptime('2016-06-01','%Y-%m-%d')
lowerRange = datetime.datetime.strptime('2016-05-01','%Y-%m-%d')

def scanPcap(dirPath):
    files = os.listdir(dirPath)
    for onefile in files:
        if os.path.isdir(os.path.join(dirPath,onefile)):
	    dt = datetime.datetime.strptime(str(onefile),'%Y-%m-%d')
    	    if dt >= lowerRange and dt < upperRange
                print dt
                #scanPcap(dirPath+'/'+onefile)
        elif 'cap' in onefile :
            startParse(onefile)
            
def startParse(onefile):
	with open(dirPath+'/'+onefile) as fo:
                pcap = dpkt.pcap.Reader(fo)
                try:
                    lst = main(pcap)
                    writeToTXT(lst, savePath +'/'+onefile)
                except Exception, e:
		    print e
                    print 'the file is wrong : '+ onefile
def main(pcap):
	#lst = set([])
        lst = {}
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
					lst[akey] = lst.get(akey,0) + 1

				except (dpkt.dpkt.NeedData, dpkt.dpkt.UnpackError): 
					# print NeedData
					continue
	return lst

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
    scanPcap(dirPath)
	

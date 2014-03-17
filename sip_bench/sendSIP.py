#!/usr/bin/env python
import os
import multiprocessing

numbers = ('0600000000','0600000001','0600000002')
MAX = 10

def sip( number , MAX):
	for i in range(MAX):
		i+=1	
		os.system("sipsak -c sip:0600000001@Test -M -v -s sip:"+str(number)+"@127.0.0.1:5090 -B 'Koukou from SIPSAk'")
	print 'Sending to...'+str(number)
	return

if __name__ == '__main__':
	jobs = []
	for num in numbers:
		p = multiprocessing.Process(target=sip, args=(num,MAX))
        	jobs.append(p)
        	p.start()

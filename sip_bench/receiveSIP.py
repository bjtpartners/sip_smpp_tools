#!/usr/bin/env python
import socket, time , re

LOCAL_IP = '127.0.0.1'
LOCAL_PORT = 5066

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.SOL_UDP)
sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
sock.bind((LOCAL_IP,LOCAL_PORT))

sock.setblocking(0)
ts = time.time()
while 1:
  try:
      data, addr = sock.recvfrom(1024)
  except socket.error, e:
      pass
  else:
    print data
    FROM_HOST = addr[0]
    FROM_PORT = addr[1]
    
    SIPRESPONSE = data.split('\r\n')
    
    if re.search('^MESSAGE', SIPRESPONSE[0]):
    	SIPMSG = 'SIP/2.0 200 OK\r\n'
    	SIPMSG += str(FROM_RESPONSE)+'\r\n'
    	SIPMSG += str(TO_RESPONSE)+'\r\n'
    	SIPMSG += str(CALLID_RESPONSE)+'\r\n'
    	SIPMSG += 'CSeq: 1 MESSAGE\r\n'
    	SIPMSG += 'Via: SIP/2.0/UDP '+str(FROM_HOST)+':'+str(FROM_PORT)+';alias;received='+str(FROM_HOST)+'\r\n'
    	for resp in SIPRESPONSE:
		if 'MESSAGE:' in resp:
			URI_RESPONSE = resp
		if 'From:' in resp:
			FROM_RESPONSE = resp
		if 'To:' in resp:
			TO_RESPONSE = resp
		if 'Call-ID:' in resp:
			CALLID_RESPONSE = resp
    	DATA = SIPRESPONSE[ len(SIPRESPONSE)-1 ]
	isMessage = 1
    else:
    	SIPMSG = 'SIP/2.0 406 Not Acceptable\r\n'
	isMessage = 0
    
    SIPMSG += 'User-Agent: SMSC\r\n'
    SIPMSG += 'Allow: INVITE, ACK, BYE, CANCEL, OPTIONS, MESSAGE\r\n'
    SIPMSG += 'Supported: timer, precondition, path, replaces\r\n'
    SIPMSG += 'Content-Length: 0\r\n'
    sock.sendto(str(SIPMSG), (FROM_HOST,FROM_PORT) )

sock.shutdown(1)
sock.close()



import os,sys,time,re,random,hashlib
import fcntl, re, urllib, uuid, socket
from urlparse import urlparse

class PythonSIP:
  debug = True
  min_port = 5065
  max_port = 5265
  
   ##
   # Final Response timer (in seconds)
   #
  fr_timer = 10
  
   ##
   # Lock file
   #
  lock_file = '/dev/shm/PhpSIP.lock'
  
   ##
   # Allowed methods array
   #
  allowed_methods = ["CANCEL","NOTIFY", "INVITE","BYE","REFER","OPTIONS","SUBSCRIBE","MESSAGE"]
  
   ##
   # Dialog established
   #
  dialog = False
  
   ##
   # The opened socket we listen for incoming SIP messages
   #
  socket = None
  
   ##
   # Source IP address
   #
  src_ip = None
  
  ##
   # Source IP address
   #
  user_agent = 'Python SIP'
  
  ##
   # CSeq
   #
  cseq = 20
  
  ##
   # Source port
   #
  src_port = None
  
  ##
   # Call ID
   #
  call_id = None
  
  ##
   # Contact
   #
  contact = None
  
  ##
   # Request URI
   #
  uri = None
  
  ##
   # Request host
   #
  host = '127.0.0.1'
  
  ##
   # Request port
   #
  port = 5060
  
  ##
   # Outboud SIP proxy
   #
  proxy = None
  
  ##
   # Method
   #
  method = None
  
  ##
   # Auth username
   #
  username = None
  
  ##
   # Auth password
   #
  password = None 
  
  ##
   # To
   #
  to = None
  
  	##
   # To tag
   #
  to_tag = None
  
  	##
	# From
	#
  sfrom = None
  
	##
   # From User
   #
  sfromuser = None

  ##
   # From tag
   #
  sfromtag = None
  
  ##
   # Via tag
   #
  via = None
  
  ##
   # Content type
   #
  content_type=None
  
  ##
   # Body
   #
  body = None
  
  ##
   # Received Response
   #
  response = None
  res_code = None 
  res_contact = None
  res_cseq_method = None
  res_cseq_number = None

  ##
   # Received Request
   #
  req_method = None
  req_cseq_method = None
  req_cseq_number = None
  req_contact = None
  
  ##
   # Authentication
   #
  auth = None
  
  ##
   # Routes
   #
  routes = []
  
  ##
   # Request vias
   #
  request_via = []
  
  # Additional headers
  extra_headers = []
 
  ##
   # Constructor
   # 
   # @param src_ip Ip address to bind (optional)
   #
  def __init__(self,src_ip = None):
    
    if src_ip is None:
        src_ip = "127.0.0.1"
    self.debug = True 
    self.src_ip = src_ip
    self.host = '127.0.0.1'
    self.port = 5060
    self.lock_file = '/dev/shm/PhpSIP.lock'
    self.createSocket()
  
  def __del__(self):
    self.closeSocket()
  
  def setDebug(self,status = False):
    self.debug = status
  
   # Gets src IP
   # @return string
  def getSrcIp(self):
    return self.src_ip
 


 
   # Gets port number to bind
  def getPort(self):
    fp = open(self.lock_file, "a+")
    #canWrite = fcntl.flock(fp, fcntl.LOCK_EX)
    size = os.path.getsize(self.lock_file)
    
    if size is not None:
      contents = fp.read(size)
      ports = contents.split(',')
    else:
      ports = False
    
    fp.truncate(0)
    fp.seek(0)
    
    # we are the first one to run, initialize "PID" => "port number" array
    if ports is not None:
      fp.write( str(self.min_port) )
      self.src_port =  self.min_port
    else:
      src_port = None
      
      for i in range( self.min_port , self.max_port+1) :
        if i in ports:
          src_port = i
          break
      
      ports.append( src_port )
      fp.write(','.join(ports))
      self.src_port = src_port
    fp.close()
     









  
   # Releases port
  def releasePort(self):
    fp = open(self.lock_file, 'r+')
    
    #canWrite = fcntl.flock(fp, fcntl.LOCK_EX)
    size = os.path.getsize(self.lock_file)
    content = fp.read(size)
    ports = content.split(',')
    
    key = ports.index(self.src_port)
    ports[key] = None
    
    if (len(ports) == 0):
     fp.close()
     self.lock_file = None
    else:
      fp.truncate(0)
      fp.seek(0)
      fp.write(','.join(ports))      
      fcntl.flock(fp, LOCK_UN)
      fp.close()      
  
  ##
   # Adds aditional header
   # 
   # @param string header
   #
  def addHeader(self,header):
    self.extra_headers.append(  header )
  
  ##
   # Sets From header
   # 
   # @param string from
   #
  def setFrom(self,sfrom):
    if re.search('/<.#>/',sfrom):
      self.sfrom = sfrom
    else:
      self.sfrom = '<'+str(sfrom)+'>'
    
    m = re.search('/sip:(.#)@/i',self.sfrom)
    if m is not None:
	self.sfromuser = m[1]
  
  ##
   # Sets method
   # 
   # @param string method
   #
  def setMethod(self,method):
    self.method = method
    
    if method == 'INVITE':
      body = "v=0\r\n"
      body += "o=click2dial 0 0 IN IP4 "+self.src_ip+"\r\n"
      body += "s=click2dial call\r\n"
      body += "c=IN IP4 "+self.src_ip+"\r\n"
      body += "t=0 0\r\n"
      body += "m=audio 8000 RTP/AVP 0 8 18 3 4 97 98\r\n"
      body += "a=rtpmap:0 PCMU/8000\r\n"
      body += "a=rtpmap:18 G729/8000\r\n"
      body += "a=rtpmap:97 ilbc/8000\r\n"
      body += "a=rtpmap:98 speex/8000\r\n"
      
      self.body = body
      
      self.setContentType(None)
    
    if method == 'REFER':
      self.setBody('')
    
    if method == 'CANCEL':
      self.setBody('')
      self.setContentType(None)
    
    if method == 'MESSAGE':
      self.setContentType(None)
  
  ##
   # Sets SIP Proxy
   # 
   # @param proxy
   #
  def setProxy(self,proxy):
    self.proxy = proxy
  
  ##
   # Sets request URI
   #
   # @param string uri
   #
  def setUri(self,uri):
    self.uri = uri
    self.to = '<'+str(uri)+'>'
    
    if self.proxy:
      if ":" in self.proxy:
        temp = self.proxy.split(":")
        
        self.host = temp[0]
        self.port = temp[1]
      else:
        self.host = self.proxy
    else:
	t_pos = uri.find("")
	if t_pos != -1:
		uri = uri[0:t_pos]
		url = uri.replace("sip:","sip:#")
		url = urlparse(url)
      	self.host = url.hostname

	try:
		self.port = url.port
	except:
		pass      
  
  ##
   # Sets username
   #
   # @param string username
   #
  def setUsername(self,username):
    self.username = username
  
  ##
   # Sets User Agent
   #
   # @param string user_agent
   #
  def setUserAgent(self,user_agent):
    self.user_agent = user_agent
  
  ##
   # Sets password
   #
   # @param string password
   #
  def setPassword(self,password):
    self.password = password
  
  ##
   # Sends SIP request
   # 
   # @return string Reply 
   #
  def send(self):
    if self.sfrom is None:
      print 'Missing From.'
    
    if self.method is None:
      print 'Missing Method.'
    
    if self.uri is None:
      print 'Missing URI.'
    
    data = self.formatRequest()
    self.sendData(data)
    self.readResponse()
    
    if self.method == 'CANCEL' and self.res_code == '200' :
      i = 0
      while self.res_code[0] != '4' and i < 2 :
        self.readResponse()
        i= i+1
    
    if self.res_code == '407':
      self.cseq= self.cseq+1
      self.auth()
      data = self.formatRequest()
      self.sendData(data)
      self.readResponse()
    
    if self.res_code == '401' :
      self.cseq=self.cseq+1
      self.authWWW()
      data = self.formatRequest()
      self.sendData(data)
      self.readResponse()
    
    if self.res_code[0] == '1' :
      i = 0
      while self.res_code[0] == '1' and i < 4 :
        self.readResponse()
        i=i+1
    
    self.extra_headers = []
    self.cseq= self.cseq+1
    return self.res_code
  




   # Sends data
  def sendData(self,data):
    self.sock.sendto(data,("127.0.0.1", 5061))
    
    if self.debug is not None:
      temp = data.split('\r\n')
      print "-. "+str(temp[0])+"\n"
  



  ##
   # Listen for request
   # 
   # @todo This needs to be improved
   #
  def listen(self,method):
    i = 0
    while self.req_method != method:
      self.readResponse() 
      i=i+1
      if i > 5:
        print "Unexpected request "+str(self.req_method)+"received."
  
   # Reads response
  def readResponse(self):
    self.response = self.sock.recv( 10000 )
    
    if self.debug is not None:
      temp = self.response.split("\r\n")
      print "<-- "+str(temp[0])+"\n"
    
    # Response
    result = []
    result = re.search( '/^SIP\/2\.0 ([0-9]{3})/' , self.response )
    if result :
      self.res_code = result[1].strip()
      res_class = self.res_code[0]
      if res_class == '1' or res_class == '2' :
        self.dialog = True
      self.parseResponse()
	# Request
    else:
      self.parseRequest()
  
   # Parse Response
  def parseResponse(self):
    # To tag
    result = []
    result = re.search('/^To: .#tag=(.#)/im', self.response )
    if result:
	 	self.to_tag = result[1].strip()
    
    # Route
    result = []
    result = re.findall('/^Record-Route: (.#)/im', self.response )
    if result:
      for route in result[1] :
        if route not in self.routes :
          self.routes.append( route.strip() )
    
    # Request via
    result = []
    self.request_via = []
    result = re.findall('/^Via: (.#)/im',self.response)
    if result:
      for via in result[1]:
        self.request_via.append( via.strip() )
    
    # Response contact
    result = []
    result = re.search('/^Contact:.#<(.#)>/im',self.response)
    if result:
      self.res_contact = result[1].strip()
      semicolon = self.res_contact.find("")
      if semicolon != -1:
        self.res_contact = self.res_contact[0:semicolon]
    
    # Response CSeq method
    result = []
    result = re.search('/^CSeq: [0-9]+ (.#)/im',self.response )
    if result :
      self.res_cseq_method = result[1].strip()
    
    # ACK 2XX-6XX - only invites - RFC3261 17.1.2.1
    if self.res_cseq_method == 'INVITE' and self.res_code[0] in ['2','3','4','5','6'] :
      self.ack()
    return self.res_code
  
   # Parse Request
  def parseRequest(self):
    temp = self.response.split("\r\n")
    temp = temp[0].split(" ")
    self.req_method = temp[0].strip()
    
    # Route
    result = []
    result = re.findall('/^Record-Route: (.#)/im',self.response)
    if result :
      for route in result[1]:
        if route.strip() not in self.routes:
          self.routes.append( route.strip() )
    
    # Request via
    result = []
    self.request_via = []
    result = re.findall('/^Via: (.#)/im' , self.response )
  
    if result :
      for via in result[1] :
        self.request_via.append(via.strip())
    
    # Method contact
    result = re.findall('/^Contact: <(.#)>/im' , self.response )
    if result:
      self.req_contact = result[1].strip()
      semicolon = self.res_contact.find("")
      if semicolon != -1 :
        self.res_contact = self.res_contact[0:semicolon]
    
    # Response CSeq method
    result = re.search('/^CSeq: [0-9]+ (.#)/im',self.response)
    if result :
      self.req_cseq_method = result[1].strip()
    
    # Response CSeq number
    result = re.search('/^CSeq: ([0-9]+) .#im',self.response )
    if result :
      self.req_cseq_number = result[1].strip()
  
   # Send Response
   # @param int code     Response code
   # @param string text  Response text
   #
  def reply(self,code,text):
    r = 'SIP/2.0 '+str(code)+' '+str(text)+"\r\n"
    # Via
    for via in self.request_via:
      r+= 'Via: '+str(via)+"\r\n"
    # From
    r+= 'From: '+str(self.sfrom)+'tag='+str(self.to_tag)+"\r\n"
    # To
    r+= 'To: '+str(self.to)+'tag='+str(self.sfromtag)+"\r\n"
    # Call-ID
    r+= 'Call-ID: '+(self.call_id)+"\r\n"
    #CSeq
    r+= 'CSeq: '+str(self.req_cseq_number)+' '+str(self.req_cseq_method)+"\r\n"
    # Max-Forwards
    r+= 'Max-Forwards: 70'+"\r\n"
    # User-Agent
    r+= 'User-Agent: '+str(self.user_agent)+"\r\n"
    # Content-Length
    r+= 'Content-Length: 0'+"\r\n"
    r+= "\r\n"
    self.sendData(r)
  
  ##
   # ACK
   #
  def ack(self):
    if self.res_cseq_method == 'INVITE' and self.res_code == '200':
      a = 'ACK '+str(self.res_contact)+' SIP/2.0'+"\r\n"
    else:
      a = 'ACK '+str(self.uri)+' SIP/2.0'+"\r\n"
    # Via
    a+= 'Via: '+str(self.via)+"\r\n"
    # Route
    if self.routes:
      for route in self.routes:
        a+= 'Route: '+str(route)+"\r\n"
    # From
    if self.sfromtag is None:
		self.setFromTag()
    a+= 'From: '+str(self.sfrom)+'tag='+str(self.sfromtag)+"\r\n"
    # To
    if self.to_tag :
      a+= 'To: '+str(self.to)+'tag='+str(self.to_tag)+"\r\n"
    else:
      a+= 'To: '+str(self.to)+"\r\n"
    # Call-ID
    if self.call_id is None:
		self.setCallId()
    a+= 'Call-ID: '+str(self.call_id)+"\r\n"
    #CSeq
    a+= 'CSeq: '+str(self.cseq)+' ACK'+"\r\n"
    # Authentication
    if self.res_code == '200' and self.auth :
      a+= 'Proxy-Authorization: '+str(self.auth)+"\r\n"
    # Max-Forwards
    a+= 'Max-Forwards: 70'+"\r\n"
    # User-Agent
    a+= 'User-Agent: '+str(self.user_agent)+"\r\n"
    # Content-Length
    a+= 'Content-Length: 0'+"\r\n"
    a+= "\r\n"
    self.sendData(a)
  
   # Formats SIP request
   # @return string
  def formatRequest(self):
    if self.method in ('BYE','REFER','SUBSCRIBE'):
      r = str(self.method)+' '+str(self.res_contact)+' SIP/2.0'+"\r\n"
    else:
      r = str(self.method)+' '+str(self.uri)+' SIP/2.0'+"\r\n"
    
    # Via
    if self.method != 'CANCEL':
      self.setVia()
    r+= 'Via: '+str(self.via)+"\r\n"
    
    # Route
    if self.method != 'CANCEL' and self.routes :
      for route in self.routes:
        r+= 'Route: '+str(route)+"\r\n"
    
    # From
    if self.sfromtag :
		self.setFromTag()
    r+= 'From: '+str(self.sfrom)+'tag='+str(self.sfromtag)+"\r\n"
    
    # To
    if self.dialog and self.method not in ("INVITE","CANCEL","NOTIFY") and self.to_tag :
      r+= 'To: '+str(self.to)+'tag='+str(self.to_tag)+"\r\n"
    else:
      r+= 'To: '+str(self.to)+"\r\n"
    
    # Authentication
    if self.auth :
      r+= str(self.auth)+"\r\n"
      self.auth = None
    
    # Call-ID
    if self.call_id is None:
		self.setCallId()
    r+= 'Call-ID: '+str(self.call_id)+"\r\n"
    
    #CSeq
    if self.method == 'CANCEL':
      self.cseq-=1
    r+= 'CSeq: '+str(self.cseq)+' '+str(self.method)+"\r\n"
    
    # Contact
    if self.method != 'MESSAGE':
      r+= 'Contact: <sip:'+str(self.sfromuser)+'@'+str(self.src_ip)+':'+str(self.src_port)+'>'+"\r\n"
    
    # Content-Type
    if self.content_type:
      r+= 'Content-Type: '+str(self.content_type)+"\r\n"
    
    # Max-Forwards
    r+= 'Max-Forwards: 70'+"\r\n"
    
    # User-Agent
    r+= 'User-Agent: '+str(self.user_agent)+"\r\n"
    
    # Additional header
    for header in self.extra_headers:
      r+= str(header)+"\r\n"
    
    # Content-Length
    r+= 'Content-Length: '+str(len(self.body))+"\r\n"
    r+= "\r\n"
    r+= str(self.body)
    
    return r
  
   # Sets body
  def setBody(self,body):
    self.body = body
  
   # Sets Content Type
  def setContentType(self,content_type = None):
    if content_type is not None:
      self.content_type = content_type
    else:
      if self.method == 'INVITE':
          self.content_type = 'application/sdp'
      elif self.method == 'MESSAGE':
          self.content_type = 'text/html charset=utf-8'
      else:
          self.content_type = None
  
   # Sets Via header
  def setVia(self):
    rand = random.randint(100000,999999)
    self.via = 'SIP/2.0/UDP '+str(self.src_ip)+':'+str(self.src_port)+'rportbranch=z9hG4bK'+str(rand)
  
   # Sets from tag
  def setFromTag(self):
    self.sfromtag = random.randint(10000,99999)
  
   # Sets call id
  def setCallId(self):
    self.call_id = str(hashlib.md5( str(uuid.uuid1()) ))+'@'+str(self.src_ip)
  
   # Gets value of the header from the previous request
   # @param string name Header name
   # @return string or False
  def getHeader(self,name):
    result = re.search('/^'+str(name)+': (.#)/m',self.response)
    if result:
      return result[1].strip()
    else:
      return False
  
   # Calculates Digest authentication response
  def auth(self):
    if self.username is None:
      print "Missing username"
    
    if self.password is None:
      print "Missing password"
    
    # realm
    result = re.search('/^Proxy-Authenticate: .# realm="(.#)"/imU',self.response)
    if not result:
      print "Can't find realm in proxy-auth"
    
    realm = result[1]
    
    # nonce
    result = re.search('/^Proxy-Authenticate: .# nonce="(.#)"/imU',self.response)
    if not result :
      print "Can't find nonce in proxy-auth"
    
    nonce = result[1]
    
    ha1 = hashlib.md5(str(self.username)+':'+str(realm)+':'+str(self.password))
    ha2 = hashlib.md5(str(self.method)+':'+str(self.uri))
    
    res = hashlib.md5(str(ha1)+':'+str(nonce)+':'+str(ha2))
    
    self.auth = 'Proxy-Authorization: Digest username="'+str(self.username)+'", realm="'+str(realm)+'", nonce="'+str(nonce)+'", uri="'+str(self.uri)+'", response="'+str(res)+'", algorithm=MD5'
  
   # Calculates WWW authorization response
  def authWWW(self):
    if self.username is None:
      print "Missing auth username"
    
    if self.password is None:
      print "Missing auth password"
    
    qop_present = False
    if self.response.find('qop='): 
      qop_present = True
    
    result = re.search('/^WWW-Authenticate: .# realm="(.#)"/imU',self.response)
    if not result:
      print "Can't find realm in www-auth"
    
    realm = result[1]
    
    result = re.search( '/^WWW-Authenticate: .# nonce="(.#)"/imU',self.response )
    if not result:
      print "Can't find nonce in www-auth"
    
    nonce = result[1]
    
    ha1 = hashlib.md5(str(self.username)+':'+str(realm)+':'+str(self.password))
    ha2 = hashlib.md5(str(self.method)+':'+str(self.uri))
    
    if qop_present == True:
      cnonce = hashlib.md5(time.time())
      res = hashlib.md5(str(str(ha1)+':'+str(nonce)+':00000001:'+str(cnonce)+':auth:'+str(ha2)))
    else:
      res = hashlib.md5(str(str(ha1)+':'+str(nonce)+':'+str(ha2)))
    
    self.auth = 'Authorization: Digest username="'+str(self.username)+'", realm="'+str(realm)+'", nonce="'+str(nonce)+'", uri="'+str(self.uri)+'", response="'+str(res)+'", algorithm=MD5'
    
    if qop_present is True:
      self.auth+= ', qop="auth", nc="00000001", cnonce="'+str(cnonce)+'"'
  
  def createSocket(self):
    self.getPort()
    
    if self.src_ip is None:
      print "Source IP not defined."
    self.sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM, socket.SOL_UDP)
    self.sock.bind((self.src_ip, self.src_port))
    self.sock.listen(1)

    #self.sock.setsockopt( socket.SOL_SOCKET, socket.SO_RCVTIMEO, self.fr_timer )
    #self.sock.setsockopt( socket.SOL_SOCKET, socket.SO_SNDTIMEO, 5)
    #struct.pack('LL', 12, 34567) ?   
  
   # Close the connection
   # @return bool True on success
  def closeSocket(self):
	if self.sock is not None:
	  self.sock.shutdown(1)
	  self.sock.close()
    	  #self.releasePort()
  
  # Resets callid, to/from tags etc.
  def newCall(self):
    self.cseq = 20
    self.call_id = None
    self.to_tag = None
    self.sfromtag = None
    
    # Body
    self.body = None
    
    # Received Response
    self.response = None
    self.res_code = None
    self.res_contact = None
    self.res_cseq_method = None
    self.res_cseq_number = None

    # Received Request
    self.req_method = None
    self.req_cseq_method = None
    self.req_cseq_number = None
    self.req_contact = None
    
    self.routes = []
    self.request_via = []

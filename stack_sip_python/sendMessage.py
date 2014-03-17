import pythonsip

try:
  api = pythonsip.PythonSIP('127.0.0.1') 
  api.addHeader('Event: MESSAGE')
  api.setMethod('MESSAGE')
  api.setFrom('sip:10000@127.0.0.1:5060')
  api.setUri('sip:10000@127.0.0.1:5061')
  api.setBody('HELLO WORLD From PHP')
  res = api.send()
  print "res1: res\n"
  
except Exception,e :
  print str( e )+"\n"


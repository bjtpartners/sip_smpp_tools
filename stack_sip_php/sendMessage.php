<?php
require_once('PhpSIP.class.php');

try
{
  $api = new PhpSIP('127.0.0.1'); // IP we will bind to
  $api->addHeader('Event: MESSAGE');
  $api->setMethod('MESSAGE');
  $api->setFrom('sip:10000@127.0.0.1:5060');
  $api->setUri('sip:10000@127.0.0.1:5061');
  $api->setBody('HELLOW WORLD From PHP');
  $res = $api->send();
  echo "res1: $res\n";
  
} catch (Exception $e) {
  
  echo $e->getMessage()."\n";
}

?>

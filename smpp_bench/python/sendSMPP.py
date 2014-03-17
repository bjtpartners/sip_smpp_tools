#!/usr/bin/env python
from libs import smpplib
#
# SMPP Library usage example
#
#import smpplib

def recv_handler(self, **args):
    print 'Message received:', args


if __name__ == '__main__':
    client = smpplib.client.Client("127.0.0.1", 2775)
    client.connect()
    client.bind_transmitter(system_id="LOGIN", password="PASSWORD", system_type='TEST')
    msg = "This is a test message............................."
    length = len(msg)
    splitat = 160
    parts = length/splitat +1
    if length > splitat:
        for k in range(parts):
            msgpart =  msg[k*splitat:k*splitat+splitat]
            client.send_message(source_addr_ton=2,
                                source_addr_npi = 4,
                                source_addr='0600000000',
                                dest_addr_ton=smpplib.command.SMPP_TON_UNK,
                                dest_addr_npi = smpplib.command.SMPP_NPI_ISDN,
                                destination_addr='0600000003',
                                sar_msg_ref_num = 1,
                                sar_total_segments = parts,
                                sar_segment_seqnum = k+1,
                                message_payload=msgpart)
    else:
        client.send_message(source_addr_ton=5,
                                source_addr_npi = 3,
                                source_addr='0600000000',
                                dest_addr_ton=smpplib.command.SMPP_TON_UNK,
                                dest_addr_npi = smpplib.command.SMPP_NPI_ISDN,
                                destination_addr='0600000003',
                                #protocol_id=smpplib.command.SMPP_PID_RIP,
                                short_message=msg)
    print "Sent.."
    client.unbind()
    client.disconnect()

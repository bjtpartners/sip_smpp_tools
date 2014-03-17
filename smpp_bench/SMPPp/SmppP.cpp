#include <iostream>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <getopt.h>
#include "connectionSMPP.h"

#define LOGIN   "login"
#define PASSWD  "passwd"

void help(){
    printf("How to use SmppP ... \n");
    printf("   -f : SMS From\n");
    printf("   -t : SMS To\n");
    printf("   -m : SMS Message\n");
    printf("   -S : IP Server Dst\n");
    printf("   -P : Port Server Dst\n");
    printf("   -n : Number of sms to send\n");
    return;
}

int main(int argc,char **argv){
    if(argc>=5){
    Connection_SMPP *smpp = NULL;
    SMS *sms = NULL;
    int c;
    char *sms_source  = NULL;
    char *sms_dest    = NULL;
    char *sms_message = NULL;
    char *server_src  = NULL;
    char *server_port = NULL;
    int   sms_nb      = 1;

    while((c=getopt(argc, argv, "f:t:m:S:P:n:"))!=-1) {//: quand il y a un paramettre
        switch(c) {
            case 'f':
                    sms_source  = optarg;
                    break;
            case 't':
            	    sms_dest    = optarg;
	            break;
            case 'm':
                    sms_message = optarg;
                    break;
            case 'S':
                    server_src  = optarg;
                    break;
            case 'P':
                    server_port = optarg;
                    break;
	    case 'n':
                    sms_nb      = atoi(optarg);
		    break;
            default:
                    abort();
        }
    }

    printf("SMS Source   : [%s]\n", sms_source);
    printf("SMS Dest     : [%s]\n", sms_dest);
    printf("SMS Message  : [%s]\n", sms_message);
    printf("Server Src   : [%s]\n", server_src);
    printf("Server Port  : [%s]\n", server_port);
    printf("Nb of SMS    : [%d]\n", sms_nb);

    if(sms_source && sms_dest && sms_message){
	sms = new SMS();
        sms->src = (char*)malloc(sizeof(char)*21);
        sms->dst = (char*)malloc(sizeof(char)*21);
        sms->msg = (char*)malloc(sizeof(char)*256);
        strcpy((char*)sms->src,(char*)sms_source);
        strcpy((char*)sms->dst,(char*)sms_dest);
        strcpy((char*)sms->msg,(char*)sms_message);
    }else{
	printf("SMS is invalid");
    }

    smpp = new Connection_SMPP(server_src,server_port,
				LOGIN,PASSWD,BIND_TRANSMITTER,false);
    
    printf("Wait...");
    sleep(2);

    while(sms_nb-- > 0 && smpp->sendSMS(*sms)==true);

    delete smpp;

    }else{
    	help();
    }
    return 0;
}

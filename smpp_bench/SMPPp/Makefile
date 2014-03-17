make:
	clang -Wall -pedantic -g -c sip/udp_methode.c -o sip/udp_methode.o
	clang -Wall -pedantic -g -c smpp/smpp.c -o sip/smpp.o
	clang -Wall -pedantic -g -c smpp/tcp.c -o smpp/tcp.o
	clang++ -Wall -pedantic -g -std=c++11 -c connectionSMPP.cpp -o connectionSMPP.o
	clang++ -Wall -pedantic -g SmppP.cpp -o smppp connectionSMPP.o sip/udp_methode.o smpp/tcp.o smpp/smpp.o -lsmpp34 -std=c++11

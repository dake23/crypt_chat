# -*- coding: utf-8 -*-
import json
import time
import random
import re
import socket
import threading


_server_ip = "192.168.1.9"
_server_port = 5544
_address_bind = _server_ip, _server_port

_recvbuffer = 1024




def main():
	
	_updsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	_updsock.bind(_address_bind)
	
	#get message from client 1
	_response, _addC = _updsock.recvfrom(_recvbuffer)
	
	_addC1 = (str(_addC[0]) + "," + str(_addC[1]))
	
	print("Message from client1: ", _response.decode('utf-8'), "\nAddres: ", _addC)
	#_updsock.sendto(''.encode('utf-8'),_addC)
	
	#get message from client 2
	_response, _addC = _updsock.recvfrom(_recvbuffer)
	print("Message from client2: ", _response.decode('utf-8'), "\nAddres: ", _addC)
	_updsock.sendto(_addC1.encode('utf-8'),_addC)
	
	_updsock.close()
	
	
main()
input()
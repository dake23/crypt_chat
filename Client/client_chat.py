# -*- coding: utf-8 -*-
import json
import time
import random
import re
import socket
import threading


_server_ip = "192.168.1.9"
_server_port = 5544
_address_server = _server_ip, _server_port

_recvbuffer = 1024




def main():
	
	
	_updsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	
	#send message
	print('Send message to STUN')
	_updsock.sendto('I am client 2'.encode('utf-8'),_address_server)
	
	_response, _addS = _updsock.recvfrom(_recvbuffer)
	_response = _response.decode('utf-8')
	print(_response)
	_addC2 = _response.split(',')
	_addC2 = _addC2[0],int(_addC2[1])
	print("Send message to client2")
	_updsock.sendto('Privet i am client 2'.encode('utf-8'),_addC2)
	_response, _addC = _updsock.recvfrom(_recvbuffer)
	print("Message from client1:",_response.decode('utf-8'))
	_updsock.close()
	
	
main()
input()
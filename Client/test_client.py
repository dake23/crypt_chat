# -*- coding: utf-8 -*-
import json
import time
import random
import re
import socket
import threading


_server_ip = "192.168.1.3"
_server_port = 5544
_address_server = _server_ip, _server_port

_recvbuffer = 1024


global talkToServer

'''
class sendServer(threading.Thread):
	def __init__(self):
        threading.Thread.__init__(self)
        self.running = 1
        self.conn = None
        self.addr = None
    def run(self):
        
    def kill(self):
        self.running = 0

class listenServer(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.host = None
		self.sock = None
		self.running = 1
	def run(self):
		self.sock = socket.socket()
		self.sock.connect(_address_server)
		
		while self.running:
			response = self.sock.recv(_recvbuffer).decode('utf-8')
			print(response)
		
	def send(self,_req):
		self.sock.send(_req.encode('utf-8'))
		
	def kill(self):
		self.send('BYE')
		self.sock.close()
		self.running = 0

class Text_Input(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.running = 1
	def run(self):
		while self.running == True:
			text = input('INPUT: ')
			if 'exit' in text:
				self.kill()
				
			elif 'Exit' in text:
				self.kill()
				
			elif 'LIST' in text:
				req_str = str(text)
				talkToServer.send(req_str)
				
			time.sleep(0)
	def kill(self):
		self.running = 0
		talkToServer.kill()
		#НАПИСАТЬ ЗАКРЫТИЕ ВСЕХ ПОТОКОВ
		# плюс отправку сигнала на сервер о закрытие сессии

'''

def main():
	class listenServer(threading.Thread):
		def __init__(self):
			threading.Thread.__init__(self)
			self.host = None
			self.sock = None
			self.running = 1
		def run(self):
			self.sock = socket.socket()
			self.sock.connect(_address_server)
			
			while self.running:
				response = self.sock.recv(_recvbuffer).decode('utf-8')
				print(response)
			
		def send(self,_req):
			self.sock.send(_req.encode('utf-8'))
			
		def kill(self):
			self.send('BYE')
			self.sock.close()
			self.running = 0

	class Text_Input(threading.Thread):
		def __init__(self):
			threading.Thread.__init__(self)
			self.running = 1
		def run(self):
			while self.running == True:
				text = input('INPUT: ')
				if 'exit' in text:
					self.kill()
					
				elif 'Exit' in text:
					self.kill()
					
				elif 'LIST' in text:
					req_str = str(text)
					talkToServer.send(req_str)
					
				time.sleep(0)
		def kill(self):
			self.running = 0
			talkToServer.kill()
			#НАПИСАТЬ ЗАКРЫТИЕ ВСЕХ ПОТОКОВ
			# плюс отправку сигнала на сервер о закрытие сессии
		
		
		
		
	talkToServer = listenServer()
	talkToServer.start()
	input_message = Text_Input()
	input_message.start()
		
	
	
	'''
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
	'''
	
main()
input()
# -*- coding: utf-8 -*-
import json
import time
import random
import re
import socket
import threading
import select

_server_ip = "192.168.43.65"
_server_port = 5544
_address_server = _server_ip, _server_port

_recvbuffer = 1024

_yourself_ip = "192.168.43.65"
_serverChat_port = int(random.uniform(5545,5550))
_address_bind = _yourself_ip,_serverChat_port
_maxconnect = 2

global talkToServer
global serverChat

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

	class serverChat(threading.Thread):
		
		def __init__(self,clientSock, addr):
			threading.Thread.__init__(self)
			self.addr = addr
			self.sock = clientSock
			self.running = 1
			self.login = ""
			
		def run(self):
			
			global client_array
			#client conn
			while self.running:
				inputready,outputready,exceptready = select.select ([self.sock],[self.sock],[])
				for input_item in inputready:
					#get response
					response = self.sock.recv(_recvbuffer).decode('utf-8')
					if response:
						# do action
						self.response_operation(response)
					else: break
				time.sleep(0)
			
			self.sock.close()
			print("Client disconnect")
			
		def response_operation(self,_response):
			global client_array
			
			if 'LOGIN' in _response:
				_res_mas = _response.split(' ')
				
				self.login = _res_mas[1]
				client_array[self.login] = self
				print('Client ', _res_mas[1] , ' start chat')
		
			else:
				print(self.login,": ", _response)
		
		def send(self,_request):
			self.sock.send(_request.encode('utf-8'))
	
	class clientChat(threading.Thread):
		def __init__(self,server_addr):
			threading.Thread.__init__(self)
			self.host = None
			self.sock = None
			self.serv_addr = server_addr
			self.login_server = None
			
			self.running = 1
			
		def run(self):
			global login
		
		
			self.sock = socket.socket()
			self.sock.connect(self.serv_addr)
			
			self.sock.send('LOGIN ',login)
			
		def response_operation(self,_response):
			global server_array
			
			if 'LOGIN' in _response:
				_res_mas = _response.split(' ')
				
				self.login = _res_mas[1]
				server_array[self.login] = self
				print(' ', _res_mas[1] , ' start chat')
		
			else:
				print(self.login,": ", _response)
		
		def send(self,_request):
			self.sock.send(_request.encode('utf-8')) 
	
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
				inputready,outputready,exceptready = select.select ([self.sock],[self.sock],[])
				for input_item in inputready:
					response = self.sock.recv(_recvbuffer).decode('utf-8')
					if response:
						self.o_response(response)
					else: break
				time.sleep(0)
				
			self.sock.close()
			print('Close')
			
		def o_response(self,_response):
			
			if 'LIST' in _response:
				_res_mas = _response.split(' ')
				_user_list = _res_mas[1].split(';')
				
				print('User list ',_user_list,"\n")
			elif 'SESSION' in _response:
				_res_mas = _response.split(' ')
				print('User ',_res_mas[1], 'want start chat. Address to connect: ',_res_mas[2])
				addr,port = _res_mas[2].split(':')
				serv_adr = str(addr), int(port)
				client = clientChat(serv_adr)
				client.start()
				
		def send(self,_req):
			self.sock.send(_req.encode('utf-8'))
			
		def kill(self):
			self.send(str('BYE'))
			self.running = 0
			
	'''
					Описание команды CREATE [[ID] [IP:PORT]]
					Команда создания p2p чата с клиентом ID
					Открывается порт для старта соединения
	'''
	class Text_Input(threading.Thread):
		def __init__(self):
			threading.Thread.__init__(self)
			self.running = 1
		def run(self):
			while self.running == True:
				text = input('INPUT: ')
				if 'exit' in text or 'Exit' in text:
					self.kill()
					
				elif 'LIST' in text:
					req_str = str(text)
					talkToServer.send(req_str)
	
				
				elif 'CREATE' in text:
					text = text + " "+str(_yourself_ip) + ":"+ str(_serverChat_port)
					req_str = str(text)
					talkToServer.send(req_str)
					
				elif 'CHAT' in text:
					req_str = text.split(':')
					login_c = req_str[1]
					req_str = req_str[2]
					
					if login_c in client_array:
						client_array[login_c].send(req_str)
					elif login_c in server_array:
						server_array[login_c].send(req_str)
					
				time.sleep(1)
		def kill(self):
			self.running = 0
			talkToServer.kill()
			#НАПИСАТЬ ЗАКРЫТИЕ ВСЕХ ПОТОКОВ
			# плюс отправку сигнала на сервер о закрытие сессии
		
		
		
	login = input('INPUT login: ')	
	
	talkToServer = listenServer()
	talkToServer.start()
	time.sleep(1)
	talkToServer.send('LOGIN '+str(login))
	input_message = Text_Input()
	input_message.start()
	
	# start server chat
	chat_sock = socket.socket()
	chat_sock.bind(_address_bind)
	chat_sock.listen(_maxconnect)
	# for first start
	count_thread = 1
	#dictonary threads -> ip:thread
	client_array = {}
	while count_thread >= 1:
		
		# create new connection
		conn, addr = chat_sock.accept()
		print("START NEW CHAT with ", str(addr))
		
		#client_array[addr[0]] = talkToClient(conn,addr).start()
		serverChat(conn,addr).start()
		serverChat.send("LOGIN ",login)
		
		#get current count threads
		count_thread = threading.active_count()
	
	
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
#input('Enter for close')
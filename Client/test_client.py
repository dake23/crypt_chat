# -*- coding: utf-8 -*-
import json
import time
import random
import re
import socket
import threading
import select
import os
import hashlib
from Crypto.Cipher import AES
from Crypto import Random




_server_ip = "192.168.1.5"
_server_port = 5544
_address_server = _server_ip, _server_port

_recvbuffer = 1024

_yourself_ip = "192.168.1.5"
_serverChat_port = int(random.uniform(5545,5550))
_address_bind = _yourself_ip,_serverChat_port
_maxconnect = 2

global talkToServer
global serverChat
global login
global server_array
global client_array
global K
global K1

MODE = AES.MODE_CFB

def main():
	global login
	global server_array
	global client_array
	global MODE
	global K
	global K1
	
	def encrypt(text,IV,KEY):
		c_obj = AES.new(KEY,MODE,IV)
		cipher_text = c_obj.encrypt(text)
		return cipher_text

	def decrypt(cipher_text,IV,KEY):
		c_obj = AES.new(KEY,MODE,IV)
		text = c_obj.decrypt(cipher_text)
		return text
	def get_IV():
		IV = Random.new().read(AES.block_size)
		return IV
	
	class serverChat(threading.Thread):
		
		def __init__(self,clientSock, addr,login):
			threading.Thread.__init__(self)
			self.addr = addr
			self.sock = clientSock
			self.running = 1
			self.y_login = login
			self.login = ""
			self.iv = ""
			self.key = ""
			
		def run(self):
			global server_array
			global client_array
			global K,K1
			
			
			# ----- START Create session key
			self.login = self.sock.recv(_recvbuffer).decode('utf-8')
			client_array[self.login] = self
			#send y_login
			self.sock.send(self.y_login.encode('utf-8'))
				
			#step 1 - get rA from client
			rA = self.sock.recv(_recvbuffer).decode('utf-8')
			
			w_str = "_".join([str(rA),str(K1)])
			self.key = hashlib.md5(w_str.encode('utf-8')).hexdigest()
			
			self.iv = get_IV()
			
			self.sock.send(self.iv)
			
			
			# ----- END Create session key
			
			#self.send('LOGIN '+str(self.y_login))
			#client conn
			while self.running:
				inputready,outputready,exceptready = select.select ([self.sock],[self.sock],[])
				for input_item in inputready:
					#get response
					response = self.sock.recv(_recvbuffer)#.decode('utf-8')
					if response:
						# do action
						self.response_operation(decrypt(response,self.iv,self.key).decode('utf-8'))
					else: break
				time.sleep(0)
			
			self.sock.close()
			print("Client disconnect")
			
		def response_operation(self,_response):
			
			if 'LOGIN' in _response:
				_res_mas = _response.split(' ')
				
				self.login = _res_mas[1]
				client_array[self.login] = self
				print('Client ', _res_mas[1] , ' start chat')
				print('\nServer connection ',client_array)
		
			else:
				print("\n",self.login,": ", _response,"\n")
		
		def send(self,_request):
			self.sock.send(encrypt(_request,self.iv,self.key))#.encode('utf-8'))
	
	class clientChat(threading.Thread):
		def __init__(self,server_addr,login):
			threading.Thread.__init__(self)
			self.host = None
			self.sock = None
			self.serv_addr = server_addr
			self.login_server = None
			self.y_login = login
			self.running = 1
			self.iv = ""
			self.key = ""
			
		def run(self):
			global server_array
			global client_array
			global K
			global K1
				
			self.sock = socket.socket()
			self.sock.connect(self.serv_addr)
			
			# ----- START Create session key
			self.sock.send(self.y_login.encode('utf-8'))
			
			#get login server
			self.login_server = self.sock.recv(_recvbuffer).decode('utf-8')
			server_array[self.login_server] = self
			#step 1 - generate rA and send to server
			rA = int(random.uniform(222222,99999999))
			self.sock.send(str(rA).encode('utf-8'))
			
			#step 2 - generate W - session key
			w_str = "_".join([str(rA),str(K1)])
			self.key = hashlib.md5(w_str.encode('utf-8')).hexdigest()
			
			self.iv = self.sock.recv(_recvbuffer)
			
			# ----- END Create session key
			
			while self.running:
				inputready,outputready,exceptready = select.select ([self.sock],[self.sock],[])
				for input_item in inputready:
					#get response
					response = self.sock.recv(_recvbuffer)#.decode('utf-8')
					if response:
						# do action
						self.response_operation(decrypt(response,self.iv,self.key).decode('utf-8'))
					else: break
				time.sleep(0)
			
			
			
		def response_operation(self,_response):
						
			if 'LOGIN' in _response:
				_res_mas = _response.split(' ')
				
				self.login = _res_mas[1]
				server_array[self.login] = self
				print(' ', _res_mas[1] , ' start chat')
				print('\nClient connection ',server_array)
		
			else:
				print("\n",self.login_server,": ", _response,"\n")
		
		def send(self,_request):
			self.sock.send(encrypt(_request,self.iv,self.key))#.encode('utf-8')) 
	
	class listenServer(threading.Thread):
		def __init__(self,key):
			threading.Thread.__init__(self)
			self.host = None
			self.sock = None
			self.iv = ""
			self.key = key
			self.running = 1
		def run(self):
		
			global login
			global K
			global K1
			
			self.sock = socket.socket()
			self.sock.connect(_address_server)
			
			#----- START auth on server
			
			#step 1 - send username
			self.sock.send(('LOGIN '+str(login)).encode('utf-8'))
			
			#step 2 - get servername and rB   response = servername;rB
			response = self.sock.recv(_recvbuffer).decode('utf-8')
			servername,rB = response.split(';')
			print('sn = ',servername,'\nrB = ',rB)
			#step 3 - generate rA
			rA = int(random.uniform(222222,99999999))
			print('rA = ',rA)
			
			#step 4 - generate IV and encry string servername_rB_rA on key
			self.iv = get_IV()
			plain_text = servername+'_'+str(rB)+'_'+str(rA)
			cipher_text = encrypt(plain_text,self.iv,self.key)
			
			#step 5 - send to server iv
			self.sock.send(self.iv)
			time.sleep(1)
			
			#step 6 - send to server cipher_text
			self.sock.send(cipher_text)
			
			#step 7 - get from server cipher string username_rA
			response = self.sock.recv(_recvbuffer)
			username,_rA = decrypt(response,self.iv,self.key).decode('utf-8').split('_')
			if int(_rA) == int(rA):
				print('Auth success')
			else:
				print('Not auth')
			
			#---------END AUTH ------------
			
			while self.running:
				inputready,outputready,exceptready = select.select ([self.sock],[self.sock],[])
				for input_item in inputready:
					response = self.sock.recv(_recvbuffer)#.decode('utf-8')
					if response:
						self.o_response(decrypt(response,self.iv,self.key).decode('utf-8'))
					else: break
				time.sleep(0)
				
			self.sock.close()
			print('Close')
			
		def o_response(self,_response):
			global K,K1
			if 'LIST' in _response:
				_res_mas = _response.split(' ')
				_user_list = _res_mas[1].split(';')
				
				print('User list ',_user_list,"\n")
			elif 'SESSION' in _response:
				_res_mas = _response.split(' ')
				print('User ',_res_mas[1], 'want start chat. Address to connect: ',_res_mas[2])
				addr,port = _res_mas[2].split(':')
				serv_adr = str(addr), int(port)
				client = clientChat(serv_adr,login)
				client.start()
			elif 'KEYS' in _response:
				_res_mas = _response.split(':')
				K = _res_mas[1]
				K1 = _res_mas[2]
				
				
		def send(self,_req):
			self.sock.send(encrypt(_req,self.iv,self.key))#.encode('utf-8'))
			
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
		
		
	# get secret key for start messeges with server	
	KEY = ""
	login = input('INPUT login: ')
	pwd = login+'/'
	if os.path.exists(login):
		input('Exist user auth file')
		secret_key = input("Input your secret code: ")
		cipher_key = open(pwd+'key','rb').readline()
		iv = open(pwd+'iv','rb').readline()
		KEY = decrypt(cipher_key,iv,secret_key+secret_key).decode('utf-8')
		KEY += KEY
				
	else:
		#create user dir
		os.mkdir(login)
		key = input("First setup. Please input you activete code: ")
		secret_key = input("For secure you active code, input secret code out of 8 symbol: ")
		
		#key must be 16 len
		
		iv = get_IV()
		cipher_key = encrypt(key,iv,secret_key+secret_key)
		open(pwd+'key','wb').write(cipher_key)
		open(pwd+'iv','wb').write(iv)
		KEY = key+key
	#-------------------------
	
	
		
	
	talkToServer = listenServer(KEY)
	talkToServer.start()
	time.sleep(1)
	
	#talkToServer.send('LOGIN '+str(login))
	
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
	server_array = {}
	while count_thread >= 1:
		
		# create new connection
		conn, addr = chat_sock.accept()
		print("START NEW CHAT with ", str(addr))
		
		#client_array[addr[0]] = talkToClient(conn,addr).start()
		serverChat(conn,addr,login).start()
		
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
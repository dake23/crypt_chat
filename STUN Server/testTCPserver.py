# -*- coding: utf-8 -*-
import json
import time
import random
import re
import socket
import threading
import sqlite3
import select
from Crypto.Cipher import AES
from Crypto import Random



#server address
_server_ip = "192.168.1.5"
#server port
_server_port = 5544
#address for bind port
_address_bind = _server_ip, _server_port
#buffer size
_recvbuffer = 1024
_maxconnect = 1024




'''
# --- Create tables ---

# create table users
cur.execute('CREATE TABLE IF NOT EXISTS USERS (ID INT PRIMARY KEY NOT NULL, LOGIN CHAR(32), USERNAME CHAR(90), REGISTER BOOLEAN NOT NULL, USER_A_KEY CHAR(254))')
# create table active_code
cur.execute('CREATE TABLE IF NOT EXISTS ACTIVE_CODE (CODE CHAR(254), ID_USER INT, USE_F BOOLEAN NOT NULL, FOREIGN KEY(ID_USER) REFERENCES USERS(ID))')
# create table activity
cur.execute('CREATE TABLE IF NOT EXISTS ACTIVITY (ID_ACT INT PRIMARY KEY NOT NULL, ID_USER INT, IP CHAR(32), LAST_ACT DATETIME, FOREIGN KEY(ID_USER) REFERENCES USERS(ID))')
# ---------------------
'''


# thread for work with clients connection

class talkToClient(threading.Thread):
	def __init__(self,clientSock, addr):
		self.sock = clientSock
		self.addr = addr
		self.running = 1
		self.login = ""
		self.iv = ""
		self.key = ""
		threading.Thread.__init__(self)
		
	def run(self):
	
		global K,K1
		#connection on database
		connDB = sqlite3.connect('serverDB.db')
		#create cursor
		cur = connDB.cursor()
		
		
#--------------- start auth client -----
		
#--------step 1 - get from client your username
		response = self.sock.recv(_recvbuffer).decode('utf-8')
		
		if 'LOGIN' in response:
			_res_mas = response.split(' ')
			
			self.login = _res_mas[1]
			
			thread_array[self.login] = self
			print('Client ', _res_mas[1] , ' want auth in system')
			
		else: self.kill()
		
		#get key from DB
		cur.execute('select key from users where login == ?',(self.login,))
		resp_db = cur.fetchone()
		if resp_db == None:
			print('Error: Not find user ',self.login)
			self.kill()
		else:
			self.key = resp_db[0]
			#print(key)		#ПОТОМ УБРАТЬ !!!!!
			self.key += self.key
		
		
#--------step 2 - generate rB and send servename;rB
		rB = int(random.uniform(222222,99999999))
		servername = 'pestserver'
		
		self.sock.send(';'.join([servername,str(rB)]).encode('utf-8'))
		
#--------step 3 - get IV from client and get cipher string servername_rB_rA
		
		self.iv = self.sock.recv(_recvbuffer)
		response = self.sock.recv(_recvbuffer)
		_servn,_rB,rA = decrypt(response,self.iv,self.key).decode('utf-8').split('_')
		print("sn = ",_servn,'\n_rB = ',_rB,'\nrB = ',rB,'\nrA = ',rA)
		
	
#--------step 4 - if auth success send cipher string username_rA
		if int(_rB) == int(rB):
			print('Client ',self.login, ' auth success')
			plain_text = self.login+"_"+rA
			cipher_text = encrypt(plain_text,self.iv,self.key)
			self.sock.send(cipher_text)
		else: 
			print('Client ',self.login,'not auth')
			self.kill()
		
#---------END AUTH ------------
			
		self.send("KEYS:"+str(K)+":"+str(K1))
		
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
		'''
			COMMAND FROM CLIENT and ACTION on this command:
				COMMAND LIST:
					desription: get list ip users
					action: send list ip users
				COMMAND CREATE [[ID_client] [IP:PORT]]:
					ID_client - ID client with whom want to start session
					IP:PORT - Client's IP who wants to start the session
					desription: start session with client IP
					action: send message client with IP, about other client want start session 
				COMMAND BYE:
					desription: close connection
					action: close connection
		'''
		
		global thread_array
		
		
		if 'LOGIN' in _response:
			_res_mas = _response.split(' ')
			
			self.login = _res_mas[1]
			
			thread_array[self.login] = self
			print('Client ', _res_mas[1] , ' registration on system')
			
		
		elif 'LIST' in _response:
			print("Client ", self.addr[0], _response)
			#get ip-list
			list_user = list(thread_array.keys())
			#remove yourself ip
			#list_user.remove(self.addr[0])
			#create request string "xx.xx.xx.xx;xx.xx.xx.xx"
			list_user = str(';'.join(list_user))
			self.send('LIST '+list_user)
			
		
		elif 'CREATE'  in _response:
			print("Client ", self.addr[0], _response)
			# get ip clients
			command,login_c,_address_connClient = _response.split(' ')	#from command string CREATE IP IP:PORT
			
			#get self thread clients
			client_thread = thread_array[login_c]
			req_string = "SESSION "+login_c+' '+str(_address_connClient)
			# send to client about other client want start session
			client_thread.send(req_string)
		elif 'BYE' in _response:
			print("Client ", self.addr[0], _response)
			#delete client out thread_list
			thread_array.pop(self.login)
			self.kill()
	
	def send(self,_request):
		self.sock.send(encrypt(_request,self.iv,self.key))#.encode('utf-8'))
		print('Send to ',self.login, _request)
		
	def kill(self):
		self.running = 0

		
		
class Text_Input(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.running = 1
	def run(self):
		while self.running == True:
			text = input('INPUT COMMAND: ')
			if 'exit' in text or 'Exit' in text:
				self.kill()
			
	
			
			time.sleep(1)
		'''	
class sendToClient(threading.Thread):
	def __init__(self,clientSock, addr):
		self.sock = clientSock
		self.addr = addr
		self.running = 1
		threading.Thread.__init__(self)
		
	def run(self):
'''		
global thread_array
global MODE
global K
global K1

K = int(random.uniform(10000000,90000000))
K1 = int(random.uniform(10000000,90000000))

MODE = AES.MODE_CFB
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
	
def main():
	
	global thread_array
	
	
	#create socket for listener
	sock = socket.socket()
	sock.bind(_address_bind)
	sock.listen(_maxconnect)
	print('SERVER LISTEN on ',_address_bind )
	# for first start
	count_thread = 1
	#dictonary threads -> ip:thread
	thread_array = {}
	
	while count_thread >= 1:
		
		# create new connection
		conn, addr = sock.accept()
		print(":NEW CONNECTION IP ", str(addr))
		
		
		#thread_array[addr[0]] = talkToClient(conn,addr).start()
		talkToClient(conn,addr).start()
		
		#get current count threads
		count_thread = threading.active_count()
		
		
	
	
	
	'''
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
	'''

	
	
# START	
main()
input()
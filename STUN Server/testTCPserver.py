# -*- coding: utf-8 -*-
import json
import time
import random
import re
import socket
import threading
import sqlite3
import select

#server address
_server_ip = "10.0.0.108"
#server port
_server_port = 5544
#address for bind port
_address_bind = _server_ip, _server_port
#buffer size
_recvbuffer = 1024
_maxconnect = 1024


'''
# Set DB options and create tables
#connection on database
connDB = sqlite3.connect('chatDB')
#create cursor
cur = connDB.cursor()

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
		threading.Thread.__init__(self)
		
	def run(self):
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
		'''
			COMMAND FROM CLIENT and ACTION on this command:
				COMMAND LIST:
					desription: get list ip users
					action: send list ip users
				COMMAND CREATE [[IP] [IP:PORT]]:
					IP - IP client with whom want to start session
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
		self.sock.send(_request.encode('utf-8'))
		print('Send to ',self.login, _request)
		
	def kill(self):
		self.running = 0

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
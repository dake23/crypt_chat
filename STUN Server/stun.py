# -*- coding: utf-8 -*-
import json
import time
import random
import re
import socket
import threading
import sqlite3


#server address
_server_ip = "192.168.1.9"
#server port
_server_port = 5544
#address for bind port
_address_bind = _server_ip, _server_port
#buffer size
_recvbuffer = 1024


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



# thread for work with clients connection
class talkToClient(threading.Thread):
	def __init__(self,clientSock, addr,mode):
		self.clientSock = clientSock
		self.addr = addr
		self.mode = mode
		threading.Thread.__init__(self)
		
	def run(self):
		

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
	

	
	
# START	
main()
input()
# -*- encoding: utf-8 -*-
from gevent.socket import socket
from gevent.ssl import SSLSocket

import gevent.monkey
import gevent
import time
import base64
from flask import request, make_response
from parser import parser
from webservice import app
from pymongo import Connection
from bson.objectid import ObjectId
import sss_crawler
class IRC:
	def __init__(self):
		self.recvdata = ''
		pass
	def init(self):
		self.sslconn = SSLSocket(socket())
		self.sslconn.connect(('127.0.0.1',16667))
		self.on_connect()
		self.spawn_send_recv_loop()

	def on_connect(self):
		self.sslconn.send('USER efgd efgd efgd :efgd\r\n')
		self.sslconn.send('NICK efgd\r\n')

	def spawn_send_recv_loop(self):
		gevent.spawn(self.send_recv_loop)

	def send_recv_loop(self):
		while True:
			recvdata = self.sslconn.recv(4086)
			if type(recvdata) == type(int) and recvdata <= 0:
				# 소켓 error or disconnect
				self.init()
				break
			self.recvdata += recvdata
			self.recvdata = self.recvdata.replace('\r','')
			while True:			
				nextpos = self.recvdata.find('\n')
				if nextpos == -1:
					break
				parseinfo = parser.parser(self.recvdata[:nextpos])
				try:
					func = getattr(IRC, 'on_' + parseinfo.get_command().lower())
					func(self,*parseinfo.get_all())
				except:
					pass
				print parseinfo.get_all()
				self.recvdata = self.recvdata[nextpos+1:]

	def on_ping(self, message):
		self.sslconn.send('PONG :' + message + '\r\n')


	def on_001(self, message_from, message_to, message):
		self.sslconn.send('JOIN #efgd\r\n')
		gevent.spawn(sss_crawler.init_crawler)
		
	

irc = IRC()

if __name__ == '__main__':
	gevent.monkey.patch_all()

#	sslconn = SSLSocket(socket())
#	sslconn.connect(('127.0.0.1',8080))
#	sslconn.send('user abcd abcd abcd :abcd\r\nNICK efgd\r\n')
#	while True:
#		print sslconn.recv(4086)

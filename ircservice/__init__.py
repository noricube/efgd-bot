from client import irc

def send_irc_message(msg):
	print msg
	sendmsg = u'PRIVMSG #efgd :' + msg + u'\r\n'
	irc.sslconn.send(sendmsg.encode('utf-8'))

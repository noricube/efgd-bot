import gevent.monkey
from gevent.wsgi import WSGIServer
from gevent.backdoor import BackdoorServer
from webservice import app
from ircservice import irc

gevent.monkey.patch_all()

backdoor = BackdoorServer(('127.0.0.1',18080))
backdoor.start()

irc.init()

http_server = WSGIServer(('', 8000), app)
http_server.serve_forever()

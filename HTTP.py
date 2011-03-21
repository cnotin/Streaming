# -*- coding: utf-8 -*-


from TCPPull import TCPPullControlFactory
from catalogue import Catalogue
from streaming import SEP
from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor


class ServeurHttp(LineReceiver):
	def __init__(self):
		self.delimiter = "\n"
	def __del__(self):
		pass

	def addHeader(self, msg):
		header = "HTTP/1.1 200 OK" + SEP + "Server: localhost" + SEP + "Connection: Keep-Alive" + SEP + "Content-Type: text/txt" + SEP + "Content-Length: "
		header += str(len(msg))
		msg = header + SEP + SEP + msg
		return msg

	def lineReceived(self, line):
		print "HTTP = " + line
		#on a un GET mais pas pour le catalogue => dégage
		if (line.find("GET") != -1):
			self.transport.write(self.addHeader(self.factory.cat.getCatalogue()))

	def connectionMade(self):
		print "client connecté"



class ServeurHTTPFactory(Factory):
	protocol = ServeurHttp

	def __init__(self):
		self.cat = Catalogue("catalogue.txt")
		for objet in self.cat.objects:
			if objet[5] == "TCP_PULL":
				reactor.listenTCP(objet[4], TCPPullControlFactory(objet[1]))
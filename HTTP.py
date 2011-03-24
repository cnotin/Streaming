# -*- coding: utf-8 -*-


from TCPPull import TCPPullControlFactory
from TCPPush import TCPPushControlFactory
from UDPPull import UDPPullControl
from catalogue import Catalogue
from streaming import SEP
from twisted.internet import reactor
from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver


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
		if (line.find("GET") != -1):
			self.transport.write(self.addHeader(self.factory.cat.getCatalogue()))

	def connectionMade(self):
		print "client connecté"



class ServeurHTTPFactory(Factory):
	protocol = ServeurHttp

	def __init__(self, ip):
		self.cat = Catalogue("catalogue.txt", ip)
		for objet in self.cat.objects:
			if objet[5] == "TCP_PULL":
				reactor.listenTCP(objet[4], TCPPullControlFactory(objet[1]))
			if objet[5] == "TCP_PUSH":
				reactor.listenTCP(objet[4], TCPPushControlFactory(objet[1], objet[6]))
			elif objet[5] == "UDP_PULL":
				reactor.listenUDP(objet[4], UDPPullControl(objet[1]))
			

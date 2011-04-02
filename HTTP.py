# -*- coding: utf-8 -*-


from TCPPull import TCPPullControlFactory
from TCPPush import TCPPushControlFactory
from UDPPull import UDPPullControl
from UDPPush import UDPPushControl
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
		print "[HTTP] reçu = " + line
		if (line.find("GET") != -1):
			self.transport.write(self.addHeader(self.factory.cat.getCatalogue()))

	def connectionMade(self):
		print "[HTTP] client connecté"


class ServeurHTTPFactory(Factory):
	"""
	Factory qui va créer des instances (une seule ici) d'un serveur HTTP minimaliste,
	la Factory sert à rassembler le code et les attributs qui sont communs entre les différentes instances.
	Comme par ex le catalogue.
	"""
	
	# ServeurHTTP : classe à partir de laquelle la Factory va créer les instances
	protocol = ServeurHttp

	def __init__(self, catalogue):
		self.cat = catalogue
		
		# pour chaque vidéo du catalogue, on regarde son protocole et on crée un objet qui correspond
		for objet in self.cat.objects:
			if objet[5] == "TCP_PULL":
				reactor.listenTCP(objet[4], TCPPullControlFactory(objet[1]))
			elif objet[5] == "TCP_PUSH":
				#pour mémoire : objet[6] = ips de la vidéo
				# le push a besoin de connaître ça pour savoir à quelle fréquence il doit pusher
				reactor.listenTCP(objet[4], TCPPushControlFactory(objet[1], objet[6]))
			elif objet[5] == "UDP_PULL":
				reactor.listenUDP(objet[4], UDPPullControl(objet[1]))
			elif objet[5] == "UDP_PUSH":
				#pour mémoire : objet[6] = ips de la vidéo
				# le push a besoin de connaître ça pour savoir à quelle fréquence il doit pusher
				reactor.listenUDP(objet[4], UDPPushControl(objet[1], objet[6]))

		print "Catalogue chargé, le serveur est prêt :)\n"

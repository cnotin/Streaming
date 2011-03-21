# -*- coding: utf-8 -*-

from catalogue import Catalogue
import glob
from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ClientEndpoint
from twisted.internet.protocol import Factory
from twisted.internet.protocol import Protocol
from twisted.protocols.basic import LineReceiver

PRON = "pr0n\\"
SEP = "\r\n"

def gotProtocol(p, tcpPullControl):
	tcpPullControl.clientProtocol = p


class TCPPullData(Protocol):
	def __init__(self):
		print "constructeur TCPPullDataProtocol"
		self.image_id = 1

	def __del__(self):
		print "Fermeture connexion données"

	
	def sendCurrentImage(self, images):
		if self.image_id == len(images):
			self.image_id = 1
		#print "j'envoie l'image %s" % self.image_id
		self.transport.write("%s%s%s%s%s" % (self.image_id, SEP, len(images[self.image_id]), SEP,  images[self.image_id]))
		self.image_id += 1


class TCPPullControl(LineReceiver):
	def __init__(self):
		self.clientProtocol = None

	def __del__(self):
		print "Fermeture connexion contrôle"

	def lineReceived(self, line):
		#print "TCP PULL = " + line
		if (line.find("GET -1") == 0):
			if self.clientProtocol:
				self.clientProtocol.sendCurrentImage(self.factory.images)
		elif (line.find("LISTEN_PORT") == 0):
			point = TCP4ClientEndpoint(reactor, self.transport.getPeer().host, int(line.split(" ")[1]))
			d = point.connect(self.factory.tcpPullDataFactory)
			d.addCallback(gotProtocol, self)
		

	def connectionMade(self):
		print "TCP PULL contrôle connecté !"


class TCPPullControlFactory(Factory):
	protocol = TCPPullControl
	tcpPullDataFactory = None

	def __init__(self, movie):
		self.tcpPullDataFactory = Factory()
		self.tcpPullDataFactory.protocol = TCPPullData

		self.images = []
		self.images.append("") #car ceci commence à 0 et la première image a l'index 1

		imagesPath = PRON + movie + "\\"
		if movie == "tophat":
			countImages = 99
		else:
			countImages = len(glob.glob1(imagesPath,"*.jpg"))
		for i in range(1, countImages + 1):
			#print "image %s" % i
			f = open(imagesPath + str(i) + ".jpg", "rb")
			self.images.append(f.read())
			f.close()
		print "a chargé %d images pour %s" % (countImages, movie)



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


def main():
	print "Welcome"
	reactor.listenTCP(4590, ServeurHTTPFactory())
	reactor.run()

if __name__ == '__main__':
	main()

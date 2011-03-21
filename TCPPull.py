# -*- coding: utf-8 -*-

import glob
from streaming import PRON
from streaming import SEP
from twisted.internet.endpoints import TCP4ClientEndpoint
from twisted.internet.protocol import Factory
from twisted.internet.protocol import Protocol
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor


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
		# Tenative d'optimisation :
		#sender = FileSender()
		#output = StringIO.StringIO("%s%s%s%s%s" % (self.image_id, SEP, len(images[self.image_id]), SEP,  images[self.image_id]))
		#sender.beginFileTransfer(output, self.transport, None)

		self.transport.write(images[self.image_id])
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
		elif (line.find("END") == 0):
			self.transport.loseConnection()


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
			imageData = f.read()
			self.images.append("%s%s%s%s%s" % (i, SEP, len(imageData), SEP,  imageData))
			f.close()
		print "a chargé %d images pour %s" % (countImages, movie)



if __name__ == "__main__":
    print "Hello World"

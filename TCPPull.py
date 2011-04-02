# -*- coding: utf-8 -*-

import glob
import os
from streaming import VIDEOTHEQUE
from streaming import SEP
from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ClientEndpoint
from twisted.internet.protocol import Factory
from twisted.internet.protocol import Protocol
from twisted.protocols.basic import LineReceiver


class TCPPullData(Protocol):
	def __init__(self):
		print "[TCP Pull] construction du canal de données"
		self.image_id = 1

	def __del__(self):
		print "[TCP Pull] Fermeture canal de données"

	def sendCurrentImage(self, images):
		if self.image_id == len(images):
			self.image_id = 1

		self.transport.write(images[self.image_id])
		self.image_id += 1


def gotProtocol(p, tcpPullControl):
	tcpPullControl.clientProtocol = p
	
class TCPPullControl(LineReceiver):
	def __init__(self):
		print "[TCP Pull] Création du canal de contrôle"
		self.clientProtocol = None

	def __del__(self):
		print "[TCP Pull] Fermeture du canal de contrôle"

	def lineReceived(self, line):
		if (line.find("GET -1") == 0):
			if self.clientProtocol:
				self.clientProtocol.sendCurrentImage(self.factory.images)
			else:
				reactor.callLater(0, self.lineReceived, line)
				
		elif (line.find("LISTEN_PORT") == 0):
			print "[TCP Pull] reçu = " + line

			point = TCP4ClientEndpoint(reactor, self.transport.getPeer().host, int(line.split(" ")[1]))
			d = point.connect(self.factory.tcpPullDataFactory)
			d.addCallback(gotProtocol, self)
			
		elif (line.find("END") == 0):
			print "[TCP Pull] reçu = " + line
			
			self.transport.loseConnection()


	def connectionMade(self):
		print "[TCP Pull] Canal de contrôle connecté !"


class TCPPullControlFactory(Factory):
	protocol = TCPPullControl
	tcpPullDataFactory = None

	def __init__(self, movie):
		self.tcpPullDataFactory = Factory()
		self.tcpPullDataFactory.protocol = TCPPullData

		self.images = []
		self.images.append("") #car ceci commence à 0 et la première image a l'index 1

		imagesPath = os.path.join(VIDEOTHEQUE, movie)
		countImages = len(glob.glob1(imagesPath,"*.jpg"))
		
		for i in range(1, countImages + 1):
			f = open(os.path.join(imagesPath, str(i) + ".jpg"), "rb")
			imageData = f.read()
			self.images.append("%s%s%s%s%s" % (i, SEP, len(imageData), SEP,  imageData))
			f.close()
		print "a chargé %d images pour %s" % (countImages, movie)

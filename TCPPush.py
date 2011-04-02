# -*- coding: utf-8 -*-

import glob
import os
from streaming import VIDEOTHEQUE
from streaming import SEP
from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ClientEndpoint
from twisted.internet.protocol import Factory
from twisted.internet.protocol import Protocol
from twisted.internet.task import LoopingCall
from twisted.protocols.basic import LineReceiver


def gotProtocol(p, tcpPushControl):
	tcpPushControl.clientProtocol = p

class TCPPushData(Protocol):
	def __init__(self):
		print "[TCP Push] Construction du canal de données"
		self.image_id = 1

	def __del__(self):
		self.transport.loseConnection()
		print "[TCP Push] Fermeture du canal de données"


	def sendCurrentImage(self, images):
		if self.image_id == len(images):
			self.image_id = 1

		self.transport.write(images[self.image_id])
		self.image_id += 1


class TCPPushControl(LineReceiver):
	def __init__(self):
		print "[TCP Push] Création du canal de contrôle"
		self.clientProtocol = None
		self.lc = None

	def __del__(self):
		print "[TCP Push] Fermeture du canal de contrôle"

	def lineReceived(self, line):
		print "[TCP Push] reçu = " + line
		if (line.find("START") == 0):
			if self.clientProtocol:
				self.isSending = True
				if not self.lc:
					self.lc = LoopingCall(self.clientProtocol.sendCurrentImage, self.factory.images)
				self.lc.start(1./self.factory.fps)
			else:
				reactor.callLater(0, self.lineReceived, line)

		elif (line.find("PAUSE") == 0):
			self.isSending = False
			self.lc.stop()

		elif (line.find("LISTEN_PORT") == 0):
			point = TCP4ClientEndpoint(reactor, self.transport.getPeer().host, int(line.split(" ")[1]))
			d = point.connect(self.factory.tcpPushDataFactory)
			d.addCallback(gotProtocol, self)

		elif (line.find("END") == 0):
			self.transport.loseConnection()
			if self.isSending:
				self.lc.stop()
			del self.clientProtocol

	def connectionMade(self):
		print "[TCP Push] Canal de contrôle connecté !"


class TCPPushControlFactory(Factory):
	protocol = TCPPushControl
	tcpPushDataFactory = None

	def __init__(self, movie, fps):
		self.tcpPushDataFactory = Factory()
		self.tcpPushDataFactory.protocol = TCPPushData
		self.fps = fps

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

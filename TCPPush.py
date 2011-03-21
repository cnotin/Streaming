# -*- coding: utf-8 -*-

import glob
from streaming import PRON
from streaming import SEP
from twisted.internet.endpoints import TCP4ClientEndpoint
from twisted.internet.protocol import Factory
from twisted.internet.protocol import Protocol
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor


def gotProtocol(p, tcpPushControl, fps):
	tcpPushControl.clientProtocol = p
	p.pauseTime = 1./fps

class TCPPushData(Protocol):
	def __init__(self):
		print "constructeur TCPPushDataProtocol"
		self.image_id = 1
		self.isSending = False

	def __del__(self):
		self.transport.loseConnection()
		print "Fermeture connexion données"


	def sendCurrentImage(self, images):
		if self.isSending :
			if self.image_id == len(images):
				self.image_id = 1
			print "j'envoie l'image %s" % self.image_id
			# Tenative d'optimisation :
			#sender = FileSender()
			#output = StringIO.StringIO("%s%s%s%s%s" % (self.image_id, SEP, len(images[self.image_id]), SEP,  images[self.image_id]))
			#sender.beginFileTransfer(output, self.transport, None)

			self.transport.write(images[self.image_id])
			self.image_id += 1
			reactor.callLater(self.pauseTime, self.sendCurrentImage, images)


class TCPPushControl(LineReceiver):
	def __init__(self):
		self.clientProtocol = None

	def __del__(self):
		print "Fermeture connexion contrôle"

	def lineReceived(self, line):
		print "TCP PUSH = " + line
		if (line.find("START") == 0):
			if self.clientProtocol:
				self.clientProtocol.isSending = True
				self.clientProtocol.sendCurrentImage(self.factory.images)
			else:
				#print "tcp push appel moi plus tard"
				reactor.callLater(0, self.lineReceived, line)

		elif (line.find("PAUSE") == 0):
			self.clientProtocol.isSending = False

		elif (line.find("LISTEN_PORT") == 0):
			point = TCP4ClientEndpoint(reactor, self.transport.getPeer().host, int(line.split(" ")[1]))
			d = point.connect(self.factory.tcpPushDataFactory)
			d.addCallback(gotProtocol, self, self.factory.fps)

		elif (line.find("END") == 0):
			self.transport.loseConnection()
			self.clientProtocol.isSending = False
			del self.clientProtocol

	def connectionMade(self):
		print "TCP PUSH contrôle connecté !"


class TCPPushControlFactory(Factory):
	protocol = TCPPushControl
	tcpPushDataFactory = None

	def __init__(self, movie, fps):
		self.tcpPushDataFactory = Factory()
		self.tcpPushDataFactory.protocol = TCPPushData
		self.fps = fps

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

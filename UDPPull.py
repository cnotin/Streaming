# -*- coding: utf-8 -*-

import glob
import os
from streaming import PRON
from streaming import SEP
from twisted.internet import reactor
from twisted.internet.protocol import DatagramProtocol
import socket

class UDPPullControl(DatagramProtocol):
	def __init__(self, movie):
		self.images = []
		self.images.append("") #car ceci commence à 0 et la première image a l'index 1
		self.clients = {}
		imagesPath = os.path.join(PRON, movie)
		if movie == "tophat":
			countImages = 99
		else:
			countImages = len(glob.glob1(imagesPath,"*.jpg"))
		for i in range(1, countImages + 1):
			#print "image %s" % i
			f = open(os.path.join(imagesPath, str(i) + ".jpg"), "rb")
			self.images.append(f.read())
			f.close()
		print "a chargé %d images pour %s" % (countImages, movie)

	def __del__(self):
		print "Fermeture connexion contrôle"
		
	def sendCurrentImage(self, host, port, image, fragmentNum = 0, a = 0):
		#print "envoi image %s %s" % (image, fragmentNum)
		client = self.clients[host+":%s" % port]

		tailleImage = len(self.images[image])
		fragmentPos = fragmentNum * client["fragmentSize"]
		
		if fragmentPos + client["fragmentSize"] > tailleImage:
			finImage = True
			tailleFragment = tailleImage - fragmentPos
		else:
			finImage = False
			tailleFragment = client["fragmentSize"]


		message = "%s%s%s%s%s%s%s%s%s" % (image, SEP, tailleImage,\
		SEP, fragmentPos, SEP, tailleFragment, SEP, self.images[image][fragmentPos:fragmentPos + tailleFragment])

		try:
			self.transport.write(message, (host, client["port"]))
		except:
			print "Buffer d'envoi UDP rempli, baisser la qualité des images et/ou la fréquence"
			a += 1
		else:
			fragmentNum += 1

		if not finImage and a < 1:
			reactor.callLater(0, self.sendCurrentImage, host, port, image, fragmentNum, a)
	

	def datagramReceived(self, data, (host, port)):
		if not host+":%s" % port in self.clients:
			self.clients[host+":%s" % port]= {}
			client = self.clients[host+":%s" % port]
			client["imagecourante"] = 1
			client["packagecourant"] = 0
		else:
			client = self.clients[host+":%s" % port]		
		listedonnes = data.split(SEP)
			
		for line in listedonnes:		
			if (line.find("GET -1") == 0):
				#print "send"

				self.sendCurrentImage(host, port, client["imagecourante"])

				if client["imagecourante"] == len(self.images) - 1:
					client["imagecourante"] = 1
				else:
					client["imagecourante"] += 1
				
			elif (line.find("LISTEN_PORT") == 0):
				client["port"] = int(line.split(" ")[1])
				#print "port"
			elif (line.find("FRAGMENT_SIZE") == 0):
				client["fragmentSize"]= int(line.split(" ")[1])
				self.transport.getHandle().setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 20000000)
				#print "image"
			elif (line.find("END") == 0):
				del client
				#self.transport.connect(host,int(line.split(" ")[1])
				#point = UDP4ClientEndpoint(reactor, self.transport.getPeer().host, int(line.split(" ")[1]))
				#d = point.connect(self.factory.UDPPullDataFactory)
				#d.addCallback(gotProtocol, self)


	def connectionMade(self):
		print "UDP PULL contrôle connecté !"


if __name__ == "__main__":
    print "Hello World"

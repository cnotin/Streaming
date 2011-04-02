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
		print "[UDP Pull] Création du canal de contrôle"
		self.images = []
		self.images.append("") #car ceci commence à 0 et la première image a l'index 1
		self.clients = {}
		imagesPath = os.path.join(PRON, movie)
		countImages = len(glob.glob1(imagesPath,"*.jpg"))
		
		for i in range(1, countImages + 1):
			f = open(os.path.join(imagesPath, str(i) + ".jpg"), "rb")
			self.images.append(f.read())
			f.close()
		print "a chargé %d images pour %s" % (countImages, movie)

	def __del__(self):
		print "[UDP Pull] Fermeture du canal contrôle"
		
	def sendCurrentImage(self, host, port, image, fragmentNum = 0, tryNum = 0):
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
		except socket.error:
			print "Buffer d'envoi UDP rempli, baisser la qualité des images et/ou la fréquence"
			tryNum += 1
		else:
			fragmentNum += 1

		if not finImage and tryNum < 2:
			reactor.callLater(0, self.sendCurrentImage, host, port, image, fragmentNum, tryNum)
	

	def datagramReceived(self, data, (host, port)):		
		if not host+":%s" % port in self.clients:
			self.clients[host+":%s" % port]= {}
			client = self.clients[host+":%s" % port]
			client["imagecourante"] = 1
		else:
			client = self.clients[host+":%s" % port]		
		listedonnes = data.split(SEP)
			
		for line in listedonnes:
			if (line.find("GET -1") == 0):
				self.sendCurrentImage(host, port, client["imagecourante"])

				if client["imagecourante"] == len(self.images) - 1:
					client["imagecourante"] = 1
				else:
					client["imagecourante"] += 1
				
			elif (line.find("LISTEN_PORT") == 0):
				print "[UDP Pull] reçu = " + str(data)
				client["port"] = int(line.split(" ")[1])

			elif (line.find("FRAGMENT_SIZE") == 0):
				print "[UDP Pull] reçu = " + str(data)
				client["fragmentSize"]= int(0.8*int(line.split(" ")[1]))
				self.transport.getHandle().setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, client["fragmentSize"] * 200)

			elif (line.find("END") == 0):
				print "[UDP Pull] reçu = " + str(data)
				del self.clients[host+":%s" % port]


	def connectionMade(self):
		print "[UDP Pull] Canal de contrôle connecté !"

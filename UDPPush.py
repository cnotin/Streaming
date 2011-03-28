# -*- coding: utf-8 -*-

import exceptions
import glob
import os
import socket
from streaming import PRON
from streaming import SEP
from twisted.internet import reactor
from twisted.internet.protocol import DatagramProtocol
from twisted.internet.task import LoopingCall

class UDPPushControl(DatagramProtocol):
	def __init__(self, movie, fps):
		self.fps = fps
		
		self.images = []
		self.images.append("") #car ceci commence à 0 et la première image a l'index 1
		self.clients = {}
		imagesPath = os.path.join(PRON, movie)
		if movie == "tophat":
			countImages = len(glob.glob1(imagesPath,"*.jpg"))#99
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
		try:
			client = self.clients[host+":%s" % port]
		except exceptions.KeyError:
			pass
		else:
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

	def sendImages(self, host, port, client):
		print "envoi images %d " % client["imagecourante"]
		if client["imagecourante"] == len(self.images) - 1:
			client["imagecourante"] = 1
		else:
			client["imagecourante"] += 1

		self.sendCurrentImage(host, port, client["imagecourante"])


	def clientTimeout(self, client, host, port):
		client["sendingDeferred"].stop()
		del self.clients[host+":%s" % port]

	def datagramReceived(self, data, (host, port)):
		#print "data = %s" % data
		if not host+":%s" % port in self.clients:
			self.clients[host+":%s" % port]= {}
			client = self.clients[host+":%s" % port]
			client["imagecourante"] = 1
			#client["receiveBuffer"] = []
			client["fragmentSize"] = 0
			client["port"] = 0
			client["aliveDeferred"] = None
			client["sendingDeferred"] = None

		else:
			client = self.clients[host+":%s" % port]

		#client["receiveBuffer"] = data.split(SEP)

		for line in data.split(SEP):
			if (line.find("START") == 0):

				#if client["fragmentSize"] != 0 and client["port"] != 0:
				if not client["sendingDeferred"]:
					client["sendingDeferred"] = LoopingCall(self.sendImages, host, port, client)
				client["sendingDeferred"].start(1./self.fps, now=True)

				if not client["aliveDeferred"]:
					client["aliveDeferred"] = reactor.callLater(60, self.clientTimeout, client, host, port)

			elif (line.find("PAUSE") == 0):
				client["sendingDeferred"].stop()

			elif (line.find("LISTEN_PORT") == 0):
				if client["port"] == 0:
					client["port"] = int(line.split(" ")[1])

			elif (line.find("FRAGMENT_SIZE") == 0):
				client["fragmentSize"] = int(line.split(" ")[1])
				self.transport.getHandle().setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, client["fragmentSize"] * 80000)

			elif (line.find("END") == 0):
				client["sendingDeferred"].stop()
				del self.clients[host+":%s" % port]

			elif (line.find("ALIVE") == 0):
				client["aliveDeferred"].reset(60)
				print "alive"


	def connectionMade(self):
		print "UDP PUSH contrôle connecté !"


if __name__ == "__main__":
    print "Hello World"

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
		
	def sendCurrentImage(self, host, port):
		client=self.clients[host+":%s" % port]
		i=client["packagecourant"]
		if client["imagecourante"] == len(self.images):
			client["imagecourante"] = 1
		nbfragments=len(self.images[client["imagecourante"]])/client["fragmentSize"]
		reste=len(self.images[client["imagecourante"]]) % client["fragmentSize"]
		if reste == 0:
			reste=-1
		else:
			reste=0
		
		messageImage = self.images[client["imagecourante"]][i*client["fragmentSize"]:(1+i)*client["fragmentSize"]]
		fragmentImage = "%s%s%s%s%s%s%s%s" % (client["imagecourante"],SEP,\
										str(len(self.images[client["imagecourante"]])),\
										 SEP,str(i*client["fragmentSize"]), SEP, str(len(messageImage)),SEP)
		#print i
		fragmentImage += "%s" % messageImage
		
		try:
			self.transport.write(fragmentImage, (host, client["port"]))
			
		except socket.error:
			reactor.callLater(0, self.sendCurrentImage, host, port)
			
		else:	
			client["packagecourant"] +=1
			
			if(i==nbfragments+reste):		
				client["imagecourante"] += 1
				client["packagecourant"]= 0
			else:
				reactor.callLater(0, self.sendCurrentImage, host, port)
	

	def datagramReceived(self, data, (host, port)):
		if not host+":%s" % port in self.clients:
			self.clients[host+":%s" % port]= {}
		#print data
		listedonnes = data.split(SEP)
		for line in listedonnes:		
			if (line.find("GET -1") == 0):
				#print "send"
				self.sendCurrentImage(host,port)
				
			elif (line.find("LISTEN_PORT") == 0):
				self.clients[host+":%s" % port]["port"] = int(line.split(" ")[1])
				#print "port"
			elif (line.find("FRAGMENT_SIZE") == 0):
				self.clients[host+":%s" % port]["fragmentSize"]= int(line.split(" ")[1])
				self.clients[host+":%s" % port]["imagecourante"]= 1
				self.clients[host+":%s" % port]["packagecourant"]=0
				#print "image"
			elif (line.find("END") == 0):
				del self.clients[host+":%s" % port]
				#self.transport.connect(host,int(line.split(" ")[1])
				#point = UDP4ClientEndpoint(reactor, self.transport.getPeer().host, int(line.split(" ")[1]))
				#d = point.connect(self.factory.UDPPullDataFactory)
				#d.addCallback(gotProtocol, self)


	def connectionMade(self):
		print "UDP PULL contrôle connecté !"


if __name__ == "__main__":
    print "Hello World"

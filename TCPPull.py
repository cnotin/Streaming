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
	"""
	Protocol qui gère le canal de données, càd qu'il ne fait qu'envoyer des images quand on lui dit.
	Il y aura un objet de cette classe par canal.
	"""
	def __init__(self):
		print "[TCP Pull] construction du canal de données"
		self.image_id = 1 # on commence à l'image 1

	def __del__(self):
		print "[TCP Pull] Fermeture canal de données"

	def sendCurrentImage(self, images):
		# on boucle une fois arrivé à la fin de la vidéo
		if self.image_id == len(images):
			self.image_id = 1

		self.transport.write(images[self.image_id])
		self.image_id += 1


def gotProtocol(p, tcpPullControl):
	"""
	Callback appelé quand la connexion a été établie, on veut donner au tcpPullControl du canal de contrôle,
	une référence vers le protocol qui gère le canal de données, pour pouvoir dans l'objet du canal de contrôle
	déclencher des méthodes de l'objet du canal de données.
	"""
	tcpPullControl.clientProtocol = p # p : TCPPullData, protocol du canal de données

class TCPPullControl(LineReceiver):
	"""
	Protocole créé à chaque instance de canal de contrôle.

	Quand on reçoit LISTEN_PORT, on va lancer la connexion vers le client. Cela peut être long et comme nous
	sommes dans un paradigme de programmation évènementielle c'est intolérable donc on dit au réacteur de se
	connecter et il nous rappellera quand cela sera fait. C'est pour cela que nous avons self.clientProtocol
	qui est initialisé à None puis renseigné une fois que le callback de connexion établie sera appelé.
	"""
	def __init__(self):
		print "[TCP Pull] Création du canal de contrôle"
		self.clientProtocol = None

	def __del__(self):
		print "[TCP Pull] Fermeture du canal de contrôle"

	def lineReceived(self, line):
		if (line.find("GET -1") == 0):
			if self.clientProtocol: # nous nous sommes connectés avec succès au client
				self.clientProtocol.sendCurrentImage(self.factory.images) # envoyer l'image en cours
			else: # la connexion vers le client n'a pas encore été établie, on enregistre ce "GET -1" et on le redéclenche
			# jusqu'à ce que la connexion ait bien été établie (comme ça on ne perd pas le message)
				reactor.callLater(0, self.lineReceived, line)

		elif (line.find("LISTEN_PORT") == 0):
			print "[TCP Pull] reçu = " + line

			# tentative de connexion au client
			point = TCP4ClientEndpoint(reactor, self.transport.getPeer().host, int(line.split(" ")[1]))
			d = point.connect(self.factory.tcpPullDataFactory) # Factory qui va créer un objet TCPPullData qui va gérer cette connexion
			# Quand la connexion s'est bien déroulée, appeler ce callback
			d.addCallback(gotProtocol, self)

		elif (line.find("END") == 0):
			print "[TCP Pull] reçu = " + line

			self.transport.loseConnection()
			del self.clientProtocol


	def connectionMade(self):
		print "[TCP Pull] Canal de contrôle connecté !"


class TCPPullControlFactory(Factory):
	"""
	Factory qui va créer un objet TCPPullControl par client qui se connecte au canal de contrôle d'une vidéo TCP Pull.
	La factory rassemble les attributs partagés par les différentes instances : les images de la vidéos.
	"""
	protocol = TCPPullControl
	tcpPullDataFactory = None # factory qui ca créer les canaux de données

	def __init__(self, movie):
		self.tcpPullDataFactory = Factory()
		self.tcpPullDataFactory.protocol = TCPPullData # la factory du canal de données crée un objet TCPPullData par vidéo visualisée

		self.images = []
		self.images.append("") #car un tableau commence à 0 et la première image à l'index 1

		imagesPath = os.path.join(VIDEOTHEQUE, movie)
		# compte toutes les images (*.jpg) présentes dans le répertoire, attention si un fichier .jpg qui ne fait pas partie de la vidéo
		# est présent il sera compté comme tel et posera problème
		countImages = len(glob.glob1(imagesPath,"*.jpg"))

		for i in range(1, countImages + 1):
			# charger 1.jpg, 2.jpg, 3.jpg etc...
			f = open(os.path.join(imagesPath, str(i) + ".jpg"), "rb")
			imageData = f.read()
			# les headers de chaque paquet, image par image, sont précalculés car ils ne changent pas à l'exécution
			self.images.append("%s%s%s%s%s" % (i, SEP, len(imageData), SEP,  imageData))
			f.close()
		print "a chargé %d images pour %s" % (countImages, movie)

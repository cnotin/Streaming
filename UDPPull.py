# -*- coding: utf-8 -*-

import glob
import os
from streaming import VIDEOTHEQUE
from streaming import SEP
from twisted.internet import reactor
from twisted.internet.protocol import DatagramProtocol
import socket

class UDPPull(DatagramProtocol):
	"""
	Protocol créé 1 fois par vidéo qui va recevoir les requêtes des clients et leur envoyer les vidéos. En pull c'est le client qui demande
	chaque image de la vidéo 1 par 1, s'il ne demande rien on n'envoie rien.
	"""
	def __init__(self, movie):
		print "[UDP Pull] Création du canal"
		
		# ce dictionnaire sert à mémoriser les informations de chaque client, contrairement à TCP où l'on utilise un mode connecté et donc un objet
		# par client, ici il n'y a qu'un objet pour tous les clients et il doit donc jongler pour savoir si c'est un client qu'il a déjà vu ou pas
		# les clés du dictionnaire sont au format texte "ip_client:port_source"
		self.clients = {}
		
		self.images = []
		self.images.append("") #car ceci commence à 0 et la première image à l'index 1
		imagesPath = os.path.join(VIDEOTHEQUE, movie)
		# compte toutes les images (*.jpg) présentes dans le répertoire, attention si un fichier .jpg qui ne fait pas partie de la vidéo
		# est présent il sera compté comme tel et posera problème
		countImages = len(glob.glob1(imagesPath,"*.jpg"))
		
		for i in range(1, countImages + 1):
		# charger 1.jpg, 2.jpg, 3.jpg etc...
			f = open(os.path.join(imagesPath, str(i) + ".jpg"), "rb")
			self.images.append(f.read())
			f.close()
		print "a chargé %d images pour %s" % (countImages, movie)

	def __del__(self):
		print "[UDP Pull] Fermeture du canal"
		
	def sendCurrentImage(self, host, port, image, fragmentNum = 0, tryNum = 0):
		"""
		Envoyer l'image courante vers le client qui écoute sur l'ip <host> et qui a envoyé à partir du <port> source,
		<image> est l'id qui commence à 1 (pour le fichier 1.jpg), <fragmentNum> commence à 0 et s'incrémente de 1 en 1
		pour chaque morceau de l'image, <tryNum> sert à éviter de renvoyer un nombre infini de fois	l'image courante si
		le buffer est plein : au bout de quelques essais on sacrifie l'image
		"""
		client = self.clients[host+":%s" % port] # récupère un pointeur vers le client

		tailleImage = len(self.images[image])
		# si fragmentSize = 1024, le fragment 0 est à l'adresse @0, le fragment 1 à @1024, le 2 @2048...
		fragmentPos = fragmentNum * client["fragmentSize"]
		
		if fragmentPos + client["fragmentSize"] > tailleImage:
			# on envoie le dernier fragment de l'image et donc la taille du fragment est <= fragmentSize
			finImage = True
			tailleFragment = tailleImage - fragmentPos
		else:
			finImage = False
			tailleFragment = client["fragmentSize"]


		# génère un message en correspondance avec le format voulu dans le protocole
		message = "%s%s%s%s%s%s%s%s%s" % (image, SEP, tailleImage,\
		SEP, fragmentPos, SEP, tailleFragment, SEP, self.images[image][fragmentPos:fragmentPos + tailleFragment])

		try:
			self.transport.write(message, (host, client["port"]))
		except socket.error:
			print "Buffer d'envoi UDP rempli, baisser la qualité des images et/ou la fréquence"
			tryNum += 1 # on incrémente le nombre de tentatives en cas d'échec (buffer plein)
		else:
			fragmentNum += 1 # si l'envoi s'est bien effectué, on passe au fragment suivant

		if not finImage and tryNum < 2: # on ne fait que 2 tentatives d'envoi par fragment, si on dépasse ce seuil on saute à l'image suivante
			# on dit au réacteur de nous rappeler tout de suite (0 sec) pour qu'on envoie le fragment suivant, on lui rend la main
			# pour qu'il puisse effectivement envoyer le message qu'on lui a donné avec self.transport.write(...) (sinon il ne peut pas le faire : prog évènementielle)
			reactor.callLater(0, self.sendCurrentImage, host, port, image, fragmentNum, tryNum)
	

	def datagramReceived(self, data, (host, port)):
		"""
		A chaque trame UDP reçue on regarde quel est la commande.
		"""
		# a-t-on déjà vu ce client ou pas ?
		if not host+":%s" % port in self.clients:
			# réponse : non, on le crée !
			self.clients[host+":%s" % port]= {}
			client = self.clients[host+":%s" % port]
			client["imagecourante"] = 1 # on commence par envoyer l'image 1
		else:
			# réponse : oui, on récupère un pointeur sur ce client
			client = self.clients[host+":%s" % port]
		
		# découpe la trame en lignes
		for line in data.split(SEP):
			if (line.find("GET -1") == 0):
				self.sendCurrentImage(host, port, client["imagecourante"])

				# à la fin d'une vidéo on boucle
				if client["imagecourante"] == len(self.images) - 1:
					client["imagecourante"] = 1
				else:
					client["imagecourante"] += 1
				
			elif (line.find("LISTEN_PORT") == 0):
				print "[UDP Pull] reçu = " + str(data)
				# on note le port auquel envoyer les messages pour ce client
				client["port"] = int(line.split(" ")[1])

			elif (line.find("FRAGMENT_SIZE") == 0):
				print "[UDP Pull] reçu = " + str(data)
				# pour ne pas perturber les clients buggués, on ne considère que 80% du fragment_size annoncé (donc les entêtes peuvent
				# être comptées tout en conservant une trame inférieure à fragment_size
				client["fragmentSize"]= int(0.8*int(line.split(" ")[1]))
				# on augmente le buffer UDP d'envoi, sinon il sature très vite (défaut = 2048 octets sur windows)
				self.transport.getHandle().setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, client["fragmentSize"] * 200)

			elif (line.find("END") == 0):
				print "[UDP Pull] reçu = " + str(data)
				# on enlève le client de notre dictionnaire pour en accepter un autre futur avec même ip et même port source
				del self.clients[host+":%s" % port]


	def connectionMade(self):
		print "[UDP Pull] Canal connecté !"

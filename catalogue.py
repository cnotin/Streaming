# -*- coding: utf-8 -*-

class Catalogue():
	"""
	Recense la logique inhérente à la gestion du Catalogue : lecture à partir
	d'un fichier dans un dictionnaire, puis re-conversion de ce qui a été lu vers
	le format texte (pour envoyer au client).
	"""

	def __init__(self, fichier):
		"""
		On prend le path du fichier catalogue.txt que l'on va parser (attention au format).
		"""
		self.objects = []

		f = open(fichier, "r")
		temp = f.readlines()
		self.servAddr = temp[0].split(": ")[1].strip() #ip locale du serveur
		#port local du serveur, attention : doit être libre car ce n'est pas vérifié !
		self.servPort = int(temp[1].split(": ")[1])
		print "J'écoute sur l'adresse IP %s et le port %d" % (self.servAddr, self.servPort)
		
		print "Chargement du catalogue et des images en mémoire...\n"
		# pour chaque ligne du catalogue (exceptée les 2 premières qui ont déjà été lues pour
		# l'IP et le port
		for line in temp[2:]:
			splittedLine = line.split("=")
			id = int(splittedLine[1].split(" ")[0]) #ID de la vidéo
			name = splittedLine[2].split(" ")[0] # son nom
			type = splittedLine[3].split(" ")[0] # son type
			addr = splittedLine[4].split(" ")[0] # son IP
			# on remplace automatiquement les occurences de "MYIP" par l'IP locale du serveur
			# (plus pratique pour écrire le catalogue"
			addr = addr.replace("MYIP", self.servAddr)
			port = int(splittedLine[5].split(" ")[0]) # port de la vidéo, doit être libre sinon erreur non gérée
			protocole = splittedLine[6].split(" ")[0] # protocole de la vidéo (TCP_PULL, UDP_PUSH ...)
			ips = float(splittedLine[7].split(" ")[0]) # fps pour la vidéo
			# on ajoute toutes ces infos dans notre liste de vidéos
			self.objects.append((id, name, type, addr, port, protocole, ips))



	def getCatalogue(self):
		"""
		Transforme le catalogue que l'on conserve sous forme objet en mémoire en sa représentation textuelle
		pour l'envoyer au client qui le demande en HTTP.
		"""
		retour = "ServerAddress: " + self.servAddr + "\r\n"
		retour += "ServerPort: " + str(self.servPort) + "\r\n"
		for objet in self.objects:
			retour += "Object ID=" + str(objet[0]) + " name=" + objet[1] + " type=" + objet[2] + " address=" + \
			objet[3] + " port=" + str(objet[4]) + " protocol=" + objet[5] + " ips=" + str(objet[6]) + "\r\n"
		retour += "\r\n"
		return retour

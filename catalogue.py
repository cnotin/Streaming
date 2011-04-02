# -*- coding: utf-8 -*-

class Catalogue():
	"""
	Recense la logique inhérente à la gestion du Catalogue : lecture à partir
	d'un fichier dans un dictionnaire, puis re-conversion de ce qui a été lu vers
	le format texte (pour envoyer au client).
	"""

	def __init__(self, fichier):
		"""
		On prend le path du fichier catalogue.txt que l'on va lire (attention au format).
		"""
		self.objects = []

		f = open(fichier, "r")
		temp = f.readlines()
		self.servAddr = temp[0].split(": ")[1].strip()
		self.servPort = int(temp[1].split(": ")[1])
		print "J'écoute sur l'adresse IP %s et le port %d" % (self.servAddr, self.servPort)
		
		print "Chargement du catalogue et des images en mémoire...\n"
		for line in temp[2:]:
			splittedLine = line.split("=")
			id = int(splittedLine[1].split(" ")[0])
			name = splittedLine[2].split(" ")[0]
			type = splittedLine[3].split(" ")[0]
			addr = splittedLine[4].split(" ")[0]
			addr = addr.replace("MYIP", self.servAddr)
			port = int(splittedLine[5].split(" ")[0])
			protocole = splittedLine[6].split(" ")[0]
			ips = float(splittedLine[7].split(" ")[0])
			self.objects.append((id, name, type, addr, port, protocole, ips))



	def getCatalogue(self):
		retour = "ServerAddress: " + self.servAddr + "\r\n"
		retour += "ServerPort: " + str(self.servPort) + "\r\n"
		for objet in self.objects:
			retour += "Object ID=" + str(objet[0]) + " name=" + objet[1] + " type=" + objet[2] + " address=" + \
			objet[3] + " port=" + str(objet[4]) + " protocol=" + objet[5] + " ips=" + str(objet[6]) + "\r\n"
		retour += "\r\n"
		return retour

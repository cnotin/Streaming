AHAHAHA lol




# -*- coding: utf-8 -*-

from HTTP import *
from twisted.internet import reactor


PRON = "pr0n"
SEP = "\r\n"


def main():
	print "Bonjour, bienvenue sur le serveur de streaming de Clément Notin et Thomas Piccolo (B3154)"
	try:
		ipFile = open("MYIP.conf", "r")
	except IOError:
		print "Le fichier de config de l'adresse IP locale, MYIP.conf, n'a pas été trouvé\nPassage à l'IP par défaut : 127.0.0.1 et port 4590"
		ip = "127.0.0.1"
		port = 4590
	else:
		(ip, port) = ipFile.readline().split(":")
		port = int(port)
		print "j'écoute sur l'adresse IP %s et le port %d" % (ip, port)
		ipFile.close()

	reactor.listenTCP(port, ServeurHTTPFactory(ip))
	reactor.run()

if __name__ == '__main__':
	main()

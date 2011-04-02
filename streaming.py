# -*- coding: utf-8 -*-

from HTTP import *
from twisted.internet import reactor


PRON = "pr0n"
SEP = "\r\n"


def main():
	print "Bonjour, bienvenue sur le serveur de streaming de Clément Notin et Thomas Piccolo (B3154)"
	
	cat = Catalogue("catalogue.txt")
	
	reactor.listenTCP(cat.servPort, ServeurHTTPFactory(cat))
	reactor.run()

if __name__ == '__main__':
	main()

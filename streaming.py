# -*- coding: utf-8 -*-

from HTTP import *
from twisted.internet import reactor


PRON = "pr0n"
SEP = "\r\n"


def main():
	print "Bonjour, veuillez entrer l'IP locale (ENTREE pour 127.0.0.1"
	ip = raw_input()
	if ip == "":
		ip = "127.0.0.1"
	reactor.listenTCP(4590, ServeurHTTPFactory(ip))
	reactor.run()

if __name__ == '__main__':
	main()

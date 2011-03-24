# -*- coding: utf-8 -*-

from HTTP import *
from twisted.internet import reactor


PRON = "pr0n"
SEP = "\r\n"


def main():
	print "Welcome"
	reactor.listenTCP(4590, ServeurHTTPFactory())
	reactor.run()

if __name__ == '__main__':
	main()

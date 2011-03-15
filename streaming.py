# -*- coding: utf-8 -*-

from catalogue import Catalogue
from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ClientEndpoint
from twisted.internet.protocol import Factory
from twisted.internet.protocol import Protocol
from twisted.protocols.basic import LineReceiver

PRON = "pr0n\\"
SEP = "\r\n"

def gotProtocol(p):
	p.factory.client = p

class PullProtocol(Protocol):
	def __init__(self):
		print "creation pull proto"
		self.image_id = 1
		self.images = []
		self.images.append("") #car ceci commence à 0 et la première image a l'index 1
		for i in range(1,148):
			print "image %s" % i
			f = open(PRON + "mavideo\\img" + str(i) + ".jpg", "rb")
			self.images.append(f.read())
			f.close()
		
	def sendMessage(self, message):
		self.transport.write(message)
		
	def sendCurrentImage(self):
		if self.image_id == len(self.images):
			self.image_id = 1
		#print "j'envoie l'image %s" % self.image_id
		self.sendMessage("%s%s%s%s%s" % (self.image_id, SEP, len(self.images[self.image_id]), SEP,  self.images[self.image_id]))
		self.image_id += 1


class TCPPull(LineReceiver):
	def __init__(self):
		pass
	def __del__(self):
		pass

	def lineReceived(self, line):
		#print "TCP PULL = " + line
		if (line.find("LISTEN_PORT") == 0):
			point = TCP4ClientEndpoint(reactor, self.transport.getPeer().host, int(line.split(" ")[1]))
			d = point.connect(self.factory.pullFactory)
			d.addCallback(gotProtocol)
		elif (line.find("GET -1") == 0):
			if ("client" in self.factory.pullFactory.__dict__):
				self.factory.pullFactory.client.sendCurrentImage()
			

	def connectionMade(self):
		print "TCP pull connecté !"

class TCPPullFactory(Factory):
	protocol = TCPPull
	pullFactory = None

	def __init__(self):
		self.pullFactory = Factory()
		self.pullFactory.protocol = PullProtocol



class ServeurHttp(LineReceiver):
	def __init__(self):
		self.delimiter = "\n"
	def __del__(self):
		pass

	def addHeader(self, msg):
		header = "HTTP/1.1 200 OK" + SEP + "Server: localhost" + SEP + "Connection: Keep-Alive" + SEP + "Content-Type: text/txt" + SEP + "Content-Length: "
		header += str(len(msg))
		msg = header + SEP + SEP + msg
		return msg

	def lineReceived(self, line):
		print "HTTP = " + line
		#on a un GET mais pas pour le catalogue => dégage
		if ((line.find("GET") == 0) and (line.find("GET /catalog") == -1)):
			self.transport.loseConnection()
		if (line.find("GET /catalog") != -1):
			self.transport.write(self.addHeader(self.factory.cat.getCatalogue()))

	def connectionMade(self):
		print "client connecté"



class ServeurHTTPFactory(Factory):
	protocol = ServeurHttp

	def __init__(self):
		self.cat = Catalogue("catalogue.txt")
		for objet in self.cat.objects:
			if objet[5] == "TCP_PULL":
				reactor.listenTCP(objet[4], TCPPullFactory())


def main():
	print "Welcome"
	reactor.listenTCP(4590, ServeurHTTPFactory())
	reactor.run()

if __name__ == '__main__':
	main()

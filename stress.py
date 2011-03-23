# -*- coding: utf-8 -*-

from twisted.internet import reactor
from twisted.internet.protocol import Factory, Protocol
from twisted.internet.endpoints import TCP4ClientEndpoint
import time

SEP = "\r\n"

def tcpPullConnected(p, video):
	p.launch(video)

class TCPPullData(Protocol):
	def __init__(self):
		self.taille = 0
		self.startTime = time.time()
		print "data connecte"
	
	def dataReceived(self, data):
		self.taille += len(data)
		print "débit (ko/s) %d" % (self.taille / (time.time() - self.startTime) / 1000)
	
	
class TCPPullDataFactory(Factory):
	protocol = TCPPullData	
	
class StressTCPPull(Protocol):
	def __init__(self):
		print "création StressTCPPull"
		self.compteur = 0
		
	def launch(self, video):
		print "lancement stress tcp pull " + str(video)
		reactor.listenTCP(4690, TCPPullDataFactory())
		self.transport.write("LISTEN_PORT 4690" + SEP)
		self.stress()
	
	def stress(self):
		print "bim %s" % self.compteur
		self.transport.write("GET -1" + SEP)
		self.compteur += 1
		reactor.callLater(0, self.stress)

def catalogueConnected(p):
	print "Catalogue connected"
	p.sendMessage("GET /catalogue.txt" + SEP + SEP)


class Catalogue(Protocol):
	def __init__(self):
		self.objects = []

	def sendMessage(self, msg):
		self.transport.write(msg)
	
	def dataReceived(self, data):
		self.parse(data.split(SEP)[8:-2])
		#for obj in self.objects:
		obj = self.objects[0]
		if obj[5] == "TCP_PULL":
			factory = Factory()
			factory.protocol = StressTCPPull
			point = TCP4ClientEndpoint(reactor, obj[3], obj[4])
			d = point.connect(factory)
			d.addCallback(tcpPullConnected, obj)
		
	def prettyPrint(self):
		for objet in self.objects:
			print "Object ID=" + str(objet[0]) + " name=" + objet[1] + " type=" + objet[2] + " address=" + \
			objet[3] + " port=" + str(objet[4]) + " protocol=" + objet[5] + " ips=" + str(objet[6])
		
	def parse(self, cat):
		for obj in cat:
			splittedLine = obj.split("=")
			id = int(splittedLine[1].split(" ")[0])
			name = splittedLine[2].split(" ")[0]
			type = splittedLine[3].split(" ")[0]
			addr = splittedLine[4].split(" ")[0]
			port = int(splittedLine[5].split(" ")[0])
			protocole = splittedLine[6].split(" ")[0]
			ips = float(splittedLine[7].split(" ")[0])
			self.objects.append((id, name, type, addr, port, protocole, ips))
			
		self.prettyPrint()

def main():
	print "Welcome"
	factory = Factory()
	factory.protocol = Catalogue
	point = TCP4ClientEndpoint(reactor, "localhost", 4590)
	d = point.connect(factory)
	d.addCallback(catalogueConnected)
	reactor.run()

if __name__ == '__main__':
	main()

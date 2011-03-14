from catalogue import Catalogue
from twisted.internet import reactor
from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver

class ServeurHttp(LineReceiver):
        def __init__(self):
                self.delimiter = "\n"
        def __del__(self):
                pass

        def addHeader(self, msg):
                header = "HTTP/1.1 200 OK\r\nServer: localhost\r\nConnection: Keep-Alive\r\nContent-Type: text/txt\r\nContent-Length: "
                header += str(len(msg))
                msg = header + "\r\n\r\n" + msg
                return msg

        def lineReceived(self, line):
                #on a un GET mais pas pour le catalogue => dégage
                if ((line.find("GET") == 0) and (line.find("GET /catalogue") == -1)):
                        self.transport.loseConnection()
                if (line.find("GET /catalogue") != -1):
                        self.transport.write(self.addHeader(self.factory.cat.getCatalogue()))

                

        def connectionMade(self):
                print "client connecté"

class ServeurHTTPFactory(Factory):
        protocol = ServeurHttp

        def __init__(self):
                self.cat = Catalogue("catalogue.txt")


def main():
        print "Welcome"
        reactor.listenTCP(4590, ServeurHTTPFactory())
        reactor.run()

if __name__ == '__main__':
        main()

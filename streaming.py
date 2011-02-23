from twisted.internet.protocol import Protocol, Factory
from twisted.internet import reactor
from twisted.protocols.basic import LineReceiver
from catalogue import Catalogue


class ServeurHttp(LineReceiver):
        def __init__(self):
                self.cat = Catalogue("catalogue.txt")

        def __del__(self):
                pass

        def addHeader(self, msg):
                header = "HTTP/1.1 200 OK\r\nServer: localhost\r\nConnection: Keep-Alive\r\nContent-Type: text/txt\r\nContent-Length: "
                header += str(len(msg))
                msg = header + "\r\n\r\n" + msg
                return msg

        def lineReceived(self, line):
                if (line.find("GET /catalogue") != -1):
                        self.transport.write(self.addHeader(self.cat.getCatalogue()))
                #self.transport.loseConnection()

        def connectionMade(self):
                print "client connecté"


def main():
        print "Welcome"
        f = Factory()
        f.protocol = ServeurHttp
        reactor.listenTCP(4590, f)
        #stdio.StandardIO(ServeurHttp())
        reactor.run()

if __name__ == '__main__':
        main()

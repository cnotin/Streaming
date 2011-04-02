# -*- coding: utf-8 -*-

import glob
import os
from streaming import VIDEOTHEQUE
from streaming import SEP
from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ClientEndpoint
from twisted.internet.protocol import Factory
from twisted.internet.protocol import Protocol
from twisted.internet.task import LoopingCall
from twisted.protocols.basic import LineReceiver


class TCPPushData(Protocol):
    def __init__(self):
        print "[TCP Push] Construction du canal de données"
        self.image_id = 1

    def __del__(self):
        self.transport.loseConnection()
        print "[TCP Push] Fermeture du canal de données"

    def sendCurrentImage(self, images):
        # on boucle une fois arrivé à la fin de la vidéo
        if self.image_id == len(images):
            self.image_id = 1

        self.transport.write(images[self.image_id])
        self.image_id += 1


def gotProtocol(p, tcpPushControl):
    """
    Callback appelé quand la connexion a été établie, on veut donner au tcpPushControl du canal de contrôle,
    une référence vers le protocol qui gère le canal de données, pour pouvoir dans l'objet du canal de contrôle
    déclencher des méthodes de l'objet du canal de données.
    """
    tcpPushControl.clientProtocol = p # p : TCPPushData, protocol du canal de données

class TCPPushControl(LineReceiver):
    """
    Protocole créé à chaque instance de canal de contrôle.

    Quand on reçoit LISTEN_PORT, on va lancer la connexion vers le client. Cela peut être long et comme nous
    sommes dans un paradigme de programmation évènementielle c'est intolérable donc on dit au réacteur de se
    connecter et il nous rappellera quand cela sera fait. C'est pour cela que nous avons self.clientProtocol
    qui est initialisé à None puis renseigné une fois que le callback de connexion établie sera appelé.
    """
    def __init__(self):
        print "[TCP Push] Création du canal de contrôle"
        self.clientProtocol = None

        # self.lc est l'objet de type LoopingCall, qui sera utilisé pour créer un évènement répétitif qui délenchera l'envoi des images
        self.lc = None

    def __del__(self):
        print "[TCP Push] Fermeture du canal de contrôle"

    def lineReceived(self, line):
        print "[TCP Push] reçu = " + line
        if (line.find("START") == 0):
            if self.clientProtocol: # nous nous sommes connectés avec succès au client
                self.isSending = True # on mémorise que la vidéo est en état de lecture, utilisé au moment du END
                if not self.lc: # si le LoopingCall n'existe pas encore (premier START de l'échange)
                    # on le crée
                    self.lc = LoopingCall(self.clientProtocol.sendCurrentImage, self.factory.images)
                # et on le lance avec la bonne fréquence, en commençant tout de suite (now=True) : n'attend pas le premier appel
                self.lc.start(1./self.factory.fps, now=True)
            else: # la connexion vers le client n'a pas encore été établie, on enregistre ce "START" et on le redéclenche
            # jusqu'à ce que la connexion ait bien été établie (comme ça on ne perd pas le message)
                reactor.callLater(0, self.lineReceived, line)

        elif (line.find("PAUSE") == 0):
            self.isSending = False # on mémorise que la vidéo est en pause, utilisé au moment du END
            self.lc.stop() # on stoppe l'envoi en arrêtant la boucle répétitive

        elif (line.find("LISTEN_PORT") == 0):
            # tentative de connexion au client
            point = TCP4ClientEndpoint(reactor, self.transport.getPeer().host, int(line.split(" ")[1]))
            d = point.connect(self.factory.tcpPushDataFactory) # Factory qui va créer un objet TCPPushData qui va gérer cette connexion
            # Quand la connexion s'est bien déroulée, appeler ce callback
            d.addCallback(gotProtocol, self)

        elif (line.find("END") == 0):
            # si on était en train d'envoyer des images, il faut arrêter (car une fois la connexion fermée, le fait de continuer est une erreur)
            if self.isSending:
                self.lc.stop()
            self.transport.loseConnection()
            del self.clientProtocol

    def connectionMade(self):
        print "[TCP Push] Canal de contrôle connecté !"


class TCPPushControlFactory(Factory):
    """
    Factory qui va créer un objet TCPPushControl par client qui se connecte au canal de contrôle d'une vidéo TCP Push.
    La factory rassemble les attributs partagés par les différentes instances : les images de la vidéos.
    """
    protocol = TCPPushControl
    tcpPushDataFactory = None # factory qui ca créer les canaux de données

    def __init__(self, movie, fps):
        self.tcpPushDataFactory = Factory()
        self.tcpPushDataFactory.protocol = TCPPushData # la factory du canal de données crée un objet TCPPushData par vidéo visualisée
        self.fps = fps # on push les images à une certaine fréquence qui nous est donnée

        self.images = []
        self.images.append("") #car un tableau commence à 0 et la première image à l'index 1

        imagesPath = os.path.join(VIDEOTHEQUE, movie)
        # compte toutes les images (*.jpg) présentes dans le répertoire, attention si un fichier .jpg qui ne fait pas partie de la vidéo
        # est présent il sera compté comme tel et posera problème
        countImages = len(glob.glob1(imagesPath,"*.jpg"))

        for i in range(1, countImages + 1):
            # charger 1.jpg, 2.jpg, 3.jpg etc...
            f = open(os.path.join(imagesPath, str(i) + ".jpg"), "rb")
            imageData = f.read()
            # les headers de chaque paquet, image par image, sont précalculés car ils ne changent pas à l'exécution
            self.images.append("%s%s%s%s%s" % (i, SEP, len(imageData), SEP,  imageData))
            f.close()
        print "a chargé %d images pour %s" % (countImages, movie)

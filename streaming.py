# -*- coding: utf-8 -*-

from HTTP import *
from twisted.internet import reactor
import os

# Dossier dans lequel sont stockées les vidéos
VIDEOTHEQUE = os.path.join("..", "videotheque")

# Séparateur réseau utilisé dans le serveur HTTP par exemple
SEP = "\r\n"


def main():
    print "Bonjour, bienvenue sur le serveur de streaming de Clément Notin et Thomas Piccolo (B3154)"

    # On charge le catalogue, et les images de toutes les vidéos _en mémoire_ !
    cat = Catalogue(os.path.join(VIDEOTHEQUE, "catalogue.txt"))

    # Lancement du serveur HTTP
    reactor.listenTCP(cat.servPort, ServeurHTTPFactory(cat))
    reactor.run()

if __name__ == '__main__':
    main()

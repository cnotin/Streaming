class Catalogue():
        def __init__(self, fichier):
                self.fichier = fichier
                self.objects = []

                f = open(self.fichier, "r")
                temp = f.readlines()
                self.servAddr = temp[0].split(": ")[1].strip()
                self.servPort = int(temp[1].split(": ")[1])
                for line in temp[2:]:
                        id = int(line.split("=")[1].split(" ")[0])
                        name = line.split("=")[2].split(" ")[0]
                        type = line.split("=")[3].split(" ")[0]
                        addr = line.split("=")[4].split(" ")[0]
                        port = int(line.split("=")[5].split(" ")[0])
                        protocole = line.split("=")[6].split(" ")[0]
                        ips = float(line.split("=")[7].split(" ")[0])
                        self.objects.append((id, name, type, addr, port, protocole, ips))



        def getCatalogue(self):
                retour = "ServerAddress: " + self.servAddr + "\r\n"
                retour += "ServerPort: " + str(self.servPort) + "\r\n"
                for objet in self.objects:
                        retour += "Object ID=" + str(objet[0]) + " name=" + objet[1] + " type=" + objet[2] + " address=" + \
                        objet[3] + " port=" + str(objet[4]) + " protocol=" + objet[5] + " ips=" + str(objet[6]) + "\r\n"
                retour += "\r\n"
                return retour
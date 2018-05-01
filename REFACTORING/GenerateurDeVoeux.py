import csv
from Parcours import *


class GenerateurDeVoeux:


    def __init__(self, directoryName, optimizer):
        self.optimizer = optimizer
        self.nbDossiersGeneres = 0
        self.directoryName = directoryName
        try:
            os.mkdir(directoryName)
        except:
            pass


    def generer(self, N):
        for i in range(N):
            try:
                path = self.directoryName+"/"+str(self.nbDossiersGeneres)
                os.mkdir(path)
            except:
                pass
            for Parcours_Objet in self.optimizer.ListeDesParcours:
                Parcours_Objet.generer_csv_aleatoires(path)
            self.nbDossiersGeneres += 1



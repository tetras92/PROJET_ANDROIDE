# -*- coding: utf-8 -*-
"""
Created on Sun Mar 11 22:11:50 2018

@author: amoussou
"""
import csv
from Parcours import *
import os
class Generateur_Voeux:
    
    nbMaxUEParVoeu = 5
    directoryName = "/Vrac/DAK/RAND_VOEUX"
    
    def __init__(self, fichierDescParcours, fichierEDT):
        self.fichierDescParcours = fichierDescParcours
        self.ListeDesParcours = list()
        self.nbDossiersGeneres = 0
        self.DictCapaciteTotaleUE = dict()

        edt = open(fichierEDT)
        data = csv.DictReader(edt)


        for csv_line in data:
            intitule = csv_line["intitule"]
            nb_groupes = int(csv_line["nb_groupes"])
            ListeCapacites = [int(csv_line["capac"+str(i)]) for i in range(1,int(nb_groupes)+1)]
            self.DictCapaciteTotaleUE[intitule] = sum(ListeCapacites)

        # print(self.DictCapaciteTotaleUE)
        
    def generer(self):
        self.ListeDesParcours = list() #Vider à chaque fois la listeDesParcours
        csvfile = open(self.fichierDescParcours, 'r')
        parcoursreader = csv.DictReader(csvfile, delimiter=',')
        self.nbDossiersGeneres += 1
        try:
            os.mkdir(Generateur_Voeux.directoryName+str(self.nbDossiersGeneres))
        except:
            pass
        
        for parcoursCsvLine in parcoursreader:
            current_parcours = Parcours(parcoursCsvLine, self.DictCapaciteTotaleUE)
            self.ListeDesParcours.append(current_parcours)
            path = Generateur_Voeux.directoryName+str(self.nbDossiersGeneres)
            current_parcours.generer_csv_aleatoires(path)
        csvfile.close()

        return path, self.ListeDesParcours



                

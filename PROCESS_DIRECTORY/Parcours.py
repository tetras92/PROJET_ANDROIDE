# -*- coding: utf-8 -*-
"""
Created on Sun Mar 11 13:06:08 2018

@author: amoussou
"""

import random
import csv
import numpy as np
# import scipy.stats as stat
import math
import itertools as it
# import CompatibilityModel
from CompatibilityModel import *
class Parcours:


        def __init__(self, csvLine, DictNbConfig):
            self.nom = csvLine["parcours"]
            self.effectifMin = int(csvLine["effectif_min"])
            self.effectifMax = int(csvLine["effectif_max"])
            self.ListeUEObligatoires = [csvLine["oblig"+str(i)] for i in range(1, 3+1) if csvLine["oblig"+str(i)] != ""] #**
            self.nbUEObligatoires = len(self.ListeUEObligatoires)
            self.ListeUEConseilles = [csvLine["cons"+str(i)] for i in range(1, 8+1) if csvLine["cons"+str(i)] != ""] #***
            self.nbUEConseilles = len(self.ListeUEConseilles)
            # print([csvLine["P"+str(i)] for i in range(1, 6)])
            self.Proportions = [float(csvLine["P"+str(i)]) for i in range(1, 6)]
            self.EnsembleIdEtudiantsInsatisfaits = set()
            self.EnsembleIdUEInsatisfaites = set()

            # self.ListeCapaciteUEConseillees = [DictCapaciteUE[ue_cons] for ue_cons in self.ListeUEConseilles]
            # ANCIENNE METHODE CHOIX DES UES CONSEILLEES
            # self.ListeProbaUEConseillees = [1.0*valeur/sum(self.ListeCapaciteUEConseillees) for valeur in self.ListeCapaciteUEConseillees]
            self.ListeProbaUEConseillees = [float(csvLine["Pcons"+str(i)]) for i in range(1, 8+1) if csvLine["Pcons"+str(i)] != ""]
            # print("somme" + self.nom , self.ListeProbaUEConseillees)
            self.DicoConfigurations = dict()
            self.DictNbConfig = DictNbConfig


        def constituer_voeu(self, k):
            """Construit un voeu de k UE"""

            nbMaxUEObligatoiresDuVoeu = min(self.nbUEObligatoires, k)
            nbMinUEObligatoiresDuVoeu = self.nbUEObligatoires - (5 - k)
            if nbMinUEObligatoiresDuVoeu < 0:
                nbMinUEObligatoiresDuVoeu = 0
#            print("nb min oblig " +  str(nbMinUEObligatoiresDuVoeu))
            nbUEObligatoiresDuVoeu = random.randint(nbMinUEObligatoiresDuVoeu, nbMaxUEObligatoiresDuVoeu) #PEUT eTRE AFFINEE AVEC LES PROBA DE REUSSIR UNE UE OBLIGATOIRES
#            print("nb voeu oblig " + str(nbUEObligatoiresDuVoeu))
            nbUeConseilleesDuVoeu = k - nbUEObligatoiresDuVoeu
            ListeChoixUEObligatoires = random.sample([i for i in range(len(self.ListeUEObligatoires))], nbUEObligatoiresDuVoeu)

            #Orienter le choix des ues conseillees en fonction de la notoriete de l'UE (sa capacite max)
            ListeChoixUEConseillees = np.random.choice([i for i in range(len(self.ListeUEConseilles))], nbUeConseilleesDuVoeu, replace=False, p=self.ListeProbaUEConseillees)
            # print(ListeChoixUEConseillees)
            # ListeChoixUEConseillees = random.sample([i for i in range(len(self.ListeUEConseilles))], nbUeConseilleesDuVoeu) #Trop SIMPLISTE

            contratUEObligatoires = [self.ListeUEObligatoires[ue_oblig] for ue_oblig in ListeChoixUEObligatoires]
            contratUEConseillees = [self.ListeUEConseilles[ue_cons] for ue_cons in ListeChoixUEConseillees]
            contratUEConseillees.sort()
            contratUEObligatoires.sort()
            contrat = contratUEObligatoires + contratUEConseillees
            # contrat.sort()
            if len(contrat) > 1 and self.DictNbConfig[self.nom][tuple(contrat)] == 0.0: #l'orde oblig avant conseilles importants
                    # print("incompatible cree")
                    return self.constituer_voeu(k)
            return contratUEObligatoires, contratUEConseillees

        def generer_csv_aleatoires(self, directoryName):
            """Genere un csv aleatoire d'au plus n etudiants au cas ou 0 apparait dans les tirages aleatoires (loi binomiale n, P)"""
            file = open(directoryName + "/voeux."+self.nom, "w")

            fieldnames = ["num"] + ["oblig"+str(i) for i in range(1,4)] + ["cons"+str(i) for i in range(1,6)]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            effectif = random.randint(self.effectifMin, self.effectifMax)
            self.set_effectif(effectif)
            # print(self.Proportions)

            s = np.random.multinomial(effectif, self.Proportions, size=1)[0]

            s = [v for i in range(len(s)) for v in [i+1]*s[i]]
            random.shuffle(s)
            # print(s)
#            print (s)
#            s = np.random.binomial(5, P, n) #****
            id_rel = 0
            for i in range(len(s)):
                current_nb_ue = s[i]
                if current_nb_ue != 0:
                    id_rel += 1
                    L_Oblig, L_Cons = self.constituer_voeu(current_nb_ue)
                    csvLine = dict()
                    csvLine["num"] = id_rel
                    for o in range(len(L_Oblig)):
                        csvLine["oblig"+str(o+1)] = L_Oblig[o]
                    for c in range(len(L_Cons)):
                        csvLine["cons"+str(c+1)] = L_Cons[c]
                    writer.writerow(csvLine)
            
                        
            file.close()
            
        def set_effectif(self, effectif):
            self.effectif = effectif

        def generer_dico_Nbconfig(self):
            for taille_voeu in range(2,6): #A elargir a toutes les tailles
                nbMaxUEObligatoiresDuVoeu = min(self.nbUEObligatoires, taille_voeu)
                nbMinUEObligatoiresDuVoeu = max(0, self.nbUEObligatoires - (5 - taille_voeu))
                # print(nbMaxUEObligatoiresDuVoeu, nbMinUEObligatoiresDuVoeu)
                # if nbMinUEObligatoiresDuVoeu < 0:
                #     nbMinUEObligatoiresDuVoeu = 0
                for nbUEOblig in range(nbMinUEObligatoiresDuVoeu, nbMaxUEObligatoiresDuVoeu+1):
                    nbUECons = taille_voeu - nbUEOblig
                    # print(list(it.combinations(self.ListeUEObligatoires, nbUEOblig)))
                    for combiO in it.combinations(self.ListeUEObligatoires, nbUEOblig):
                        ss_ContratOblig = list(combiO)
                        ss_ContratOblig.sort()
                        # print(ss_ContratOblig)
                        # print(list(it.combinations(self.ListeUEConseilles, nbUECons)))
                        for combiC in it.combinations(self.ListeUEConseilles, nbUECons):
                            ss_ContratCons = list(combiC)
                            ss_ContratCons.sort()
                            Contrat = ss_ContratOblig + ss_ContratCons
                            # Contrat.sort()
                            # print(Contrat)
                            cM = CompatibilityModel("edt.csv", Contrat)
                            ContratStr , nb_config = cM.resoudre()
                            # print(ContratStr)
                            cM.remise_a_zero()
                            ContratStr = tuple(ContratStr)
                            nb_config = int(nb_config)
                            self.DicoConfigurations[ContratStr] = nb_config
            return self.DicoConfigurations


# L = [1,2,3,4]
# print(list(it.combinations(L, 2)))

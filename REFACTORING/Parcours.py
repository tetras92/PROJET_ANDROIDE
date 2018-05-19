import csv
import itertools as it
import random
import time

import numpy as np

from CompatibilityModel import *


class Parcours:


        def __init__(self, csvLine, optimizer):
            self.optimizer = optimizer
            self.optimizer_Params = optimizer.Parameters
            self.nom = csvLine["parcours"]
            self.index = int(csvLine["index"])
            self.effectifMin = int(csvLine["effectif_min"])
            self.effectifMax = int(csvLine["effectif_max"])
            self.ListeUEObligatoires = [csvLine["oblig"+str(i)] for i in range(1, self.optimizer_Params.nbMaxUEObligatoires+1) if csvLine["oblig"+str(i)] != ""] #**
            self.nbUEObligatoires = len(self.ListeUEObligatoires)
            self.ListeUEConseilles = [csvLine["cons"+str(i)] for i in range(1, self.optimizer_Params.nbMaxUEConseilleesParcours+1) if csvLine["cons"+str(i)] != ""] #***
            self.nbUEConseilles = len(self.ListeUEConseilles)
            # print([csvLine["P"+str(i)] for i in range(1, 6)])
            self.Proportions = [float(csvLine["P"+str(i)]) for i in range(1, self.optimizer_Params.TailleMaxContrat+1)]

            self.EnsembleIdEtudiantsInsatisfaits = set()
            self.EnsembleIdUEInsatisfaites = set()

            self.ListeProbaUEConseillees = [float(csvLine["Pcons"+str(i)]) for i in range(1, self.optimizer_Params.nbMaxUEConseilleesParcours+1) if csvLine["Pcons"+str(i)] != ""]
            self.mesEtudiants = list()
            self.DicoConfigurations = dict()
            deb = time.time()
            self.generer_dico_Nbconfig()
            # print ("....." * int(time.time() - deb + 1)*9)
            self.effectif = 0

            # self.mesEtudiantsAProbleme = list()
            # self.lesContratsAProbleme  = list()
            self.effectifNonInscrit = 0

            self.HistoriqueDesContratsAProbleme = list()

        # def reinitialiser_parcours(self,avecSauvegarde=True):
        #     if avecSauvegarde:
        #         self.HistoriqueDesContratsAProbleme = self.HistoriqueDesContratsAProbleme + self.lesContratsAProbleme
        #     self.mesEtudiants = list()
        #     self.effectif = 0
        #     self.effacer_donnees_problemes_affectation()

        def get_dico_configurations(self):
            return self.DicoConfigurations

        def effacer_donnees_problemes_affectation(self):
            self.effectifNonInscrit = 0
            self.mesEtudiants = list()
            self.effectif = 0
            # self.lesContratsAProbleme = list()
            # self.mesEtudiantsAProbleme = list()

        def constituer_voeu(self, k):
            """Construit un voeu de k UE"""

            nbMaxUEObligatoiresDuVoeu = min(self.nbUEObligatoires, k)
            nbMinUEObligatoiresDuVoeu = self.nbUEObligatoires - (5 - k)
            if nbMinUEObligatoiresDuVoeu < 0:
                nbMinUEObligatoiresDuVoeu = 0

            nbUEObligatoiresDuVoeu = random.randint(nbMinUEObligatoiresDuVoeu, nbMaxUEObligatoiresDuVoeu) #PEUT eTRE AFFINEE AVEC LES PROBA DE REUSSIR UNE UE OBLIGATOIRES

            nbUeConseilleesDuVoeu = k - nbUEObligatoiresDuVoeu
            ListeChoixUEObligatoires = random.sample([i for i in range(len(self.ListeUEObligatoires))], nbUEObligatoiresDuVoeu)


            ListeChoixUEConseillees = np.random.choice([i for i in range(len(self.ListeUEConseilles))], nbUeConseilleesDuVoeu, replace=False, p=self.ListeProbaUEConseillees)

            contratUEObligatoires = [self.ListeUEObligatoires[ue_oblig] for ue_oblig in ListeChoixUEObligatoires]
            contratUEConseillees = [self.ListeUEConseilles[ue_cons] for ue_cons in ListeChoixUEConseillees]
            contratUEConseillees.sort()
            contratUEObligatoires.sort()
            contrat = contratUEObligatoires + contratUEConseillees
            # contrat.sort()
            if len(self.DicoConfigurations) != 0 and len(contrat) > 1 and self.DicoConfigurations[tuple(contrat)] == 0.0: #l'orde oblig avant conseilles importants
                    # print "Peut pas creer", tuple(contrat)
                    # print("incompatible cree")
                    return self.constituer_voeu(k)
            return contratUEObligatoires, contratUEConseillees

        def generer_csv_aleatoires(self, path):
            """Genere un csv aleatoire d'au plus n etudiants au cas ou 0 apparait dans les tirages aleatoires (loi binomiale n, P)"""
            file = open(path + "/voeux."+self.nom, "w")

            fieldnames = ["num"] + ["oblig"+str(i) for i in range(1,self.optimizer.Parameters.nbMaxUEObligatoires + 1)] + ["cons"+str(i) for i in range(1,self.optimizer.Parameters.nbMaxUEConseillees + 1)]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            effectif = random.randint(self.effectifMin, self.effectifMax)
            # self.set_effectif(effectif)
            # print(self.Proportions)

            s = np.random.multinomial(effectif, self.Proportions, size=1)[0]

            s = [v for i in range(len(s)) for v in [i+1]*s[i]]
            random.shuffle(s)

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

        def maj_effectif(self):
            self.effectif = len(self.mesEtudiants)

        def generer_dico_Nbconfig(self):
            self.DicoConfigurations = dict()
            print "\033[38;5;102m{} : Generation des contrats incompatibles ... en cours ...\n".format(self.nom)
            for taille_voeu in range(2,self.optimizer_Params.TailleMaxContrat+1): #A elargir a toutes les tailles
                nbMaxUEObligatoiresDuVoeu = min(self.nbUEObligatoires, taille_voeu)
                nbMinUEObligatoiresDuVoeu = max(0, self.nbUEObligatoires - (5 - taille_voeu))

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

                            self.optimizer.effacer_donnees_affectation_UEs()
                            # deb = time.time()
                            cM = CompatibilityModel(Contrat, self.optimizer)
                            ContratStr, nb_config = cM.resoudre()
                            # print time.time() - deb
                            # self.optimizer.nettoyer_les_Ues_et_les_Incompatibilites()

                            ContratStr = tuple(ContratStr)
                            nb_config = int(nb_config)
                            self.DicoConfigurations[ContratStr] = nb_config
            print u"\033[37;1m"
            # print "{} : FIN Generation des contrats incompatibles\n\033[37;1m".format(self.nom)
            self.optimizer.effacer_donnees_affectation_UEs()
            self.actualiser_dico_contrats_incompatibles()
            return self.DicoConfigurations

        def actualiser_dico_contrats_incompatibles(self):
            nb_contrat_incompatible_de_taille_5 = 0
            for contrat, nbConfig in self.DicoConfigurations.items():
                if len(contrat) == self.optimizer.Parameters.TailleMaxContrat and nbConfig == 0:
                    nb_contrat_incompatible_de_taille_5 += 1
            self.optimizer.dict_nombre_de_contrats_incompatibles_par_parcours[self.nom] = nb_contrat_incompatible_de_taille_5

        def rajouter_etudiant(self, Etu):
            self.mesEtudiants.append(Etu)
            self.maj_effectif()

        def get_intitule(self):
            return self.nom

        def get_index(self):
            return self.index

        # def get_mes_Etudiants(self):
        #     return self.mesEtudiants

        def get_mes_etudiants(self):
            return [None] + self.mesEtudiants

        def signalerUnProblemeDinscription(self, idRelatif):
            self.effectifNonInscrit += 1
            # self.mesEtudiantsAProbleme.append(str(self.get_mes_etudiants()[idRelatif]))
            # self.lesContratsAProbleme.append(self.get_mes_etudiants()[idRelatif].get_contrat())      L'IDEE INITIALE C'ETAIT DE POUVOIR AVOIR UNE IDEE DES CONTRAT AVEC DES CONFIG SERREES MAIS IDEES ABANDONNEES

        def str_nb_etudiants_insatisfaits(self):
            return self.nom + "(" + str(self.effectifNonInscrit) + ")[{}%]  ".format(round(100. - 100.0*self.effectifNonInscrit/self.effectif, 2))

        def afficher_carte_incompatibilites(self,taille):
            Liste = list()
            print_tuple = list()
            exists = False
            for tuple_, nbConfig in self.DicoConfigurations.items():
                if taille == len(tuple_) and nbConfig == 0:
                    exists = True
                    Liste.append((tuple_, nbConfig))
                    l = ""
                    for ue in tuple_:
                        l +=self.optimizer.DictUEs[ue].intituleCOLOR()+" - "

                    l = l[:-2]
                    print_tuple.append(l)
            # Liste.sort(key=lambda elmt:elmt[1])
            # for elmt in Liste:
            #     print list(elmt[0])
            for elem in print_tuple:
                print "\t"+ elem +"\n"
            return exists

        def get_Liste_ue_conseillees(self):
            return [self.optimizer.DictUEs[ue].get_id() for ue in self.ListeUEConseilles]

        def __str__(self):
            s = "Parcours : " + self.nom + "\n\t\tEffectif : {} etudiants dont {} insatisfaits ({}%)\n".format(self.effectif, self.effectifNonInscrit, round(100. - 100.0*self.effectifNonInscrit/self.effectif, 2))
            return s

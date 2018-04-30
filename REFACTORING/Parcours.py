import random
import numpy as np
import itertools as it
import csv
import CompatibilityModel

class Parcours:


        def __init__(self, csvLine, optimizer):
            self.optimizer = optimizer
            self.optimizer_Params = optimizer.Parameters
            self.nom = csvLine["parcours"]
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
            self.DicoConfigurations = self.generer_dico_Nbconfig()
            self.effectif = 0
            self.mesEtudiantsAProbleme = list()
            self.lesContratsAProbleme  = list()

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
            if len(contrat) > 1 and self.DicoConfigurations[self.nom][tuple(contrat)] == 0.0: #l'orde oblig avant conseilles importants
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
            # self.set_effectif(effectif)
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

        def maj_effectif(self, effectif):
            self.effectif = len(self.mesEtudiants)

        def generer_dico_Nbconfig(self):
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
                            # Contrat.sort()
                            # print(Contrat)
                            cM = CompatibilityModel(Contrat, self.optimizer)
                            ContratStr, nb_config = cM.resoudre()
                            # print(ContratStr)
                            ContratStr = tuple(ContratStr)
                            nb_config = int(nb_config)
                            self.DicoConfigurations[ContratStr] = nb_config
            return self.DicoConfigurations

        def rajouter_etudiant(self, Etu):
            self.mesEtudiants.append(Etu)
            self.maj_effectif()

        def get_intitule(self):
            return self.nom

        def get_mes_Etudiants(self):
            return self.mesEtudiants

        def get_mes_etudiants(self):
            return [None] + self.mesEtudiants

        def signalerUnProblemeDinscription(self, idRelatif):
            self.mesEtudiantsAProbleme.append(str(self.get_mes_etudiants()[idRelatif]))
            self.lesContratsAProbleme.append(self.get_mes_etudiants()[idRelatif].get_contrat())

        def str_nb_etudiants_insatisfaits(self):
            return self.nom + "(" + str(len(self.mesEtudiantsAProbleme)) + ")  "

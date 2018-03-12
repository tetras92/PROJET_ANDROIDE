import numpy as np
import random
import csv
class Analyses():

    nbMaxUEObligatoires = 3
    nbMaxUEConseillees = 8

    class Parcours:


        def __init__(self, csvLine):
            self.nom = csvLine["parcours"]
            self.ListeUEObligatoires = [csvLine["oblig"+str(i)] for i in range(1, Analyses.nbMaxUEObligatoires+1)]
            self.nbUEObligatoires = len(self.ListeUEObligatoires)
            self.ListeUEConseilles = [csvLine["cons"+str(i)] for i in range(1, Analyses.nbMaxUEConseillees+1)]
            self.nbUEConseilles = len(self.ListeUEConseilles)

        def constituer_voeux(self, k):
            """Construit un voeu de k UE"""

            nbMinUEObligatoiresDuVoeu = self.nbUEObligatoires - (Analyses.modelePrincipal.nbMaxVoeuxParEtudiant - k)
            nbUEObligatoiresDuVoeu = random.randint(nbMinUEObligatoiresDuVoeu, self.nbUEObligatoires) #PEUT eTRE AFFINEE AVEC LES PROBA DE REUSSIR UNE UE OBLIGATOIRES
            nbUeConseilleesDuVoeu = k - nbUEObligatoiresDuVoeu
            ListeChoixUEObligatoires = random.sample([i for i in range(len(self.ListeUEObligatoires))], nbUEObligatoiresDuVoeu)
            ListeChoixUEConseillees = random.sample([i for i in range(len(self.ListeUEConseilles))], nbUeConseilleesDuVoeu)
            contratUEObligatoires = [self.ListeUEObligatoires[ue_oblig] for ue_oblig in ListeChoixUEObligatoires]
            contratUEConseillees = [self.ListeUEConseilles[ue_cons] for ue_cons in ListeChoixUEConseillees]

            return contratUEObligatoires, contratUEConseillees

        def generer_csv_aleatoires(self, n, P):
            """Genere un csv aleatoire d'au plus n etudiants au cas ou 0 apparait dans les tirages aleatoires (loi binomiale n, P)"""
            file = open("../RAND_VOEUX/voeux."+self.nom)

            fieldnames = ["num"] + ["oblig"+str(i) for i in range(1,4)] + ["cons"+str(i) for i in range(1,6)]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()

            s = np.random.binomial(Analyses.modelePrincipal.nbMaxVoeuxParEtudiant, n)
            id_rel = 0
            for i in range(len(s)):
                L_Oblig, L_Cons = self.constituer_voeux(s[i])
                return #A enlever









    def __init__(self, modelMain):
        self.nb_calculs = 0
        self.nb_graphes = 0
        self.modelePrincipal = modelMain

        self.capaciteMaximale = self.calculer_capaciteMaximale()
        self.nombreDemandesInscriptions = len(self.modelePrincipal.ListedesVarY)
        self.charge = round(100.0*self.nombreDemandesInscriptions/self.capaciteMaximale,2)

        self.ListeDesParcours = self.modelePrincipal.ListeDesParcours
        self.ListeEffectifDesParcours = self.modelePrincipal.ListeEffectifDesParcours
        self.nombreTotalEtudiants = sum(self.ListeEffectifDesParcours)
        self.DistributionNbUEParParcours = {i : list() for i in range(len(self.ListeDesParcours))}
        self.maj_DistributionNbUEParParcours()
        self.ListeEffectifsDesRedoublants = [len([val for val in self.DistributionNbUEParParcours[i] if val < self.modelePrincipal.nbMaxVoeuxParEtudiant]) for i in range(len(self.ListeDesParcours))]
        self.nombreTotalRedoublants = sum(self.ListeEffectifsDesRedoublants)
        self.pourcentageRedoublants = self.nombreTotalRedoublants/self.nombreTotalEtudiants

    def incrementer_nb_calculs(self):
        self.nb_calculs += 1

    def incrementer_nb_graphes(self):
        self.nb_graphes += 1

    def calculer_capaciteMaximale(self):
        capMax = 0
        for ue in range(1, len(self.modelePrincipal.ListeDesUEs)):
            capMax += sum(self.modelePrincipal.ListeDesUEs[ue].get_ListeDesCapacites())
        return capMax

    def maj_DistributionNbUEParParcours(self):
        # f = open("maison.csv","w")
        # f.write("0,")
        # parcours = 0
        for etu in range(1, len(self.modelePrincipal.ListeDesEtudiants)):
            currentEtudiant = self.modelePrincipal.ListeDesEtudiants[etu]
            # if currentEtudiant.get_index_parcours() == parcours:
            #     f.write(str(currentEtudiant.get_nombreDeVoeux())+",")
            # else:
            #     parcours = currentEtudiant.get_index_parcours()
            #     f.write("\n"+str(parcours)+",")
            #     f.write(str(currentEtudiant.get_nombreDeVoeux())+",")
            self.DistributionNbUEParParcours[currentEtudiant.get_index_parcours()].append(currentEtudiant.get_nombreDeVoeux())


    def __str__(self):
        s = "**********ANALYSES OPTIMISTATION DES INSCRIPTIONS AUX UE (PAR DAK)**********\n\n"
        s += "\t\tNombre total d'etudiants : {}\n".format(self.nombreTotalEtudiants)
        s += "\t\tNombre total de redoublants*: {}\t\t\t*Etudiants dont le contrat contient moins de cinq (05) UE\n".format(self.nombreTotalRedoublants)
        s += "\t\tCapacite maximale : {}\n\t\tNombre totale de demandes d'inscriptions : {}\n".format(self.capaciteMaximale, self.nombreDemandesInscriptions)
        s += "\t\tCharge : {}%\n".format(self.charge)
        L = [nb_ue for (idParcours, L) in self.DistributionNbUEParParcours.items() for nb_ue in L]
        L = np.array(L)

        s += "\t\tNombre Moyen d'UE par Etudiant : {} ({})\n".format(round(np.mean(L),2), round(np.std(L),2))
        # s += str(self.DistributionNbUEParParcours)
        s += "\t\tPar Parcours:\n"
        for i in range(len(self.ListeDesParcours)):
            L_array = np.array(self.DistributionNbUEParParcours[i])
            s += "\t\t\t{} : Redoublants : {}/{} soit {}%\n\t\t\t\t ".format(self.ListeDesParcours[i], self.ListeEffectifsDesRedoublants[i], self.ListeEffectifDesParcours[i], round(100*self.ListeEffectifsDesRedoublants[i]/self.ListeEffectifDesParcours[i],2))
            s += " Nombre Moyen d'UE par Etudiant : {} ({})\n".format(round(np.mean(L_array),2), round(np.std(L_array),2))
        #
        # ,np.mean(np.array(self.DistributionNbUEParParcours[i])), np.std(np.array(self.DistributionNbUEParParcours[i]))
        return s




    def maj_resumeDesInscriptionsNonSatisfaites(self, ue, parcours, etu):
        """ue, parcours des entiers"""
        if ue not in self.resumeDesInscriptionsNonSatisfaites:
            self.resumeDesInscriptionsNonSatisfaites[self.ListeDesUes[ue]]#LIGNE A COMPLETER
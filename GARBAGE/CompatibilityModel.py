import numpy as np
import matplotlib.pyplot as plt
import csv
import copy
import os

import random
from gurobipy import *
import itertools


def produit_cartesien(L1, L2):
    def f(a, L):
        if len(L) == 1:
            return [[a, L[0]]]
        return [[a, L[0]]] + f(a, L[1:])
    return [u for a in L1 for u in f(a, L2)]


L1 = [1, 2, 3]
L2 = [2,0]

L3 = [4]
L4 = [5,1]

def produit_cartesien_mult(LL):
    if len(LL) < 2:
        return []

    PC = produit_cartesien(LL[0], LL[1])

    def final(PC, LLR):
        if len(LLR) == 0:
            return PC
        PC = [couple+[elem] for couple in PC for elem in LLR[0]]
        return final(PC, LLR[1:])

    return final(PC, LL[2:])

#Modele d'un dictionnaire Creneau
def generer_model_dict_creneau(nbMaxGroupeParUE):
        modelDict = dict()
        modelDict[0] = set()
        for k in range(nbMaxGroupeParUE):
            modelDict[k+1] = set()
        return modelDict
#Fin Modele


class CompatibilityModel():
    """ Le Modele Geneneral:\nSes attributs (des variables statiques) :
                ListeDesEtudiants : liste des objets Etudiants
                EDT : Liste de dictionnaires des creneaux
                ModelGurobi : le modele Gurobi
                DictUEs : dictionnaire des UEs; cle: intitule - valeur: Objet UE
                ListeDesUEs : Liste des references vers les UEs indicees sur leur id
                EnsIncompatibilites : ensemble des Incompatibilites
                ListeDesParcours: Listes des parcours (des String)
                ListeEffectifDesParcours : Liste des Effectifs par parcours
                ListeDesEffectifsCumules : Liste des Effectifs Cumules des Parcours pour retrouver les etudiants dans la grande liste

                idModel : identifiant du modele dans le cas d'une simulation aleatoire
                nbMaxVoeuxParEtudiant : int
                nbMaxGroupeParUE : int
                nbMaxUEObligatoires/parcours : int
                nbMaxUEConseillees/parcours : int
                nbMaxCoursParUE : int
                nbCreneauxParSemaine : int
                nbUE : nombre total d'Ues du Master d'Informatique
                charge : la charge (rapport du nombre de demandes d'inscriptions sur la capaciteMaximale
                capaciteMaximale :  cumul des capacites d'accueil de tous les groupes de toutes les ues
                proportionSatisfaction : pourcentage des inscriptions satisfaites
                """
  #TMP
    count = 0
    JCVV = list()
    #FIN TMP

# Par defaut
    nbMaxVoeuxParEtudiant = 5
    nbMaxGroupeParUE = 5
    nbMaxUEObligatoires = 3                      # REMPLACER PAR DES VARIABLES FACULTATIVES
    nbMaxUEConseillees = 5
    nbMaxCoursParUE = 2
    nbCreneauxParSemaine = 25
    nbUE = 21
    edtInitialise = False
    tauxEquilibre = 0.05
# Fin Defaut


    EDT = [dict()] + [generer_model_dict_creneau(nbMaxGroupeParUE) for i in range(0, nbCreneauxParSemaine)]
    ListeDesUEs = ["null"] + ["null"]*nbUE
    DictUEs = dict()

    ListeDesEtudiants = ["null"]
    ListeDesParcours = list()
    ListeEffectifDesParcours = list()
    ListeDesEffectifsCumules = list()
    EnsIncompatibilites = set()
    nbTotalIncompatibilites = 0
    nbTotalIncompatibilitesVides = 0
    nbInscriptionsSatisfaites = 0
    ListedesVarY = list()
    #Jeudi 15
    charge = 0
    capaciteMaximale = 0
    #Jeudi 15

    ListeDesEtudiantsParParcours = list()
    DictionnaireDesInsatisfactionsParParcours = dict()
    DictionnaireDistribUEInsatisfaitesParParcours = dict()

    modelGurobi = Model("OPTIMISATION DES INSCRIPTIONS AUX UE (PAR DAK)")
    idModel = 1
    #Vendredi 16
    proportionSatisfaction = 0
    #Mardi 20
    # DDecisionEtuUE = dict()
    #Jeudi 22
    # DNbrUeContrat = dict()
    class Incompatibilite:
        """Classe definissant une incompatibilite"""
        def __init__(self, idUEI, idGroupK, idUEJ, idGroupL):
            """Definit une incompatiblite de type ((idUEI, idGroupK),(idUEJ, idGroupL))"""

            self.ueGroup1 = idUEI, idGroupK      #Un couple (UE, Group)
            self.ueGroup2 = idUEJ, idGroupL      #Un couple (UE, Group)
            self.ensEtuConcernes =  CompatibilityModel.ListeDesUEs[idUEI].getEnsEtu() & CompatibilityModel.ListeDesUEs[idUEJ].getEnsEtu()  #L'ensemble des etudiants auxquels s'applique l'incompatibilite (Etudiant sous la forme x_Parcous_idRelatif (des strings))
            self.vide = (len(self.ensEtuConcernes) == 0)    #Un booleen
            CompatibilityModel.nbTotalIncompatibilites += 1
            if self.vide:
                CompatibilityModel.nbTotalIncompatibilitesVides += 1
        def __str__(self):
            """Retourne la chaine d'affichage de l'incompatibilite et l'effectif des etudiants concernes"""
            s = "Incompatibilite entre l'UE/Groupe {} et l'UE/Groupe {}\n\tNombre d'etudiants concernes: {}\n\n".format(self.ueGroup1, self.ueGroup2, len(self.ensEtuConcernes))

            return s

        def ajouterContrainteModeleGurobi(self, modelGurobi):
            if not self.vide:
                for etuName in self.ensEtuConcernes:
                    contrainte = LinExpr()
                    modelGurobi.addConstr(modelGurobi.getVarByName(etuName+"_%d"%self.ueGroup1[0]+"_%d"%self.ueGroup1[1]) + modelGurobi.getVarByName(etuName+"_%d"%self.ueGroup2[0]+"_%d"%self.ueGroup2[1]) <= 1)

                modelGurobi.update()



    class UE:
        """Classe definissant une UE"""
        def __init__(self,csv_line):
            self.id =int(csv_line["id_ue"])
            self.intitule = csv_line["intitule"]
            self.nb_groupes = int(csv_line["nb_groupes"])
            self.ListeCapacites = [int(csv_line["capac"+str(i)]) for i in range(1,int(self.nb_groupes)+1)]
            self.EnsEtuInteresses = set()
            self.ListeCreneauxCours = [int(csv_line["cours"+str(i)]) for i in range(1,CompatibilityModel.nbMaxCoursParUE+1) if csv_line["cours"+str(i)] != ""]
            self.ListeCreneauxTdTme = [()]+[(csv_line["td"+str(i)],csv_line["tme"+str(i)]) for i in range(1,int(self.nb_groupes)+1)]
            self.ResumeDesAffectations = ["null"] + [set()]*self.nb_groupes
            self.nbInscrits = 0
            self.ListeNonInscrits = list()
            self.ListeEtudiantsGroupes = [list() for kk in range(self.nb_groupes+1)]
            self.capaciteTotale = sum(self.ListeCapacites)
            self.equilibre = True

        def actualiseEDT(self):
            """MAJ de l'EDT"""
            for creneauCours in self.ListeCreneauxCours:
                CompatibilityModel.EDT[creneauCours][0].add(self.id)
            for gr_i in range(1, self.nb_groupes+1):
                creneauTdTme = self.ListeCreneauxTdTme[gr_i]
                try:
                    CompatibilityModel.EDT[int(creneauTdTme[0])][gr_i].add(self.id)      #Td
                    CompatibilityModel.EDT[int(creneauTdTme[1])][gr_i].add(self.id)      #tme
                except:
                    pass

        def get_id(self):
            return self.id

        def get_capaciteTotale(self):
            return self.capaciteTotale


        def get_nb_groupes(self):
            return self.nb_groupes

        def ajouterEtuInteresses(self, name):
            self.EnsEtuInteresses.add(name)

        def getEnsEtu(self):
            return self.EnsEtuInteresses

        def ajouterContrainteCapaciteModelGurobi(self, modelGurobi):
            """ajoute toutes les contraintes de  capacites de groupe au modele"""
            for idGroup in range(1, self.nb_groupes+1):
                modelGurobi.addConstr(quicksum(modelGurobi.getVarByName(etu+"_%d"%self.id+"_%d"%idGroup) for etu in self.EnsEtuInteresses) <= self.ListeCapacites[idGroup-1])
            modelGurobi.update()

        def ajouterContraintesEquilibre(self, modelGurobi):
            for idGroup1 in range(1, self.nb_groupes+1):
                for idGroup2 in range(idGroup1+1, self.nb_groupes+1):
                    modelGurobi.addConstr(quicksum((1./self.ListeCapacites[idGroup1-1])*modelGurobi.getVarByName(etu+"_%d"%self.id+"_%d"%idGroup1) for etu in self.EnsEtuInteresses) + quicksum((-1./self.ListeCapacites[idGroup2-1])*modelGurobi.getVarByName(etu+"_%d"%self.id+"_%d"%idGroup2) for etu in self.EnsEtuInteresses) <= CompatibilityModel.tauxEquilibre)
                    modelGurobi.addConstr(quicksum((1./self.ListeCapacites[idGroup1-1])*modelGurobi.getVarByName(etu+"_%d"%self.id+"_%d"%idGroup1) for etu in self.EnsEtuInteresses) + quicksum((-1./self.ListeCapacites[idGroup2-1])*modelGurobi.getVarByName(etu+"_%d"%self.id+"_%d"%idGroup2) for etu in self.EnsEtuInteresses) >= -1.*CompatibilityModel.tauxEquilibre)
            modelGurobi.update()

                    #TO BE CONTINUED

        def affecterEtuGroup(self, parcours, idRelatif, idGroup):
            self.ResumeDesAffectations[idGroup].add((parcours, idRelatif))

        def ajouterUnInscrit(self):
            self.nbInscrits += 1

        def signalerNonInscrit(self, parcours, idRelatif):
            self.ListeNonInscrits.append((parcours, idRelatif))

        def get_intitule(self):
            return self.intitule

        def get_ListeDesCapacites(self):
            return self.ListeCapacites

        def inscrire(self, etuName, numeroGroupe):
                self.ListeEtudiantsGroupes[numeroGroupe].append(etuName)

        def get_nbInscrits(self):
            return self.nbInscrits

        def get_nbInteresses(self):
            return len(self.EnsEtuInteresses)

        def set_equilibre(self):
            for idL1 in range(1, self.nb_groupes+1):
                for idL2 in range(idL1+1, self.nb_groupes+1):
                    if abs(len(self.ListeEtudiantsGroupes[idL1])/self.ListeCapacites[idL1-1]- len(self.ListeEtudiantsGroupes[idL2])/self.ListeCapacites[idL2-1]) > CompatibilityModel.tauxEquilibre:
                        self.equilibre = False
            #AJOUTER LA CARACTERISTIQUE DE COULEUR PASTILLE L'IDEE D'UN MAX
        def __str__(self):
            """ Retourne la chaine representant une UE"""
            s = "UE {} ({}) :\n\tNombre de groupes : {}\n\tCapacite totale d'accueil: {}\n\t".format(self.intitule, self.id, self.nb_groupes, sum(self.ListeCapacites))
            s += "Equilibre? : {}\n\t".format(self.equilibre)
            #CRENEAUX
            # s += "\tLes Creneaux\n\t"
            # for cours in self.ListeCreneauxCours:
            #     s += "\tCours: {}\n\t".format(cours)
            #                                                                                     #LES CRENEAUX
            # for i in range(1, len(self.ListeCreneauxTdTme)):                                     #LES CRENEAUX
            #     td, tme = self.ListeCreneauxTdTme[i]                                            #LES CRENEAUX
            #     s += "\tTD {} : {}\n\t".format(i, td)
            #     s += "\tTME {} : {}\n\t".format(i, tme)

            s += "\tNombre Etudiants interesses: {}\n\t".format(len(self.EnsEtuInteresses))
            s += "Nombre Etudiants effectivement inscrits : {}\n\t".format(self.nbInscrits)
            s += "Les Non-inscrits : "
            for parcours, idRelatif in self.ListeNonInscrits:
                s += str(idRelatif)+"("+CompatibilityModel.ListeDesParcours[int(parcours)]+") "
            s += "\n\tLes Inscrits:\n"
            for numGroup in range(1, len(self.ListeEtudiantsGroupes)):
                s += "\t\tGroupe {} [{}/{}] : ".format(numGroup, len(self.ListeEtudiantsGroupes[numGroup]), self.ListeCapacites[numGroup-1])
                for etu in self.ListeEtudiantsGroupes[numGroup]:
                    s += etu + " "
                s += "\n"
            s+= "\n\n"


            return s

    class Etudiant:
        """ Classe representant un etudiant"""
        def __init__(self,csv_line, parcours, indexParcours):
            self.idRelatif = int(csv_line["num"])
            self.parcours = parcours
            self.indexParcours = indexParcours
            self.ue_obligatoires = [CompatibilityModel.DictUEs[csv_line["oblig"+str(id)]].get_id() for id in range(1, CompatibilityModel.nbMaxUEObligatoires+1) if csv_line["oblig"+str(id)] != ""]
            self.ue_non_obligatoires = [CompatibilityModel.DictUEs[csv_line["cons"+str(id)]].get_id() for id in range(1, CompatibilityModel.nbMaxUEConseillees+1) if csv_line["cons"+str(id)] != ""]
            # **
            # L = CompatibilityModel.DDecisionEtuUE[parcours] + self.ue_non_obligatoires
            # L.sort()
            # CompatibilityModel.DDecisionEtuUE[parcours] = L
            # ** bincount

            self.nombreDeVoeux = len(self.ue_obligatoires) + len(self.ue_non_obligatoires)

            # CompatibilityModel.DNbrUeContrat[parcours].append(self.nombreDeVoeux)

            self.varName = "x_{}_{}".format(self.indexParcours, self.idRelatif)
            self.ListeDesInscriptions = list()

        def gerer_variables_contraintes_ue_obligatoires(self,modelGurobi):
            """ajoute les contraintes relatives aux ue obligatoires"""
            objectif = modelGurobi.getObjective()

            for id_ue in self.ue_obligatoires:
                var = modelGurobi.addVar(vtype=GRB.BINARY, lb=0, name="y_%d"%self.indexParcours+"_%d"%self.idRelatif+"_%d"%id_ue)
                CompatibilityModel.ListedesVarY.append("y_{}_{}_{}".format(self.indexParcours, self.idRelatif, id_ue))
                contrainte = LinExpr()
                for num_group in range(1, CompatibilityModel.ListeDesUEs[id_ue].get_nb_groupes()+1):
                    contrainte += modelGurobi.addVar(vtype=GRB.BINARY, lb=0, name=self.varName+"_%d"%id_ue+"_%d"%num_group)
                contrainte -= var

                objectif += var
                modelGurobi.addConstr(var , GRB.EQUAL, 1)   #y_i_j = 1
                modelGurobi.addConstr(contrainte, GRB.EQUAL, 0)

            modelGurobi.setObjective(objectif,GRB.MAXIMIZE) # NE PEUt-ON PAS S'EN PASSER
            modelGurobi.update()

        def gerer_variables_contraintes_ue_non_obligatoires(self, modelGurobi):
            """ajoute les contraintes relatives aux ue non obligatoires"""
            objectif = modelGurobi.getObjective()

            for id_ue in self.ue_non_obligatoires:
                var = modelGurobi.addVar(vtype=GRB.BINARY, lb=0, name="y_%d"%self.indexParcours+"_%d"%self.idRelatif+"_%d"%id_ue)
                CompatibilityModel.ListedesVarY.append("y_{}_{}_{}".format(self.indexParcours, self.idRelatif, id_ue))
                contrainte = LinExpr()
                for num_group in range(1, CompatibilityModel.ListeDesUEs[id_ue].get_nb_groupes()+1):
                    contrainte += modelGurobi.addVar(vtype=GRB.BINARY, lb=0, name=self.varName+"_%d"%id_ue+"_%d"%num_group)
                contrainte -= var

                objectif += var

                #VERIFIER LES CONTRAINTES DU MODELES
                modelGurobi.addConstr(contrainte, GRB.EQUAL, 0)

            modelGurobi.setObjective(objectif,GRB.MAXIMIZE) # NE PEUt-ON PAS S'EN PASSER
            modelGurobi.update()

        def enregistrer_interet_pour_UE(self):
            for ue in self.ue_non_obligatoires + self.ue_obligatoires:
                if ue == 11:
                    CompatibilityModel.count += 1
                CompatibilityModel.ListeDesUEs[ue].ajouterEtuInteresses(self.varName)

        def get_nombreDeVoeux(self):
            return self.nombreDeVoeux

        def get_index_parcours(self):
            return  self.indexParcours

        def get_varName(self):
            return self.varName

        def entrer_inscription(self, ue, numeroGroup):
            if numeroGroup != 0:  #numeroGroup 0 signifie non accepte
                    chaine = CompatibilityModel.ListeDesUEs[ue].get_intitule()+str(numeroGroup)
                    CompatibilityModel.ListeDesUEs[ue].inscrire(str(self), numeroGroup)
            else:
                    chaine = CompatibilityModel.ListeDesUEs[ue].get_intitule()+"X"

                    pattern = ""
                    ListeTrieeDesUE = self.ue_obligatoires + self.ue_non_obligatoires
                    ListeTrieeDesUE.sort()
                    # print(ListeTrieeDesUE)
                    for ue in ListeTrieeDesUE:
                        pattern += CompatibilityModel.ListeDesUEs[ue].get_intitule() + " "

                    CompatibilityModel.DictionnaireDesInsatisfactionsParParcours[self.parcours].append([str(self),ListeTrieeDesUE]) #remplacer ListeTrieeDesUEs par pattern if pertinent
            if ue in self.ue_obligatoires:
                self.ListeDesInscriptions = [chaine] + self.ListeDesInscriptions
            else:
                self.ListeDesInscriptions.append(chaine)

        def enregistrer_affectation(self, file):
            """enregistre l'etat des inscriptions de l'etudiant dans le fichier des affectations corresopondant a son parcours"""
            file.write(str(self.idRelatif)+" ")
            for aff in self.ListeDesInscriptions:
                file.write(aff + " ")
            file.write("\n")

        def __str__(self):
            s = str(self.idRelatif)+"("+CompatibilityModel.ListeDesParcours[self.indexParcours]+")"
            return s

    # DEBUT CompatibilityModel





    def __init__(self, fileUE, ListeVoeux):
        """Initialise le model principal A COMPLeTER"""
        # Par defaut
        self.nbMaxVoeuxParEtudiant = 5
        self.nbMaxGroupeParUE = 5
        self.nbMaxUEObligatoires = 3                      # REMPLACER PAR DES VARIABLES FACULTATIVES
        self.nbMaxUEConseillees = 5
        self.nbMaxCoursParUE = 2
        self.nbCreneauxParSemaine = 25
        self.nbUE = 21
        # Fin Defaut

        #initialisations

        #Modele d'un dictionnaire Creneau
        # modelDict = dict()
        # modelDict[0] = set()
        # for k in range(self.nbMaxGroupeParUE):              A SUPPRIMER CE 31 MARS
        #     modelDict[k+1] = set()
        #Fin Modele

        #TRAITEMENT UE : GENERATION DE L'EDT ET DES OBJETS UE
        # if not (CompatibilityModel.edtInitialise): CompatibilityModel.edtInitialise = True
        self.ListeVarObj = list()
        f_ue = open(fileUE)
        data = csv.DictReader(f_ue)
        for ligneUE in data:
            currentUE = CompatibilityModel.UE(ligneUE) #Generation de l'objet UE
            currentUE.actualiseEDT()
            CompatibilityModel.ListeDesUEs[currentUE.get_id()] = currentUE             #Rajout a la listeUe
            CompatibilityModel.DictUEs[currentUE.intitule] = currentUE                  #Rajout au DictUe

            #NETTOYER EDT : supprimer les associations de numeros de groupe avec des ensembles vides
        for creneau in range(1, len(CompatibilityModel.EDT)):
            dictCopy = CompatibilityModel.EDT[creneau].copy()
            for id in dictCopy:
                if len(dictCopy[id]) == 0:
                    del CompatibilityModel.EDT[creneau][id]
            # FIN NETTOYAGE EDT

        #FIN TRAITEMENT UE

        #AJOUT ARTIFICIEL DE L'ETUDIANT
        for voeuEff in ListeVoeux:
            CompatibilityModel.ListeDesUEs[voeuEff].EnsEtuInteresses.add("x")

        #
        self.traiter_voeu_anonyme(ListeVoeux)

        #GERER LES INCOMPATIBILITES
        for creneauId in range(1, len(CompatibilityModel.EDT)):
            #incompatibilites groupesTdTme
            dictCreneau = CompatibilityModel.EDT[creneauId]

            for (idGroup1, EnsUE1) in dictCreneau.items():
                if idGroup1 != 0:
                    #Incompatibilite intra meme numeroGroup
                    for ueIntra1 in EnsUE1:
                        for ueIntra2 in EnsUE1:       #EnsUE2:  CORRECTION
                            if ueIntra1 < ueIntra2:
                                currentIncompatibilite = CompatibilityModel.Incompatibilite(ueIntra1, idGroup1, ueIntra2, idGroup1)
                                #Instruction Rajout au model
                                currentIncompatibilite.ajouterContrainteModeleGurobi(CompatibilityModel.modelGurobi)
                                #Fin
                                # if random.random() <= 0.5:
                                #     print(currentIncompatibilite)
                                CompatibilityModel.EnsIncompatibilites.add(currentIncompatibilite)
                #Fin Incompatibilite intra meme numeroGroup
                for (idGroup2, EnsUE2) in dictCreneau.items():
                    if idGroup1 > 0 and idGroup1 < idGroup2: # CONVENTION IdGroup1 < IdGroup2:
                        for ue1 in EnsUE1:
                            for ue2 in EnsUE2:
                                if ue1 != ue2: #l'incompatibilite entre deux groupes d'une meme ue est deja gere
                                    currentIncompatibilite = CompatibilityModel.Incompatibilite(ue1, idGroup1, ue2, idGroup2)
                                    #Instruction Rajout au model
                                    currentIncompatibilite.ajouterContrainteModeleGurobi(CompatibilityModel.modelGurobi)
                                    #Fin
                                    CompatibilityModel.EnsIncompatibilites.add(currentIncompatibilite)

            #Incompatibilite intra cours meme creneau + incompatibilite inter cours et td tme
            try:
                for ue1 in dictCreneau[0]:
                    #Incompatibilite intra cours meme creneau
                    nb_group_ue1 = CompatibilityModel.ListeDesUEs[ue1].get_nb_groupes()
                    for ue2 in dictCreneau[0]:
                        if ue1 < ue2:

                            nb_group_ue2 = CompatibilityModel.ListeDesUEs[ue2].get_nb_groupes() #CORRECTION ...  ListeDesUEs[ue2] au lieu de ListeDesUEs[ue1]
                            for idGroup1 in range(1, nb_group_ue1+1):
                                for idGroup2 in range(1, nb_group_ue2):
                                    currentIncompatibilite = CompatibilityModel.Incompatibilite(ue1, idGroup1, ue2, idGroup2)
                                    #Instruction Rajout au model
                                    currentIncompatibilite.ajouterContrainteModeleGurobi(CompatibilityModel.modelGurobi)
                                    #Fin
                                    # if random.random() <= 0.5:
                                    #     print(currentIncompatibilite)
                                    CompatibilityModel.EnsIncompatibilites.add(currentIncompatibilite)

                    # incompatibilite inter cours et td tme
                    for (idGroupTdTme, EnsUE2) in dictCreneau.items():
                        if idGroupTdTme > 0:
                            for ue2 in EnsUE2:
                                for idGroup1 in range(1, nb_group_ue1+1):
                                    currentIncompatibilite = CompatibilityModel.Incompatibilite(ue1, idGroup1, ue2, idGroupTdTme)
                                    #Instruction Rajout au model
                                    currentIncompatibilite.ajouterContrainteModeleGurobi(CompatibilityModel.modelGurobi)
                                    #Fin
                                    CompatibilityModel.EnsIncompatibilites.add(currentIncompatibilite)

            except:
                pass

        #FIN GESTION DES INCOMPATIBILITES
        
    def traiter_voeu_anonyme(self, ListeVoeux):
        for voeuUE in ListeVoeux:
            LVarXij = list()
            for idG in range(1, CompatibilityModel.ListeDesUEs[voeuUE].get_nb_groupes()+1):
                #cREATION DES VARIABLES XIJ
                var = CompatibilityModel.modelGurobi.addVar(vtype=GRB.BINARY, lb=0, name="x_%d"%idG+"_%d"%voeuUE)
                LVarXij.append(var)
            #CONTRAINTE D'INSCRIPTION OBLIGATOIRE DANS TOUTES LES UE
            CompatibilityModel.modelGurobi.addConstr(quicksum(xij for xij in LVarXij) == 1)

        #CREATION DE VARIABLES N_IJKLm

            #INSTANCIATION DE TOUTES LES COMBINAISONS
        L_Combi = [[i + 1 for i in CompatibilityModel.ListeDesUEs[ueId].get_nb_groupes()+1] for ueId in ListeVoeux]

        L_Combi = produit_cartesien_mult(L_Combi)

        for L_gr_combi in L_Combi:
            #cREATION DES VARIABLES XIJ
            varname = "n"
            for idG in L_gr_combi:
                varname = varname + "_" + str(idG)
            var = CompatibilityModel.modelGurobi.addVar(vtype=GRB.BINARY, lb=0, name=varname)
            self.ListeVarObj.append(var)

            Z = zip(L_gr_combi, ListeVoeux)
            CompatibilityModel.modelGurobi.addConstr(quicksum(CompatibilityModel.modelGurobi.getVarByName("x_%d"%gr+"_%d"%ue) for gr,ue in Z) >= len(ListeVoeux)*var)
        CompatibilityModel.modelGurobi.update()

    def resoudre(self):
        objectif = CompatibilityModel.modelGurobi.getObjective()
        for varN in self.ListeVarObj:
            objectif += varN
        CompatibilityModel.modelGurobi.setObjective(objectif,GRB.MAXIMIZE)
        CompatibilityModel.modelGurobi.update()
        CompatibilityModel.modelGurobi.optimize()
        CompatibilityModel.modelGurobi.getObjective().getValue()
# modelGurobi.addConstr(quicksum((1./self.ListeCapacites[idGroup1-1])*modelGurobi.getVarByName(etu+"_%d"%self.id+"_%d"%idGroup1) for etu in self.EnsEtuInteresses) + quicksum((-1./self.ListeCapacites[idGroup2-1])*modelGurobi.getVarByName(etu+"_%d"%self.id+"_%d"%idGroup2) for etu in self.EnsEtuInteresses) >= -1.*CompatibilityModel.tauxEquilibre)

# L = zip([1,2], [3,4])
# print L


cM = CompatibilityModel("gurobi.log", [11,6,16,13,10])

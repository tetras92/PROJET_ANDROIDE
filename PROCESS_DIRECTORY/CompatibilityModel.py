import numpy as np
import matplotlib.pyplot as plt
import csv
import copy
import os

import random
from gurobipy import *
import itertools
from gurobipy import *

def produit_cartesien(L1, L2):
    def f(a, L):
        if len(L) == 1:
            return [[a, L[0]]]
        return [[a, L[0]]] + f(a, L[1:])
    return [u for a in L1 for u in f(a, L2)]



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

    modelGurobi = Model("OPTIMISATION DES INSCRIPTIONS AUX UE (PAR DAK) COMPATIBILITE")
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

            self.ueGroup1 = idGroupK, idUEI      #Un couple (UE, Group)
            self.ueGroup2 = idGroupL, idUEJ      #Un couple (UE, Group)
            self.ensEtuConcernes =  CompatibilityModel.ListeDesUEs[idUEI].getEnsEtu() & CompatibilityModel.ListeDesUEs[idUEJ].getEnsEtu()  #L'ensemble des etudiants auxquels s'applique l'incompatibilite (Etudiant sous la forme x_Parcous_idRelatif (des strings))
            self.vide = (len(self.ensEtuConcernes) == 0)    #Un booleen
            CompatibilityModel.nbTotalIncompatibilites += 1
            if self.vide:
                CompatibilityModel.nbTotalIncompatibilitesVides += 1
            # else:
            #     print(self)
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
        self.ListeVoeux = ListeVoeux

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
        self.ListeVoeux = [CompatibilityModel.DictUEs[voeu].get_id() for voeu in self.ListeVoeux]
        #AJOUT ARTIFICIEL DE L'ETUDIANT [Se restreindre au ue des voeux provoque une erreur : 12 Avril ]
        for ue_ in self.ListeVoeux:#range(1, len(CompatibilityModel.ListeDesUEs)):
            CompatibilityModel.ListeDesUEs[ue_].EnsEtuInteresses.add("x")

        #
        self.traiter_voeu_anonyme(self.ListeVoeux)

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

    def traiter_voeu_anonyme(self): #GREAT CE 20/04
        CompatibilityModel.modelGurobi.setParam( 'OutputFlag', False )
        self.LVarXij = list()
        for voeuUE in self.ListeVoeux:

            for idG in range(1, CompatibilityModel.ListeDesUEs[voeuUE].get_nb_groupes()+1):
                #cREATION DES VARIABLES XIJ
                # print (idG, voeuUE)
                var = CompatibilityModel.modelGurobi.addVar(vtype=GRB.BINARY, lb=0, name="x_%d"%idG+"_%d"%voeuUE)
                self.LVarXij.append(var)
            #CONTRAINTE D'INSCRIPTION OBLIGATOIRE DANS TOUTES LES UE
            # CompatibilityModel.modelGurobi.addConstr(quicksum(xij for xij in LVarXij) == 1)
            CompatibilityModel.modelGurobi.update()

        #CREATION DE VARIABLES N_IJKLm

            #INSTANCIATION DE TOUTES LES COMBINAISONS
        L_Combi = [[i + 1 for i in range(CompatibilityModel.ListeDesUEs[ueId].get_nb_groupes())] for ueId in self.ListeVoeux]
        # print L_Combi
        L_Combi = produit_cartesien_mult(L_Combi)
        # print L_Combi

        nbConfig = len(L_Combi)
        for L_gr_combi in L_Combi:
            #cREATION DES VARIABLES N_I
            varname = "n"
            for idG in L_gr_combi:
                varname = varname + "_" + str(idG)
            var = CompatibilityModel.modelGurobi.addVar(vtype=GRB.BINARY, lb=0, name=varname)
            # CompatibilityModel.modelGurobi.update()

            self.ListeVarObj.append(var)
            CompatibilityModel.modelGurobi.update()

            Z = zip(L_gr_combi, self.ListeVoeux)
            # print Z
            cst = CompatibilityModel.modelGurobi.addConstr(quicksum(CompatibilityModel.modelGurobi.getVarByName("x_%d"%gr+"_%d"%ue) for gr,ue in Z) >= len(ListeVoeux)*var)
            cst2 = CompatibilityModel.modelGurobi.addConstr(var, GRB.EQUAL, 1)
            CompatibilityModel.modelGurobi.update()
            CompatibilityModel.modelGurobi.optimize()

            status = CompatibilityModel.modelGurobi.Status
            if status == GRB.Status.INFEASIBLE:
                print L_gr_combi
                nbConfig -= 1

            CompatibilityModel.modelGurobi.reset()
            CompatibilityModel.modelGurobi.remove(var)
            CompatibilityModel.modelGurobi.remove(cst)
            CompatibilityModel.modelGurobi.remove(cst2)

            CompatibilityModel.modelGurobi.update()
            # print(cst)
        CompatibilityModel.modelGurobi.update()
        print nbConfig

    def resoudre(self):
        objectif = CompatibilityModel.modelGurobi.getObjective()
        for varN in self.ListeVarObj:
            objectif += varN
        CompatibilityModel.modelGurobi.setObjective(objectif,GRB.MAXIMIZE)

        CompatibilityModel.modelGurobi.update()
        # print(CompatibilityModel.modelGurobi.getObjective())
        CompatibilityModel.modelGurobi.setParam( 'OutputFlag', False )

        CompatibilityModel.modelGurobi.optimize()
        # for varName in self.ListeVarObj:
        #     if varName.x == 1:
        #         print varName
        # for varName in self.LVarXij:
        #     if varName.x == 0:
        #         print varName
        # self.ListeVoeux.sort()
        ListeVoeux = [CompatibilityModel.ListeDesUEs[ueI].get_intitule() for ueI in self.ListeVoeux]
        return ListeVoeux , CompatibilityModel.modelGurobi.getObjective().getValue()
# modelGurobi.addConstr(quicksum((1./self.ListeCapacites[idGroup1-1])*modelGurobi.getVarByName(etu+"_%d"%self.id+"_%d"%idGroup1) for etu in self.EnsEtuInteresses) + quicksum((-1./self.ListeCapacites[idGroup2-1])*modelGurobi.getVarByName(etu+"_%d"%self.id+"_%d"%idGroup2) for etu in self.EnsEtuInteresses) >= -1.*CompatibilityModel.tauxEquilibre)
    def remise_a_zero(self):
        CompatibilityModel.EDT = [dict()] + [generer_model_dict_creneau(CompatibilityModel.nbMaxGroupeParUE) for i in range(0, CompatibilityModel.nbCreneauxParSemaine)]
        CompatibilityModel.ListeDesUEs = ["null"] + ["null"]*CompatibilityModel.nbUE
        CompatibilityModel.DictUEs = dict()

        CompatibilityModel.ListeDesEtudiants = ["null"]
        CompatibilityModel.ListeDesParcours = list()
        CompatibilityModel.ListeEffectifDesParcours = list()
        CompatibilityModel.ListeDesEffectifsCumules = list()
        CompatibilityModel.EnsIncompatibilites = set()
        CompatibilityModel.nbTotalIncompatibilites = 0
        CompatibilityModel.nbTotalIncompatibilitesVides = 0
        CompatibilityModel.nbInscriptionsSatisfaites = 0
        CompatibilityModel.ListedesVarY = list()
        #Jeudi 15
        CompatibilityModel.charge = 0
        CompatibilityModel.capaciteMaximale = 0
        #Jeudi 15
        CompatibilityModel.ListeDesEtudiantsParParcours = list()
        # for parcours, List in Compatibility.DictionnaireDesInsatisfactionsParParcours.items():
        #     print (parcours + " " + str(len(List)))
        CompatibilityModel.DictionnaireDesInsatisfactionsParParcours = dict() #MARDI 20 MARS :  non remise a zero du dictionnaire des insat par parcours idee connaitre les parcours qui rejette le plus
        CompatibilityModel.DictionnaireDistribUEInsatisfaitesParParcours = dict()

        CompatibilityModel.modelGurobi = Model("OPTIMISATION DES INSCRIPTIONS AUX UE (PAR DAK)")
# L = zip([1,2], [3,4])
# print L

cM = CompatibilityModel("edt.csv", ['mapsi','ares','model','noyau', 'pr'])
cM.traiter_voeu_anonyme(['aagb','il','lrc','mapsi', 'mogpl'])
# #
# # # cM = CompatibilityModel("edt.csv", [3,7,16])
# print (cM.resoudre())

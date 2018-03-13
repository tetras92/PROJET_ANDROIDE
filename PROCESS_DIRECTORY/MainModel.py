import numpy as np
import matplotlib.pyplot as plt
import csv
import copy
import os
from Analyses import *
import random
from gurobipy import *


#Modele d'un dictionnaire Creneau
def generer_model_dict_creneau(nbMaxGroupeParUE):
        modelDict = dict()
        modelDict[0] = set()
        for k in range(nbMaxGroupeParUE):
            modelDict[k+1] = set()
        return modelDict
#Fin Modele


class MainModel():

    #Les attributs
    # ListeDesEtudiants : liste des objets Etudiants
    # EDT : Liste de dictionnaires des creneaux
    # ModelGurobi : le modele Gurobi
    # DictUEs : dictionnaire des UEs; cle: intitule - valeur: Objet UE
    # ListeDesUEs : Liste des references vers les UEs indicees sur leur id
    # ListeDesParcours: Listes des parcours (des String)
    # nbMaxVoeuxParEtudiant : int
    # nbMaxGroupeParUE
    # nbMaxUEObligatoires/parcours
    # nbMaxUEConseillees/parcours
    # EnsIncompatibilites : ensemble des incompatibilites
# Par defaut
    nbMaxVoeuxParEtudiant = 5
    nbMaxGroupeParUE = 5
    nbMaxUEObligatoires = 3                      # REMPLACER PAR DES VARIABLES FACULTATIVES
    nbMaxUEConseillees = 5
    nbMaxCoursParUE = 2
    nbCreneauxParSemaine = 25
    nbUE = 21
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

    ListeDesEtudiantsParParcours = list()
    DictionnaireDesInsatisfactionsParParcours = dict()
    modelGurobi = Model("OPTIMISATION DES INSCRIPTIONS AUX UE (PAR DAK)")
    class Incompatibilite:
        def __init__(self, idUEI, idGroupK, idUEJ, idGroupL):
            """Definit une incompatiblite de type ((idUEI, idGroupK),(idUEJ, idGroupL))"""

            self.ueGroup1 = idUEI, idGroupK
            self.ueGroup2 = idUEJ, idGroupL
            self.ensEtuConcernes =  MainModel.ListeDesUEs[idUEI].getEnsEtu() & MainModel.ListeDesUEs[idUEJ].getEnsEtu()  #getEnsEtu  a definir dans UE
            self.vide = (len(self.ensEtuConcernes) == 0)
            MainModel.nbTotalIncompatibilites += 1
            if self.vide:
                MainModel.nbTotalIncompatibilitesVides += 1
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

        def __init__(self,csv_line):
            self.id =int(csv_line["id_ue"])
            self.intitule = csv_line["intitule"]
            self.nb_groupes = int(csv_line["nb_groupes"])
            self.ListeCapacites = [int(csv_line["capac"+str(i)]) for i in range(1,int(self.nb_groupes)+1)]
            self.EnsEtuInteresses = set()
            self.ListeCreneauxCours = [int(csv_line["cours"+str(i)]) for i in range(1,MainModel.nbMaxCoursParUE+1) if csv_line["cours"+str(i)] != ""]
            self.ListeCreneauxTdTme = [()]+[(csv_line["td"+str(i)],csv_line["tme"+str(i)]) for i in range(1,int(self.nb_groupes)+1)]
            self.ResumeDesAffectations = ["null"] + [set()]*self.nb_groupes
            self.nbInscrits = 0
            self.ListeNonInscrits = list()
            self.ListeEtudiantsGroupes = [list() for kk in range(self.nb_groupes+1)]

        def actualiseEDT(self):
            """MAJ de l'EDT"""
            for creneauCours in self.ListeCreneauxCours:
                MainModel.EDT[creneauCours][0].add(self.id)
            for gr_i in range(1, self.nb_groupes+1):
                creneauTdTme = self.ListeCreneauxTdTme[gr_i]
                try:
                    MainModel.EDT[int(creneauTdTme[0])][gr_i].add(self.id)      #Td
                    MainModel.EDT[int(creneauTdTme[1])][gr_i].add(self.id)      #tme
                except:
                    pass
        def get_id(self):
            return self.id

        def get_nb_groupes(self):
            return self.nb_groupes

        def ajouterEtuInteresses(self, name):
            self.EnsEtuInteresses.add(name)

        def getEnsEtu(self):
            return self.EnsEtuInteresses

        def ajouterContrainteCapaciteModelGurobi(self, modelGurobi):
            for idGroup in range(1, self.nb_groupes+1):
                modelGurobi.addConstr(quicksum(modelGurobi.getVarByName(etu+"_%d"%self.id+"_%d"%idGroup) for etu in self.EnsEtuInteresses) <= self.ListeCapacites[idGroup-1])
            modelGurobi.update()

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

        def __str__(self):
            """ Retourne la chaine representant une UE"""
            s = "UE {} ({}) :\n\tNombre de groupes : {}\n\tCapacite totale d'accueil: {}\n".format(self.intitule, self.id, self.nb_groupes, sum(self.ListeCapacites))
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
                s += str(idRelatif)+"("+MainModel.ListeDesParcours[int(parcours)]+") "
            s += "\n\tLes Inscrits:\n"
            for numGroup in range(1, len(self.ListeEtudiantsGroupes)):
                s += "\t\tGroupe {} [{}/{}] : ".format(numGroup, len(self.ListeEtudiantsGroupes[numGroup]), self.ListeCapacites[numGroup-1])
                for etu in self.ListeEtudiantsGroupes[numGroup]:
                    s += etu + " "
                s += "\n"
            s+= "\n\n"


            return s

    class Etudiant:
        def __init__(self,csv_line, parcours, indexParcours):
            self.idRelatif = int(csv_line["num"])
            self.parcours = parcours
            self.indexParcours = indexParcours
            self.ue_obligatoires = [MainModel.DictUEs[csv_line["oblig"+str(id)]].get_id() for id in range(1, MainModel.nbMaxUEObligatoires+1) if csv_line["oblig"+str(id)] != ""]
            self.ue_non_obligatoires = [MainModel.DictUEs[csv_line["cons"+str(id)]].get_id() for id in range(1, MainModel.nbMaxUEConseillees+1) if csv_line["cons"+str(id)] != ""]
            self.nombreDeVoeux = len(self.ue_obligatoires) + len(self.ue_non_obligatoires)
            self.varName = "x_{}_{}".format(self.indexParcours, self.idRelatif)
            self.ListeDesInscriptions = list()

        def gerer_variables_contraintes_ue_obligatoires(self,modelGurobi):
            objectif = modelGurobi.getObjective()

            for id_ue in self.ue_obligatoires:
                var = modelGurobi.addVar(vtype=GRB.BINARY, lb=0, name="y_%d"%self.indexParcours+"_%d"%self.idRelatif+"_%d"%id_ue)
                MainModel.ListedesVarY.append("y_{}_{}_{}".format(self.indexParcours, self.idRelatif, id_ue))
                contrainte = LinExpr()
                for num_group in range(1, MainModel.ListeDesUEs[id_ue].get_nb_groupes()+1):
                    contrainte += modelGurobi.addVar(vtype=GRB.BINARY, lb=0, name=self.varName+"_%d"%id_ue+"_%d"%num_group)
                contrainte -= var

                objectif += var
                modelGurobi.addConstr(var , GRB.EQUAL, 1)   #y_i_j = 1
                modelGurobi.addConstr(contrainte, GRB.EQUAL, 0)

            modelGurobi.setObjective(objectif,GRB.MAXIMIZE) # NE PEUt-ON PAS S'EN PASSER
            modelGurobi.update()

        def gerer_variables_contraintes_ue_non_obligatoires(self, modelGurobi):
            objectif = modelGurobi.getObjective()

            for id_ue in self.ue_non_obligatoires:
                var = modelGurobi.addVar(vtype=GRB.BINARY, lb=0, name="y_%d"%self.indexParcours+"_%d"%self.idRelatif+"_%d"%id_ue)
                MainModel.ListedesVarY.append("y_{}_{}_{}".format(self.indexParcours, self.idRelatif, id_ue))
                contrainte = LinExpr()
                for num_group in range(1, MainModel.ListeDesUEs[id_ue].get_nb_groupes()+1):
                    contrainte += modelGurobi.addVar(vtype=GRB.BINARY, lb=0, name=self.varName+"_%d"%id_ue+"_%d"%num_group)
                contrainte -= var

                objectif += var

                #VERIFIER LES CONTRAINTES DU MODELES
                modelGurobi.addConstr(contrainte, GRB.EQUAL, 0)

            modelGurobi.setObjective(objectif,GRB.MAXIMIZE) # NE PEUt-ON PAS S'EN PASSER
            modelGurobi.update()

        def enregistrer_interet_pour_UE(self):
            for ue in self.ue_non_obligatoires + self.ue_obligatoires:
                MainModel.ListeDesUEs[ue].ajouterEtuInteresses(self.varName)

        def get_nombreDeVoeux(self):
            return self.nombreDeVoeux

        def get_index_parcours(self):
            return  self.indexParcours

        def get_varName(self):
            return self.varName

        def entrer_inscription(self, ue, numeroGroup):
            if numeroGroup != 0:  #numeroGroup 0 signifie non accepte
                    chaine = MainModel.ListeDesUEs[ue].get_intitule()+str(numeroGroup)
                    MainModel.ListeDesUEs[ue].inscrire(str(self), numeroGroup)
            else:
                    chaine = MainModel.ListeDesUEs[ue].get_intitule()+"X"

                    pattern = ""

                    for ue in self.ue_obligatoires + self.ue_non_obligatoires:
                        pattern += MainModel.ListeDesUEs[ue].get_intitule() + " "

                    MainModel.DictionnaireDesInsatisfactionsParParcours[self.parcours].add((str(self),pattern))
            if ue in self.ue_obligatoires:
                self.ListeDesInscriptions = [chaine] + self.ListeDesInscriptions
            else:
                self.ListeDesInscriptions.append(chaine)

        def enregistrer_affectation(self, file):
            file.write(str(self.idRelatif)+" ")
            for aff in self.ListeDesInscriptions:
                file.write(aff + " ")
            file.write("\n")

        def __str__(self):
            s = str(self.idRelatif)+"("+MainModel.ListeDesParcours[self.indexParcours]+")"
            return s

    # DEBUT MAINMODEL





    def __init__(self, dossierVoeux, fileUE):
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
        modelDict = dict()
        modelDict[0] = set()
        for k in range(self.nbMaxGroupeParUE):
            modelDict[k+1] = set()
        #Fin Modele

        #TRAITEMENT UE : GENERATION DE L'EDT ET DES OBJETS UE
        f_ue = open(fileUE)
        data = csv.DictReader(f_ue)
        for ligneUE in data:
            currentUE = MainModel.UE(ligneUE)
            currentUE.actualiseEDT()
            MainModel.ListeDesUEs[currentUE.get_id()] = currentUE             #Rajout a la listeUe
            MainModel.DictUEs[currentUE.intitule] = currentUE                  #Rajout au DictUe

            #NETTOYER EDT
        for creneau in range(1, len(MainModel.EDT)):
            dictCopy = MainModel.EDT[creneau].copy()
            for id in dictCopy:
                if len(dictCopy[id]) == 0:
                    del MainModel.EDT[creneau][id]
            # FIN NETTOYAGE EDT

        #FIN TRAITEMENT UE

        #TRAITEMENT VOEUX ETUDIANTS
        indexParcours = 0
        for fichierVoeux in os.listdir(dossierVoeux):
            parcours = fichierVoeux.split('.')[1]

            #INITIALISATION DICTIONNAIRE DES INSATISFACTIONS PAR PARCOURS
            MainModel.DictionnaireDesInsatisfactionsParParcours[parcours] = set()

            path = dossierVoeux+"/"+fichierVoeux
            f_voeux = open(path)
            data = csv.DictReader(f_voeux)
            effectif = 0
            for ligneEtu in data:
                currentEtu = MainModel.Etudiant(ligneEtu, parcours, indexParcours)
                effectif += 1
                MainModel.ListeDesEtudiants.append(currentEtu)
                #rajout des variables et contraintes s'appliquant a currentEtu
                currentEtu.gerer_variables_contraintes_ue_non_obligatoires(MainModel.modelGurobi)
                currentEtu.gerer_variables_contraintes_ue_obligatoires(MainModel.modelGurobi)
                #Enregistrement de l'interet pour l'ensemble de ses UE
                currentEtu.enregistrer_interet_pour_UE()
            MainModel.ListeEffectifDesParcours.append(effectif)
            MainModel.ListeDesParcours.append(parcours)
            indexParcours += 1

        MainModel.ListeDesEffectifsCumules = [0] + [val for val in MainModel.ListeEffectifDesParcours]
        for l in range(1, len(MainModel.ListeEffectifDesParcours)):
            MainModel.ListeDesEffectifsCumules[l] += MainModel.ListeDesEffectifsCumules[l-1]

        #FIN TRAITEMENT VOEUX ETUDIANTS

        #GERER LES INCOMPATIBILITES
        for creneauId in range(1, len(MainModel.EDT)):
            #incompatibilites groupesTdTme
            dictCreneau = MainModel.EDT[creneauId]

            for (idGroup1, EnsUE1) in dictCreneau.items():
                if idGroup1 != 0:
                    #Incompatibilite intra meme numeroGroup
                    for ueIntra1 in EnsUE1:
                        for ueIntra2 in EnsUE1:       #EnsUE2:  CORRECTION
                            if ueIntra1 < ueIntra2:
                                currentIncompatibilite = MainModel.Incompatibilite(ueIntra1, idGroup1, ueIntra2, idGroup1)
                                #Instruction Rajout au model
                                currentIncompatibilite.ajouterContrainteModeleGurobi(MainModel.modelGurobi)
                                #Fin
                                # if random.random() <= 0.5:
                                #     print(currentIncompatibilite)
                                MainModel.EnsIncompatibilites.add(currentIncompatibilite)
                #Fin Incompatibilite intra meme numeroGroup
                for (idGroup2, EnsUE2) in dictCreneau.items():
                    if idGroup1 > 0 and idGroup1 < idGroup2: # CONVENTION IdGroup1 < IdGroup2:
                        for ue1 in EnsUE1:
                            for ue2 in EnsUE2:
                                if ue1 != ue2: #l'incompatibilite entre deux groupes d'une meme ue est deja gere
                                    currentIncompatibilite = MainModel.Incompatibilite(ue1, idGroup1, ue2, idGroup2)
                                    #Instruction Rajout au model
                                    currentIncompatibilite.ajouterContrainteModeleGurobi(MainModel.modelGurobi)
                                    #Fin
                                    MainModel.EnsIncompatibilites.add(currentIncompatibilite)

            #Incompatibilite intra cours meme creneau + incompatibilite inter cours et td tme
            try:
                for ue1 in dictCreneau[0]:
                    #Incompatibilite intra cours meme creneau
                    nb_group_ue1 = MainModel.ListeDesUEs[ue1].get_nb_groupes()
                    for ue2 in dictCreneau[0]:
                        if ue1 < ue2:

                            nb_group_ue2 = MainModel.ListeDesUEs[ue2].get_nb_groupes() #CORRECTION ...  ListeDesUEs[ue2] au lieu de ListeDesUEs[ue1]
                            for idGroup1 in range(1, nb_group_ue1+1):
                                for idGroup2 in range(1, nb_group_ue2):
                                    currentIncompatibilite = MainModel.Incompatibilite(ue1, idGroup1, ue2, idGroup2)
                                    #Instruction Rajout au model
                                    currentIncompatibilite.ajouterContrainteModeleGurobi(MainModel.modelGurobi)
                                    #Fin
                                    # if random.random() <= 0.5:
                                    #     print(currentIncompatibilite)
                                    MainModel.EnsIncompatibilites.add(currentIncompatibilite)

                    # incompatibilite inter cours et td tme
                    for (idGroupTdTme, EnsUE2) in dictCreneau.items():
                        if idGroupTdTme > 0:
                            for ue2 in EnsUE2:
                                for idGroup1 in range(1, nb_group_ue1+1):
                                    currentIncompatibilite = MainModel.Incompatibilite(ue1, idGroup1, ue2, idGroupTdTme)
                                    #Instruction Rajout au model
                                    currentIncompatibilite.ajouterContrainteModeleGurobi(MainModel.modelGurobi)
                                    #Fin
                                    MainModel.EnsIncompatibilites.add(currentIncompatibilite)

            except:
                pass

        #FIN GESTION DES INCOMPATIBILITES
        # GERER LES CONTRAINTES DE CAPACITE
        for UE in MainModel.ListeDesUEs[1:]:
            UE.ajouterContrainteCapaciteModelGurobi(MainModel.modelGurobi)
        #FIN CONTRAINTES DE CAPACITE


    def resoudre(self):
        # print (MainModel.modelGurobi.getObjective())

        MainModel.modelGurobi.optimize()

        for varName in MainModel.ListedesVarY:
            if MainModel.modelGurobi.getVarByName(varName).x == 1:
                MainModel.nbInscriptionsSatisfaites += 1
                parcours, idRelatif, ue = varName[2:].split('_')
                MainModel.ListeDesUEs[int(ue)].ajouterUnInscrit()
                currentEtudiant = MainModel.ListeDesEtudiants[MainModel.ListeDesEffectifsCumules[int(parcours)] + int(idRelatif)]
                numGroup = 1
                # print(currentEtudiant)
                # print(parcours, idRelatif, ue)

                while MainModel.modelGurobi.getVarByName(currentEtudiant.get_varName()+"_%d"%int(ue)+"_%d"%numGroup).x == 0:
                    # print(numGroup)
                    numGroup += 1
                currentEtudiant.entrer_inscription(int(ue), numGroup)
            else:
                parcours, idRelatif, ue = varName[2:].split('_')
                MainModel.ListeDesUEs[int(ue)].signalerNonInscrit(parcours, idRelatif)
                currentEtudiant = MainModel.ListeDesEtudiants[MainModel.ListeDesEffectifsCumules[int(parcours)] + int(idRelatif)]
                currentEtudiant.entrer_inscription(int(ue), 0)
        try:
            os.mkdir("../AFFECTATIONS PAR PARCOURS")
        except:
            pass
        for parcours in range(len(MainModel.ListeDesParcours)):
            f = open("../AFFECTATIONS PAR PARCOURS/affectations.{}".format(MainModel.ListeDesParcours[parcours]), "w")
            f.write("LES AFFECTATIONS\n")
            for idRelatif in range(1, MainModel.ListeEffectifDesParcours[parcours]+1):
                MainModel.ListeDesEtudiants[MainModel.ListeDesEffectifsCumules[parcours] + int(idRelatif)].enregistrer_affectation(f)
            f.close()

            # [37, 12, 51, 27, 59, 25, 48, 33, 50]
            # [0, 37, 49, 100, 127, 186, 211, 259, 292, 50]

    def strDictionnaireDesInsatisfactions(self):
        s = ""
        # TO BE CONTINUED
    def __str__(self):
        """Affiche les UES du Modele"""
        s = ""
        for intitule,ue in MainModel.DictUEs.items():
            s += str(ue)

        s += "\n\nEDT:\n{}\n\n".format(MainModel.EDT)

        s += str(MainModel.ListeDesParcours) # A GeRER PLUS FINEMENT ET ELEGAMMENT
        s += "\n" + str(MainModel.ListeEffectifDesParcours)
        s += "\n" + str(MainModel.ListeDesEffectifsCumules)
        # print(MainModel.EDT)

        s += "\n****Nombre total d'incompatibilites: {}****\n****Nombre total d'incompatibilites vides: {}****\n\n".format(MainModel.nbTotalIncompatibilites, MainModel.nbTotalIncompatibilitesVides)
        s += "Nombre Total d'inscriptions a satisfaire : {} \n".format(len(MainModel.ListedesVarY))
        proportionSatisfaction = round(100.0*MainModel.nbInscriptionsSatisfaites/len(MainModel.ListedesVarY),2)
        s += "Nombre d'inscriptions satisfaites : {} soit {}%\n".format(MainModel.nbInscriptionsSatisfaites, proportionSatisfaction)
        s += "Detail des inscriptions non satisfaites : {}\n".format(str(MainModel.DictionnaireDesInsatisfactionsParParcours))
        return s

    #     STOP HERE



    
# m = MainModel("../VOEUX", "edt.csv")
m = MainModel("RAND_VOEUX1", "edt.csv")
m.resoudre()

analyses = Analyses(m)
f = open("R1inscription2017_2018.txt", "w")
# f = open("inscription2017_2018.txt", "w")

f.write(str(m))
f.write("\n\n"+str(analyses))
f.close()
# print(m)
# print(analyses)

import numpy as np
import matplotlib.pyplot as plt
import csv
import copy
import os
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

    ListeDesEtudiants = list()
    ListeDesParcours = list()
    ListeEffectifDesParcours = list()

    modelGurobi = Model("OPTIMISATION DES INSCRIPTIONS AUX UE (PAR DAK)")
    class Incompatibilite:
        def __init__(self, idUEI, idGroupK, idUEJ, idGroupL):
            """Definit une incompatiblite de type ((idUEI, idGroupK),(idUEJ, idGroupL))"""

            self.ueGroup1 = idUEI, idGroupK
            self.ueGroup2 = idUEJ, idGroupL
            self.ensEtuConcernes =  MainModel.ListeDesUEs[idUEI].getEnsEtu() & MainModel.ListeDesUEs[idUEJ].getEnsEtu()  #getEnsEtu  a definir dans UE

        def __str__(self):
            """Retourne la chaine d'affichage de l'incompatibilite et l'effectif des etudiants concernes"""
            s = "Incompatibilite entre l'UE/Groupe {} et l'UE/Groupe {}\n\tNombre d'etudiants concernes: {}\n\n".format(self.ueGroup1, self.ueGroup2, len(self.ensEtuConcernes))

            return s



    class UE:

        def __init__(self,csv_line):
            self.id =int(csv_line["id_ue"])
            self.intitule = csv_line["intitule"]
            self.nb_groupes = int(csv_line["nb_groupes"])
            self.ListeCapacites = [int(csv_line["capac"+str(i)]) for i in range(1,int(self.nb_groupes)+1)]
            self.EnsEtuInteresses = set()
            self.ListeCreneauxCours = [int(csv_line["cours"+str(i)]) for i in range(1,MainModel.nbMaxCoursParUE+1) if csv_line["cours"+str(i)] != ""]
            self.ListeCreneauxTdTme = [()]+[(csv_line["td"+str(i)],csv_line["tme"+str(i)]) for i in range(1,int(self.nb_groupes)+1)]

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


        def __str__(self):
            """ Retourne la chaine representant une UE"""
            s = "UE {} ({}) :\n\tNombre de groupes : {}\n\tCapacite totale d'accueil: {}\n".format(self.intitule, self.id, self.nb_groupes, sum(self.ListeCapacites))
            #CRENEAUX
            s += "\tLes Creneaux\n\t"
            for cours in self.ListeCreneauxCours:
                s += "\tCours: {}\n\t".format(cours)

            for i in range(1, len(self.ListeCreneauxTdTme)):
                td, tme = self.ListeCreneauxTdTme[i]
                s += "\tTD {} : {}\n\t".format(i, td)
                s += "\tTME {} : {}\n\t".format(i, tme)
            s += "\n"

            return s

    class Etudiant:
        def __init__(self,csv_line, parcours, indexParcours):
            self.idRelatif = int(csv_line["num"])
            self.parcours = parcours
            self.indexParcours = indexParcours
            self.ue_obligatoires = [MainModel.DictUEs[csv_line["oblig"+str(id)]].get_id() for id in range(1, MainModel.nbMaxUEObligatoires+1) if csv_line["oblig"+str(id)] != ""]
            self.ue_non_obligatoires = [MainModel.DictUEs[csv_line["cons"+str(id)]].get_id() for id in range(1, MainModel.nbMaxUEConseillees+1) if csv_line["cons"+str(id)] != ""]
            self.varName = "x_{}_{}".format(self.indexParcours, self.idRelatif)


        def gerer_variables_contraintes_ue_obligatoires(self,modelGurobi):
            objectif = modelGurobi.getObjective()

            for id_ue in self.ue_obligatoires:
                var = modelGurobi.addVar(vtype=GRB.BINARY, lb=0, name="y_%d"%self.indexParcours+"_%d"%self.idRelatif+"_%d"%id_ue)
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
                contrainte = LinExpr()
                for num_group in range(1, MainModel.ListeDesUEs[id_ue].get_nb_groupes()+1):
                    contrainte += modelGurobi.addVar(vtype=GRB.BINARY, lb=0, name=self.varName+"_%d"%id_ue+"_%d"%num_group)
                contrainte -= var
                objectif += var

                modelGurobi.addConstr(contrainte, GRB.EQUAL, 0)

            modelGurobi.setObjective(objectif,GRB.MAXIMIZE) # NE PEUt-ON PAS S'EN PASSER
            modelGurobi.update()

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
            MainModel.ListeDesParcours.append(parcours)
            indexParcours += 1

    def __str__(self):
        """Affiche les UES du Modele"""
        s = ""
        for intitule,ue in MainModel.DictUEs.items():
            s += str(ue)

        s += "\n\nEDT:\n{}\n\n".format(MainModel.EDT)

        s += str(MainModel.ListeDesParcours) # A GeRER PLUS FINEMENT ET ELEGAMMENT
        # print(MainModel.EDT)
        return s

    #     STOP HERE



    
m = MainModel("../VOEUX", "edt.csv")
print(m)

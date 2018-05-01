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
    tauxEquilibre = 0.10
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
    objectif1 = LinExpr()
    objectif2 = LinExpr()
    # modelGurobi.NumObj = 2
    # modelGurobi.setObjectiveN(objectif1,0,0)
    # modelGurobi.setObjectiveN(objectif2,1,1)
    # modelGurobi.modelSense = -1
    # self.model.NumObj = 2
# self.model.setObjectiveN(obj1,0,0)
# self.model.setObjectiveN(obj2,1,1)
# self.model.modelSense= -1
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
            self.ensEtuConcernes =  MainModel.ListeDesUEs[idUEI].getEnsEtu() & MainModel.ListeDesUEs[idUEJ].getEnsEtu()  #L'ensemble des etudiants auxquels s'applique l'incompatibilite (Etudiant sous la forme x_Parcous_idRelatif (des strings))
            self.vide = (len(self.ensEtuConcernes) == 0)    #Un booleen
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
        """Classe definissant une UE"""
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
            self.capaciteTotale = sum(self.ListeCapacites)
            self.equilibre = True

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
                    modelGurobi.addConstr(quicksum((1./self.ListeCapacites[idGroup1-1])*modelGurobi.getVarByName(etu+"_%d"%self.id+"_%d"%idGroup1) for etu in self.EnsEtuInteresses) + quicksum((-1./self.ListeCapacites[idGroup2-1])*modelGurobi.getVarByName(etu+"_%d"%self.id+"_%d"%idGroup2) for etu in self.EnsEtuInteresses) <= MainModel.tauxEquilibre)
                    modelGurobi.addConstr(quicksum((1./self.ListeCapacites[idGroup1-1])*modelGurobi.getVarByName(etu+"_%d"%self.id+"_%d"%idGroup1) for etu in self.EnsEtuInteresses) + quicksum((-1./self.ListeCapacites[idGroup2-1])*modelGurobi.getVarByName(etu+"_%d"%self.id+"_%d"%idGroup2) for etu in self.EnsEtuInteresses) >= -1.*MainModel.tauxEquilibre)
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
            # print(self.intitule)
            for idL1 in range(1, self.nb_groupes):
                for idL2 in range(idL1+1, self.nb_groupes+1):
                    # print("groupe1", idL1, "groupe2", idL2)
                    difference = abs(1.0*len(self.ListeEtudiantsGroupes[idL1])/(1.0*self.ListeCapacites[idL1-1])- 1.0*len(self.ListeEtudiantsGroupes[idL2])/(1.0*self.ListeCapacites[idL2-1]))

                    if difference > MainModel.tauxEquilibre:

                        # print difference
                        self.equilibre = False


            #AJOUTER LA CARACTERISTIQUE DE COULEUR PASTILLE L'IDEE D'UN MAX
        def __str__(self):
            """ Retourne la chaine representant une UE"""
            s = "UE {} ({}) :\n\tNombre de groupes : {}\n\tCapacite totale d'accueil: {}\n\t".format(self.intitule, self.id, self.nb_groupes, sum(self.ListeCapacites))
            # equil = ["Oui", "Non"]
            if self.equilibre:
                s += "Equilibre? : Oui\n"
            else:
                s += "Equilibre? : Non\n"
            # s += "Equilibre? : {}\n".format(self.equilibre)
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
        """ Classe representant un etudiant"""
        def __init__(self,csv_line, parcours, indexParcours):
            self.idRelatif = int(csv_line["num"])
            self.parcours = parcours
            self.indexParcours = indexParcours
            self.ue_obligatoires = [MainModel.DictUEs[csv_line["oblig"+str(id)]].get_id() for id in range(1, MainModel.nbMaxUEObligatoires+1) if csv_line["oblig"+str(id)] != ""]
            self.ue_non_obligatoires = [MainModel.DictUEs[csv_line["cons"+str(id)]].get_id() for id in range(1, MainModel.nbMaxUEConseillees+1) if csv_line["cons"+str(id)] != ""]
            # **
            # L = MainModel.DDecisionEtuUE[parcours] + self.ue_non_obligatoires
            # L.sort()
            # MainModel.DDecisionEtuUE[parcours] = L
            # ** bincount

            self.nombreDeVoeux = len(self.ue_obligatoires) + len(self.ue_non_obligatoires)

            # MainModel.DNbrUeContrat[parcours].append(self.nombreDeVoeux)

            self.varName = "x_{}_{}".format(self.indexParcours, self.idRelatif)
            self.ListeDesInscriptions = list()


        def gerer_variables_contraintes_ue_obligatoires(self,modelGurobi):
            """ajoute les contraintes relatives aux ue obligatoires"""
            # objectif = modelGurobi.getObjective()

            for id_ue in self.ue_obligatoires:
                var = modelGurobi.addVar(vtype=GRB.BINARY, lb=0, name="y_%d"%self.indexParcours+"_%d"%self.idRelatif+"_%d"%id_ue)
                MainModel.ListedesVarY.append("y_{}_{}_{}".format(self.indexParcours, self.idRelatif, id_ue))
                contrainte = LinExpr()
                for num_group in range(1, MainModel.ListeDesUEs[id_ue].get_nb_groupes()+1):
                    contrainte += modelGurobi.addVar(vtype=GRB.BINARY, lb=0, name=self.varName+"_%d"%id_ue+"_%d"%num_group)
                contrainte -= var

                # objectif += var
                MainModel.objectif1 += var

                modelGurobi.addConstr(var , GRB.EQUAL, 1)   #y_i_j = 1
                modelGurobi.addConstr(contrainte, GRB.EQUAL, 0)

            # modelGurobi.setObjective(objectif,GRB.MAXIMIZE) # NE PEUt-ON PAS S'EN PASSER
            modelGurobi.update()

        def gerer_variables_contraintes_ue_non_obligatoires(self, modelGurobi):
            """ajoute les contraintes relatives aux ue non obligatoires"""
            # objectif = modelGurobi.getObjective()
            varN = modelGurobi.addVar(vtype=GRB.BINARY, lb=0, name="n_%d"%self.indexParcours+"_%d"%self.idRelatif)
            MainModel.objectif2 += varN

            ListeCouranteVarYij = list()
            for id_ue in self.ue_non_obligatoires:
                var = modelGurobi.addVar(vtype=GRB.BINARY, lb=0, name="y_%d"%self.indexParcours+"_%d"%self.idRelatif+"_%d"%id_ue)
                ListeCouranteVarYij.append(var)
                MainModel.ListedesVarY.append("y_{}_{}_{}".format(self.indexParcours, self.idRelatif, id_ue))
                contrainte = LinExpr()
                for num_group in range(1, MainModel.ListeDesUEs[id_ue].get_nb_groupes()+1):
                    contrainte += modelGurobi.addVar(vtype=GRB.BINARY, lb=0, name=self.varName+"_%d"%id_ue+"_%d"%num_group)
                contrainte -= var

                # objectif += var
                MainModel.objectif1 += var
                #VERIFIER LES CONTRAINTES DU MODELES
                modelGurobi.addConstr(contrainte, GRB.EQUAL, 0)
            #contrainte ETUDIANT ENTIEREMENT SATISFAIT
            # if ListeCouranteVarYij != []:
            modelGurobi.addConstr(quicksum(varYij for varYij in ListeCouranteVarYij) >= len(self.ue_non_obligatoires)*varN)
            # modelGurobi.setObjective(objectif,GRB.MAXIMIZE) # NE PEUt-ON PAS S'EN PASSER
            modelGurobi.update()

        def enregistrer_interet_pour_UE(self):
            for ue in self.ue_non_obligatoires + self.ue_obligatoires:
                if ue == 11:
                    MainModel.count += 1
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
                    ListeTrieeDesUE = self.ue_obligatoires + self.ue_non_obligatoires
                    ListeTrieeDesUE.sort()
                    # print(ListeTrieeDesUE)
                    for ue in ListeTrieeDesUE:
                        pattern += MainModel.ListeDesUEs[ue].get_intitule() + " "

                    MainModel.DictionnaireDesInsatisfactionsParParcours[self.parcours].append([str(self),ListeTrieeDesUE]) #remplacer ListeTrieeDesUEs par pattern if pertinent
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
            s = str(self.idRelatif)+"("+MainModel.ListeDesParcours[self.indexParcours]+")"
            return s

    # DEBUT MAINMODEL





    def __init__(self, dossierVoeux, fileUE, equilibre=False):
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
        # if not (MainModel.edtInitialise): MainModel.edtInitialise = True



        f_ue = open(fileUE)
        data = csv.DictReader(f_ue)
        for ligneUE in data:
            currentUE = MainModel.UE(ligneUE) #Generation de l'objet UE
            currentUE.actualiseEDT()
            MainModel.ListeDesUEs[currentUE.get_id()] = currentUE             #Rajout a la listeUe
            MainModel.DictUEs[currentUE.intitule] = currentUE                  #Rajout au DictUe

            #NETTOYER EDT : supprimer les associations de numeros de groupe avec des ensembles vides
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


            # try: #POUR EVITER LES ERREURS DE SPLIT SUR LE DOSSIER DE VOEUX PAR PARCOURS
            parcours = fichierVoeux.split('.')[1]
            path = dossierVoeux+"/"+fichierVoeux
            f_voeux = open(path)
            data = csv.DictReader(f_voeux)
            # except:
            #     pass

            #INITIALISATION DICTIONNAIRE DES INSATISFACTIONS PAR PARCOURS
            # if not(MainModel.edtInitialise):
            MainModel.DictionnaireDesInsatisfactionsParParcours[parcours] = list()#set()
            # MainModel.DDecisionEtuUE[parcours] = list() #**


            # MainModel.DNbrUeContrat[parcours] = list()



            effectif = 0
            for ligneEtu in data:
                currentEtu = MainModel.Etudiant(ligneEtu, parcours, indexParcours) #generation de l'objet etudiant
                effectif += 1
                MainModel.ListeDesEtudiants.append(currentEtu)
                #rajout des variables et contraintes s'appliquant a currentEtu
                currentEtu.gerer_variables_contraintes_ue_non_obligatoires(MainModel.modelGurobi)
                currentEtu.gerer_variables_contraintes_ue_obligatoires(MainModel.modelGurobi)
                #Enregistrement de l'interet pour l'ensemble de ses UE
                currentEtu.enregistrer_interet_pour_UE()
            MainModel.ListeEffectifDesParcours.append(effectif)                     #STOCKAGE DE L'EFFECTIF DU PARCOURS
            MainModel.ListeDesParcours.append(parcours)
            indexParcours += 1
        MainModel.edtInitialise = True
         #CALCUL DES EFFECTIFS CUMULES
        MainModel.ListeDesEffectifsCumules = [0] + [val for val in MainModel.ListeEffectifDesParcours]
        for l in range(1, len(MainModel.ListeEffectifDesParcours)):
            MainModel.ListeDesEffectifsCumules[l] += MainModel.ListeDesEffectifsCumules[l-1]
         #FIN CALCUL DES EFFECTIFS CUMULES
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

        #GERER LES CONTRAINTES D'EQUILIBRAGE EFFECTIF DE GROUPE
        if equilibre :
            for UE in MainModel.ListeDesUEs[1:]:
                UE.ajouterContraintesEquilibre(MainModel.modelGurobi)
        #FIN GESTION DES CONTRAINTES D'EQUILIBRAGE EFFECTIF DE GROUPE



    def resoudre(self, Yprior=True):
        # print (MainModel.modelGurobi.getObjective())
        self.calculer_charge()
        MainModel.modelGurobi.NumObj = 2
        if Yprior:
            MainModel.modelGurobi.setObjectiveN(MainModel.objectif1,0,10)
            MainModel.modelGurobi.setObjectiveN(MainModel.objectif2,1,1)
        else:
            MainModel.modelGurobi.setObjectiveN(MainModel.objectif1,0,0)
            MainModel.modelGurobi.setObjectiveN(MainModel.objectif2,1,1)


        # MainModel.modelGurobi.setObjective(MainModel.objectif1, GRB.MAXIMIZE)
        # MainModel.modelGurobi.setObjective(MainModel.modelGurobi.getObjective(),GRB.MAXIMIZE)
        MainModel.modelGurobi.setParam( 'OutputFlag', False )
        MainModel.modelGurobi.modelSense = -1
        MainModel.modelGurobi.optimize()
        if Yprior:
            MainModel.modelGurobi.setParam(GRB.Param.ObjNumber, 0)
            print "Somme Yij", MainModel.modelGurobi.ObjNVal
            MainModel.modelGurobi.setParam(GRB.Param.ObjNumber, 1)
            print "Somme Ni", MainModel.modelGurobi.ObjNVal
        else:
            MainModel.modelGurobi.setParam(GRB.Param.ObjNumber, 0)
            print "Somme Yij", MainModel.modelGurobi.ObjNVal
            MainModel.modelGurobi.setParam(GRB.Param.ObjNumber, 1)
            print "Somme Ni", MainModel.modelGurobi.ObjNVal
            print "----------------------------------------------"



        for varName in MainModel.ListedesVarY:
            # print (varName)
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



        MainModel.proportionSatisfaction = round(100.0*MainModel.nbInscriptionsSatisfaites/len(MainModel.ListedesVarY),2)
        try:
            os.mkdir("../AFFECTATIONS PAR PARCOURS")
            affectationDirectory = "/Vrac/DAK/RAND_VOEUX"+str(MainModel.idModel)+"_AFFECTATIONS PAR PARCOURS"
            # os.mkdir(affectationDirectory)
        except:
            pass
        for parcours in range(len(MainModel.ListeDesParcours)):
            f = open("../AFFECTATIONS PAR PARCOURS/affectations.{}".format(MainModel.ListeDesParcours[parcours]), "w")
            # f = open("/Vrac/DAK/RAND_VOEUX"+str(MainModel.idModel)+"_AFFECTATIONS PAR PARCOURS/affectations.{}".format(MainModel.ListeDesParcours[parcours]), "w")
            f.write("LES AFFECTATIONS\n")
            for idRelatif in range(1, MainModel.ListeEffectifDesParcours[parcours]+1):
                MainModel.ListeDesEtudiants[MainModel.ListeDesEffectifsCumules[parcours] + int(idRelatif)].enregistrer_affectation(f)
            f.close()

        MainModel.idModel += 1
        #VERIFIER L'EQUILIBRE DES GROUPES
        for UE in MainModel.ListeDesUEs[1:]:
            # print UE.intitule
            UE.set_equilibre()
        #FIN VERIFICATION EQUILIBRE
        return MainModel.charge, MainModel.proportionSatisfaction
            # [37, 12, 51, 27, 59, 25, 48, 33, 50]
            # [0, 37, 49, 100, 127, 186, 211, 259, 292, 342]

    def strDictionnaireDesInsatisfactions(self):
        ListeParcoursStr = list()
        ListeNbInsatisfaction = list()
        ListeDistrUEInsatisfParParcours = list()
        s = ""
        def concatener_ue_insatisfaites(L):
            R = [ue for LP in L for ue in LP]
            R.sort()
            return R

        for parcours, List in MainModel.DictionnaireDesInsatisfactionsParParcours.items():
            ListeParcoursStr.append(parcours)
            ListeNbInsatisfaction.append(len(List))
            R = concatener_ue_insatisfaites([LP[1] for LP in List])
            ListeDistrUEInsatisfParParcours.append(R)
            s += "{} : {} |".format(parcours, str(len(List)))

        # print(ListeDistrUEInsatisfParParcours)            LA DISTRIBUTION DES INSATISFACTIONS A AFFICHER


        return s[:-1]
    def strListeDesInsatisfactionsParUE(self):
        s = ""
        for ue_id in range(1, len(MainModel.ListeDesUEs)):
            if MainModel.ListeDesUEs[ue_id].get_nbInscrits() != MainModel.ListeDesUEs[ue_id].get_nbInteresses():
                if MainModel.ListeDesUEs[ue_id].get_nbInscrits() == MainModel.ListeDesUEs[ue_id].get_capaciteTotale():
                    s += "**"
                s += MainModel.ListeDesUEs[ue_id].get_intitule()+" ({})|".format(MainModel.ListeDesUEs[ue_id].get_nbInteresses() - MainModel.ListeDesUEs[ue_id].get_nbInscrits())
        return s[:-1]


    def calculer_capaciteMaximale(self):
        capMax = 0
        for ue in range(1, len(MainModel.ListeDesUEs)):
            # print (ue, MainModel.ListeDesUEs[ue])
            capMax += sum(MainModel.ListeDesUEs[ue].get_ListeDesCapacites())
        MainModel.capaciteMaximale = capMax


    def calculer_charge(self):
        nombreDemandesInscriptions = len(MainModel.ListedesVarY)
        self.calculer_capaciteMaximale()
        MainModel.charge = round(100.0*nombreDemandesInscriptions/MainModel.capaciteMaximale,2)

    def __str__(self):
        """Affiche les UES du Modele"""
        s = "**********OPTIMISATION DES INSCRIPTIONS AUX UE (PAR DAK)**********\n\n"
        s += "\nNombre total d'incompatibilites: {}\nNombre total d'incompatibilites vides: {}\n\n".format(MainModel.nbTotalIncompatibilites, MainModel.nbTotalIncompatibilitesVides)
        s += "Nombre Total d'inscriptions a satisfaire : {} \n".format(len(MainModel.ListedesVarY))
        s += "Nombre Maximal d'inscriptions pouvant etre satisfaites : {} \n".format(MainModel.capaciteMaximale)
        s += "Charge : {}% \nDesequilibre maximal autorise : {} %\n\n\t\t\t*LES RESULTATS D'AFFECTATION*\n".format(MainModel.charge, MainModel.tauxEquilibre*100)

        # proportionSatisfaction = round(100.0*MainModel.nbInscriptionsSatisfaites/len(MainModel.ListedesVarY),2)
        s += "Nombre d'inscriptions satisfaites : {} soit {}%\n".format(MainModel.nbInscriptionsSatisfaites, MainModel.proportionSatisfaction)
        s += "Detail des inscriptions non satisfaites : \n\t\tNombre de demandes non satisfaites par parcours : {}\n".format(self.strDictionnaireDesInsatisfactions())
        s += "\t\tNombre de demandes non satisfaites par UE (**Saturee): {}\n".format(self.strListeDesInsatisfactionsParUE())
        s += "\n\t\t\t*DETAIL DES AFFECTATIONS PAR UE*\n\n"


        for intitule,ue in MainModel.DictUEs.items():
            s += str(ue)


        return s
    def remise_a_zero(self):
        MainModel.EDT = [dict()] + [generer_model_dict_creneau(MainModel.nbMaxGroupeParUE) for i in range(0, MainModel.nbCreneauxParSemaine)]
        MainModel.ListeDesUEs = ["null"] + ["null"]*MainModel.nbUE
        MainModel.DictUEs = dict()

        MainModel.ListeDesEtudiants = ["null"]
        MainModel.ListeDesParcours = list()
        MainModel.ListeEffectifDesParcours = list()
        MainModel.ListeDesEffectifsCumules = list()
        MainModel.EnsIncompatibilites = set()
        MainModel.nbTotalIncompatibilites = 0
        MainModel.nbTotalIncompatibilitesVides = 0
        MainModel.nbInscriptionsSatisfaites = 0
        MainModel.ListedesVarY = list()
        #Jeudi 15
        MainModel.charge = 0
        MainModel.capaciteMaximale = 0
        #Jeudi 15
        MainModel.ListeDesEtudiantsParParcours = list()
        # for parcours, List in MainModel.DictionnaireDesInsatisfactionsParParcours.items():
        #     print (parcours + " " + str(len(List)))
        MainModel.DictionnaireDesInsatisfactionsParParcours = dict() #MARDI 20 MARS :  non remise a zero du dictionnaire des insat par parcours idee connaitre les parcours qui rejette le plus
        MainModel.DictionnaireDistribUEInsatisfaitesParParcours = dict()

        MainModel.modelGurobi = Model("OPTIMISATION DES INSCRIPTIONS AUX UE (PAR DAK)")
        MainModel.objectif1 = LinExpr()
        MainModel.objectif2 = LinExpr()


    #     STOP HERE




#m = MainModel("../VOEUX", "edt.csv", equilibre=True)
# # # # # # m = MainModel("RAND_VOEUX1", "edt.csv")
#m.resoudre()
# # # #
# # # #
# f = open("inscription2017_2018_.txt", "w")
# # # # # f = open("R1inscription2017_2018.txt", "w")
# # # #
# f.write(str(m))
# # # # # f.write("\n\n"+str(analyses))
# # f.close()
#
# #

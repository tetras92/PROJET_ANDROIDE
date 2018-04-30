from gurobipy import *
from HelpingFunctions import *
import csv
import UE
import Etudiant
import Incompatibilite
import Parcours


class DAK_Optimizer:

    class Parameters:
        nbMaxCoursParUE= 2
        nbMaxUEObligatoires = 3                #Par Etudiant
        nbMaxUEConseillees = 5                  #Par Etudiant
        nbMaxUEConseilleesParcours = 8
        nbUE = 21
        tauxEquilibre = 0.10
        nbCreneauxParSemaine = 25
        nbMaxGroupeParUE = 5
        TailleMaxContrat = 5

    ListeDesParcours = list()
    DictUEs = dict()
    ListedesVarY = list()
    ListedesVarN = list()
    ListeDesUEs = ["null"] + ["null"]*Parameters.nbUE
    ListeDesEtudiants = list()
    EDT = [dict()] + [generer_model_dict_creneau(Parameters.nbMaxGroupeParUE) for i in range(0, Parameters.nbCreneauxParSemaine)]
    capaciteTotaleAccueil = 0

    iModelAlea = 0

    ListeEffectifDesParcours = list()
    ListeDesParcours = list()
    ListeDesEffectifsCumules = list()


    DictionnaireDesInsatisfactionsParParcours = dict()
    DictionnaireDistribUEInsatisfaitesParParcours = dict()


    nbTotalIncompatibilites = 0
    EnsIncompatibilites = set()


    modelGurobi = Model("OPTIMISATION DES INSCRIPTIONS AUX UE (PAR DAK)")




    def __init__(self, fileUE):
        print "constructeur DAK_Optimizer"
        # self.fileUE= fileUE
        # self.charger_edt(self.fileUE)

    def charger_edt(self, fileUE):
        f_ue = open(fileUE)
        data = csv.DictReader(f_ue)
        for ligneUE in data:
            currentUE = UE(ligneUE, self) #Generation de l'objet UE
            currentUE.actualiseEDT()
            DAK_Optimizer.ListeDesUEs[currentUE.get_id()] = currentUE             #Rajout a la listeUe
            DAK_Optimizer.DictUEs[currentUE.intitule] = currentUE                  #Rajout au DictUe

            #NETTOYER EDT : supprimer les associations de numeros de groupe avec des ensembles vides
        for creneau in range(1, len(DAK_Optimizer.EDT)):
            dictCopy = DAK_Optimizer.EDT[creneau].copy()
            for id in dictCopy:
                if len(dictCopy[id]) == 0:
                    del DAK_Optimizer.EDT[creneau][id]
            # FIN NETTOYAGE EDT
        self.generer_incompatibilites()


    def charger_parcours(self, fileParcours):
        csvfile = open(fileParcours, 'r')
        parcoursreader = csv.DictReader(csvfile, delimiter=',')

        for parcoursCsvLine in parcoursreader:
            current_parcours = Parcours(parcoursCsvLine, self)
            DAK_Optimizer.ListeDesParcours.append(current_parcours)
            # path = Generateur_Voeux.directoryName+str(self.nbDossiersGeneres)
            # current_parcours.generer_csv_aleatoires(path)
        csvfile.close()


    def generer_incompatibilites(self):
        #GERER LES INCOMPATIBILITES
        for creneauId in range(1, len(DAK_Optimizer.EDT)):
            #incompatibilites groupesTdTme
            dictCreneau = DAK_Optimizer.EDT[creneauId]

            for (idGroup1, EnsUE1) in dictCreneau.items():
                if idGroup1 != 0:
                    #Incompatibilite intra meme numeroGroup
                    for ueIntra1 in EnsUE1:
                        for ueIntra2 in EnsUE1:       #EnsUE2:  CORRECTION
                            if ueIntra1 < ueIntra2:
                                currentIncompatibilite = Incompatibilite(ueIntra1, idGroup1, ueIntra2, idGroup1, self)
                                #Instruction Rajout au model
                                # currentIncompatibilite.ajouterContrainteModeleGurobi(DAK_Optimizer.modelGurobi)
                                DAK_Optimizer.EnsIncompatibilites.add(currentIncompatibilite)
                #Fin Incompatibilite intra meme numeroGroup
                for (idGroup2, EnsUE2) in dictCreneau.items():
                    if idGroup1 > 0 and idGroup1 < idGroup2: # CONVENTION IdGroup1 < IdGroup2:
                        for ue1 in EnsUE1:
                            for ue2 in EnsUE2:
                                if ue1 != ue2: #l'incompatibilite entre deux groupes d'une meme ue est deja gere
                                    currentIncompatibilite = Incompatibilite(ue1, idGroup1, ue2, idGroup2, self)
                                    #Instruction Rajout au model
                                    # currentIncompatibilite.ajouterContrainteModeleGurobi(DAK_Optimizer.modelGurobi)
                                    #Fin
                                    DAK_Optimizer.EnsIncompatibilites.add(currentIncompatibilite)

            #Incompatibilite intra cours meme creneau + incompatibilite inter cours et td tme
            try:
                for ue1 in dictCreneau[0]:
                    #Incompatibilite intra cours meme creneau
                    nb_group_ue1 = DAK_Optimizer.ListeDesUEs[ue1].get_nb_groupes()
                    for ue2 in dictCreneau[0]:
                        if ue1 < ue2:

                            nb_group_ue2 = DAK_Optimizer.ListeDesUEs[ue2].get_nb_groupes() #CORRECTION ...  ListeDesUEs[ue2] au lieu de ListeDesUEs[ue1]
                            for idGroup1 in range(1, nb_group_ue1+1):
                                for idGroup2 in range(1, nb_group_ue2):
                                    currentIncompatibilite = Incompatibilite(ue1, idGroup1, ue2, idGroup2, self)
                                    #Instruction Rajout au model
                                    # currentIncompatibilite.ajouterContrainteModeleGurobi(DAK_Optimizer.modelGurobi)
                                    #Fin
                                    # if random.random() <= 0.5:
                                    #     print(currentIncompatibilite)
                                    DAK_Optimizer.EnsIncompatibilites.add(currentIncompatibilite)

                    # incompatibilite inter cours et td tme
                    for (idGroupTdTme, EnsUE2) in dictCreneau.items():
                        if idGroupTdTme > 0:
                            for ue2 in EnsUE2:
                                for idGroup1 in range(1, nb_group_ue1+1):
                                    currentIncompatibilite = Incompatibilite(ue1, idGroup1, ue2, idGroupTdTme, self)
                                    #Instruction Rajout au model
                                    # currentIncompatibilite.ajouterContrainteModeleGurobi(DAK_Optimizer.modelGurobi)
                                    #Fin
                                    DAK_Optimizer.EnsIncompatibilites.add(currentIncompatibilite)

            except:
                pass

        #FIN GESTION DES INCOMPATIBILITES


    def traiter_dossier_voeux(self, dossierVoeux):
        for fichierVoeux in os.listdir(dossierVoeux):
            # try: #POUR EVITER LES ERREURS DE SPLIT SUR LE DOSSIER DE VOEUX PAR PARCOURS
            parcours = fichierVoeux.split('.')[1]
            path = dossierVoeux+"/"+fichierVoeux
            f_voeux = open(path)
            data = csv.DictReader(f_voeux)

            Obj_Parcours = self.get_Parcours(parcours)

            for ligneEtu in data:
                currentEtu = Etudiant(ligneEtu, Obj_Parcours, self) #generation de l'objet etudiant
                DAK_Optimizer.ListeDesEtudiants.append(currentEtu)
                currentEtu.enregistrer_interet_pour_UE()



    def get_Parcours(self, nom):
        for Parcours_Obj in DAK_Optimizer.ListeDesParcours:
            if Parcours_Obj.get_nom() == nom:
                return Parcours_Obj

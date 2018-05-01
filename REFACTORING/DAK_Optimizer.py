from UE import *
from Etudiant import *
from Incompatibilite import *
from Parcours import *
from MatchingModel import *
from GenerateurDeVoeux import *
from Analyzer import *

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

    restaurer_UEsParcours = False        #EFFACER DONNEES AFFECTATION
    ListeDesParcours = list()



    nbTotalIncompatibilites = 0
    EnsIncompatibilites = set()



    def __init__(self):
        print "DAK_Optimizer Powered by DAK"

    def charger_edt(self, fileUE):
        f_ue = open(fileUE)
        data = csv.DictReader(f_ue)
        for ligneUE in data:
            currentUE = UE(ligneUE, self) #Generation de l'objet UE
            currentUE.actualiseEDT(DAK_Optimizer.EDT)
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

                                    DAK_Optimizer.EnsIncompatibilites.add(currentIncompatibilite)

                    # incompatibilite inter cours et td tme
                    for (idGroupTdTme, EnsUE2) in dictCreneau.items():
                        if idGroupTdTme > 0:
                            for ue2 in EnsUE2:
                                for idGroup1 in range(1, nb_group_ue1+1):
                                    currentIncompatibilite = Incompatibilite(ue1, idGroup1, ue2, idGroupTdTme, self)

                                    DAK_Optimizer.EnsIncompatibilites.add(currentIncompatibilite)

            except:
                pass

        #FIN GESTION DES INCOMPATIBILITES


    def traiter_dossier_voeux(self, dossierVoeux):
        for fichierVoeux in os.listdir(dossierVoeux):
            try: #POUR EVITER LES ERREURS DE SPLIT SUR LE DOSSIER DE VOEUX PAR PARCOURS
                parcours = fichierVoeux.split('.')[1]
                path = dossierVoeux+"/"+fichierVoeux
                f_voeux = open(path)
                data = csv.DictReader(f_voeux)

                Obj_Parcours = self.get_Parcours(parcours)

                for ligneEtu in data:
                    currentEtu = Etudiant(ligneEtu, Obj_Parcours, self) #generation de l'objet etudiant
                    DAK_Optimizer.ListeDesEtudiants.append(currentEtu)
                    currentEtu.enregistrer_interet_pour_UE()
            except:
                pass


    def get_Parcours(self, nom):
        for Parcours_Obj in DAK_Optimizer.ListeDesParcours:
            if Parcours_Obj.get_intitule() == nom:
                return Parcours_Obj

    def effacer_donnees_affectation_UEs(self):
        for Ue in DAK_Optimizer.ListeDesUEs[1:]:
            Ue.restaurer_places_apres_affectation()
        DAK_Optimizer.ListedesVarY = list()
        DAK_Optimizer.ListedesVarN = list()

    def effacer_donnees_affectation_Parcours(self):
        for Parcours_Obj in DAK_Optimizer.ListeDesParcours:
            Parcours_Obj.effacer_donnees_problemes_affectation()

    def match(self, equilibre=True, tauxEquilibre=0.10, path='',analyzer=None):
        if DAK_Optimizer.restaurer_UEsParcours:
            self.effacer_donnees_affectation_UEs()
            self.effacer_donnees_affectation_Parcours()
            DAK_Optimizer.restaurer_UEsParcours = False

        if tauxEquilibre >= 0 and tauxEquilibre <= 1.0:
            DAK_Optimizer.Parameters.tauxEquilibre = tauxEquilibre
        MM = MatchingModel(self,equilibre)
        if analyzer != None:
            analyzer.add_MatchingModel(MM)
        value = MM.match(path)
        print MM
        return value

    def nettoyer_les_Ues_et_les_Incompatibilites(self):
        for Ue in DAK_Optimizer.ListeDesUEs[1:]:
            Ue.remise_a_zero()

        for Incompatibilite in DAK_Optimizer.EnsIncompatibilites:
            Incompatibilite.reset_incompatibilite()

    def reinitialiser_les_parcours(self, sauvegarde=True):
        for Parcours_Obj in DAK_Optimizer.ListeDesParcours:
            Parcours_Obj.reinitialiser_parcours(sauvegarde)

    def eprouver_edt(self, nombreDeDossierGeneres=50, directoryName='VOEUX_RANDOM',equilibre=True, tauxEquilibre=0.10):
        G = GenerateurDeVoeux(directoryName, self)
        G.generer(nombreDeDossierGeneres)
        #Traitement
        # #RESTAURATION A L'ETAT DE DEPART
        self.reinitialiser_les_parcours(sauvegarde=False) #Au cas ou il y aurait eu un matching avant
        self.nettoyer_les_Ues_et_les_Incompatibilites()
        DAK_Optimizer.ListedesVarY = list()
        DAK_Optimizer.ListedesVarN = list()
        DAK_Optimizer.ListeDesEtudiants = list()
        #FIN RESTAURATION
        analyseur =  Analyzer(self)
        for dossierId in range(nombreDeDossierGeneres):
            self.traiter_dossier_voeux(directoryName+"/"+str(dossierId))
            self.match(equilibre,tauxEquilibre,path=directoryName+"/"+str(dossierId),analyzer=analyseur)
            DAK_Optimizer.iModelAlea += 1
            # RESTAURATION A L'ETAT DE DEPART
            self.reinitialiser_les_parcours()
            self.nettoyer_les_Ues_et_les_Incompatibilites()
            DAK_Optimizer.ListedesVarY = list()
            DAK_Optimizer.ListedesVarN = list()
            DAK_Optimizer.ListeDesEtudiants = list()
            # FIN RESTAURATION
        analyseur.analyze()

    def AS_modifier_capacite(self, idUE, numeroGroupe, nouvelleCapacite):
        DAK_Optimizer.ListeDesUEs[idUE].modifier_capacite_groupe(numeroGroupe, nouvelleCapacite)
        DAK_Optimizer.restaurer_UEsParcours = True


    def AS_supprimer_groupe(self, idUE, numeroGroupe):
        self.AS_modifier_capacite(idUE, numeroGroupe, 0)

    def AS_ajouter_groupe(self, ueId, creneauTd, creneauTme, capacite):
        numNouveauGroupe = DAK_Optimizer.ListeDesUEs[ueId].ajouter_un_groupe(creneauTd, creneauTme, capacite)
        #MAJ_EDT
        dictCreneauTd = DAK_Optimizer.EDT[creneauTd]
        if numNouveauGroupe not in dictCreneauTd:
            dictCreneauTd[numNouveauGroupe] = set([ueId])
        else:
            dictCreneauTd[numNouveauGroupe].add(ueId)

        dictCreneauTme = DAK_Optimizer.EDT[creneauTme]
        if numNouveauGroupe not in dictCreneauTme:
            dictCreneauTme[numNouveauGroupe] = set([ueId])
        else:
            dictCreneauTme[numNouveauGroupe].add(ueId)

        DAK_Optimizer.EnsIncompatibilites.clear()
        self.generer_incompatibilites()

        DAK_Optimizer.restaurer_UEsParcours = True

    def AD_afficher_carte_augmentee_incompatibilites(self, nomParcours, taille=5):

        indexParcours = 0
        while nomParcours != DAK_Optimizer.ListeDesParcours[indexParcours].get_intitule():
            indexParcours += 1

        DAK_Optimizer.ListeDesParcours[indexParcours].afficher_carte_augmentee_incompatibilites(taille)

    def maj_interets_etudiants_pour_les_ues(self):
        for Etu in DAK_Optimizer.ListeDesEtudiants:
            Etu.enregistrer_interet_pour_UE()

    def RL_introduire_les_indifferences_etudiants(self):
        for Etu in DAK_Optimizer.ListeDesEtudiants:
            Etu.generer_aleatoirement_mes_indifferences()

    def RL_voisinage(self):
        for Etu in DAK_Optimizer.ListeDesEtudiants:
            if Etu.get_statut():
                Etu.changer_mes_ues_non_obligatoires()

    def RL_appliquer(self, proba, objectif, timeLimit):

        self.RL_introduire_les_indifferences_etudiants()
        time_ = 0
        while time_ < timeLimit:
            time_ += 1
            self.RL_voisinage()
            # DAK_Optimizer.restaurer_UEsParcours = True
            self.nettoyer_les_Ues_et_les_Incompatibilites()
            # for Ue in DAK_Optimizer.ListeDesUEs[1:]:
            #     print Ue
            self.maj_interets_etudiants_pour_les_ues()
            # for Ue in DAK_Optimizer.ListeDesUEs[1:]:
            #     print Ue
            #     print Ue.getEnsEtu()

            DAK_Optimizer.ListedesVarY = list()
            DAK_Optimizer.ListedesVarN = list()
            self.effacer_donnees_affectation_Parcours()
            value = self.match()
            if value > objectif:
                print "ameliore", value, objectif
                objectif = value


Optim = DAK_Optimizer()
Optim.charger_edt("edt.csv")
print Optim.DictUEs
Optim.charger_parcours("parcours.csv")
Optim.traiter_dossier_voeux("../VOEUX")
Optim.match()
Optim.RL_appliquer(0.4, len(DAK_Optimizer.ListeDesEtudiants)/2, 35)

#
# Optim.AS_supprimer_groupe(11, 3) #Groupe 3 Mapsi
#
# Optim.AS_modifier_capacite(10, 1, 36)
# Optim.AS_modifier_capacite(10, 3, 36)   # AUX GROUPES DE LRC
# Optim.AS_modifier_capacite(10, 2, 36)
# Optim.AS_modifier_capacite(10, 4, 36)
#
# Optim.AS_ajouter_groupe(6, 5, 24, 32)      #UN GROUPE DE 32 EN COMPLEX
# Optim.AS_supprimer_groupe(9, 3)           #IL3
# Optim.AS_ajouter_groupe(9, 21, 22, 32)

# Optim.AD_afficher_carte_augmentee_incompatibilites("sfpn")
# Optim.eprouver_edt(nombreDeDossierGeneres=50)
# for P in Optim.ListeDesParcours:
#     print P.nom
#     print P.HistoriqueDesContratsAProbleme

# Optim.match(False)

# Optim.match()
# Optim.AS_modifier_capacite(10, 4, 35)
# Optim.match()

# Optim.match()
# Optim.AS_modifier_capacite(6, 2, 35)
# Optim.match()

# Optim.match(equilibre=False)
# Optim.AS_supprimer_groupe(3, 1)
# Optim.match(False)

# Optim.match()

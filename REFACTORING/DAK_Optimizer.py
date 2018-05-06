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
    UE_modifiees = False
    ListeDesParcours = list()



    nbTotalIncompatibilites = 0
    EnsIncompatibilites = set()



    def __init__(self):
        print "DAK_Optimizer Powered by DAK"

    def charger_edt(self, fileUE):
        self.EDT = [dict()] + [generer_model_dict_creneau(DAK_Optimizer.Parameters.nbMaxGroupeParUE) for i in range(0, DAK_Optimizer.Parameters.nbCreneauxParSemaine)]
        self.capaciteTotaleAccueil = 0
        f_ue = open(fileUE)
        data = csv.DictReader(f_ue)
        for ligneUE in data:
            # print ligneUE
            currentUE = UE(ligneUE, self) #Generation de l'objet UE
            currentUE.actualiseEDT(self.EDT)
            self.ListeDesUEs[currentUE.get_id()] = currentUE             #Rajout a la listeUe
            self.DictUEs[currentUE.intitule] = currentUE                  #Rajout au DictUe

            #NETTOYER EDT : supprimer les associations de numeros de groupe avec des ensembles vides
        for creneau in range(1, len(self.EDT)):
            dictCopy = self.EDT[creneau].copy()
            for id in dictCopy:
                if len(dictCopy[id]) == 0:
                    del self.EDT[creneau][id]
            # FIN NETTOYAGE EDT
        # print self.EDT
        self.generer_incompatibilites()


    def charger_parcours(self, fileParcours):
        csvfile = open(fileParcours, 'r')
        parcoursreader = csv.DictReader(csvfile, delimiter=',')

        for parcoursCsvLine in parcoursreader:
            current_parcours = Parcours(parcoursCsvLine, self)
            self.ListeDesParcours.append(current_parcours)

        csvfile.close()


    def generer_incompatibilites(self):
        #GERER LES INCOMPATIBILITES
        self.EnsIncompatibilites.clear()
        for creneauId in range(1, len(self.EDT)):
            #incompatibilites groupesTdTme
            dictCreneau = self.EDT[creneauId]

            for (idGroup1, EnsUE1) in dictCreneau.items():
                if idGroup1 != 0:
                    #Incompatibilite intra meme numeroGroup
                    for ueIntra1 in EnsUE1:
                        for ueIntra2 in EnsUE1:       #EnsUE2:  CORRECTION
                            if ueIntra1 < ueIntra2:
                                currentIncompatibilite = Incompatibilite(ueIntra1, idGroup1, ueIntra2, idGroup1, self)
                                #Instruction Rajout au model
                                # currentIncompatibilite.ajouterContrainteModeleGurobi(self.modelGurobi)
                                self.EnsIncompatibilites.add(currentIncompatibilite)
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
                                    self.EnsIncompatibilites.add(currentIncompatibilite)

            #Incompatibilite intra cours meme creneau + incompatibilite inter cours et td tme
            try:
                for ue1 in dictCreneau[0]:
                    #Incompatibilite intra cours meme creneau
                    nb_group_ue1 = self.ListeDesUEs[ue1].get_nb_groupes()
                    for ue2 in dictCreneau[0]:
                        if ue1 < ue2:

                            nb_group_ue2 = self.ListeDesUEs[ue2].get_nb_groupes() #CORRECTION ...  ListeDesUEs[ue2] au lieu de ListeDesUEs[ue1]
                            for idGroup1 in range(1, nb_group_ue1+1):
                                for idGroup2 in range(1, nb_group_ue2):
                                    currentIncompatibilite = Incompatibilite(ue1, idGroup1, ue2, idGroup2, self)

                                    self.EnsIncompatibilites.add(currentIncompatibilite)

                    # incompatibilite inter cours et td tme
                    for (idGroupTdTme, EnsUE2) in dictCreneau.items():
                        if idGroupTdTme > 0:
                            for ue2 in EnsUE2:
                                for idGroup1 in range(1, nb_group_ue1+1):
                                    currentIncompatibilite = Incompatibilite(ue1, idGroup1, ue2, idGroupTdTme, self)

                                    self.EnsIncompatibilites.add(currentIncompatibilite)

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
                    self.ListeDesEtudiants.append(currentEtu)
                    currentEtu.enregistrer_interet_pour_UE()
            except:
                pass


    def get_Parcours(self, nom):
        for Parcours_Obj in self.ListeDesParcours:
            if Parcours_Obj.get_intitule() == nom:
                return Parcours_Obj

    def effacer_donnees_affectation_UEs(self):
        for Ue in self.ListeDesUEs[1:]:
            Ue.restaurer_places_apres_affectation()
        self.ListedesVarY = list()
        self.ListedesVarN = list()

    def effacer_donnees_affectation_Parcours(self):
        for Parcours_Obj in self.ListeDesParcours:
            Parcours_Obj.effacer_donnees_problemes_affectation()

    def match(self, equilibre=True, tauxEquilibre=0.10, path='',analyzer=None):
        if self.restaurer_UEsParcours:
            self.effacer_donnees_affectation_UEs()
            self.effacer_donnees_affectation_Parcours()
            self.restaurer_UEsParcours = False

        if tauxEquilibre >= 0 and tauxEquilibre <= 1.0:
            DAK_Optimizer.Parameters.tauxEquilibre = tauxEquilibre
        MM = MatchingModel(self,equilibre)
        if analyzer != None:
            analyzer.add_MatchingModel(MM)
        value = MM.match(path)
        print MM
        return value

    def nettoyer_les_Ues_et_les_Incompatibilites(self):
        for Ue in self.ListeDesUEs[1:]:
            Ue.remise_a_zero()

        for Incompatibilite in self.EnsIncompatibilites:
            Incompatibilite.reset_incompatibilite()

    def reinitialiser_les_parcours(self, sauvegarde=True):
        for Parcours_Obj in self.ListeDesParcours:
            Parcours_Obj.reinitialiser_parcours(sauvegarde)


#----------EPROUVER
    def eprouver_edt(self, nombreDeDossierGeneres=50, directoryName='VOEUX_RANDOM',equilibre=True, tauxEquilibre=0.10):
        if self.UE_modifiees:
            print "sauvegarde"
            self.sauvegarde_UEs(".edt.csv")
            self.charger_edt(".edt.csv")
            print self.capaciteTotaleAccueil
            for Parcours_Obj in self.ListeDesParcours:
                Parcours_Obj.generer_dico_Nbconfig()
            self.UE_modifiees = False
            self.AD_afficher_carte_augmentee_incompatibilites("and")

        G = GenerateurDeVoeux(directoryName, self)
        G.generer(nombreDeDossierGeneres)


        #Traitement
        # #RESTAURATION A L'ETAT DE DEPART
        self.reinitialiser_les_parcours(sauvegarde=False) #Au cas ou il y aurait eu un matching avant
        self.nettoyer_les_Ues_et_les_Incompatibilites()
        self.ListedesVarY = list()
        self.ListedesVarN = list()
        self.ListeDesEtudiants = list()
        #FIN RESTAURATION
        analyseur =  Analyzer(self)
        for dossierId in range(nombreDeDossierGeneres):
            self.traiter_dossier_voeux(directoryName+"/"+str(dossierId))
            self.match(equilibre,tauxEquilibre,path=directoryName+"/"+str(dossierId),analyzer=analyseur)
            self.iModelAlea += 1
            # RESTAURATION A L'ETAT DE DEPART
            self.reinitialiser_les_parcours()
            self.nettoyer_les_Ues_et_les_Incompatibilites()
            self.ListedesVarY = list()
            self.ListedesVarN = list()
            self.ListeDesEtudiants = list()
            # FIN RESTAURATION
        analyseur.analyze()




    def AS_modifier_capacite(self, idUE, numeroGroupe, nouvelleCapacite):
        # if nouvelleCapacite != 0:
        self.ListeDesUEs[idUE].modifier_capacite_groupe(numeroGroupe, nouvelleCapacite)
        self.restaurer_UEsParcours = True
        # else:
        #     print "pour supprimer un groupe utiliser la fonction adequate"

    def AS_supprimer_groupe(self, idUE, numeroGroupe):
        self.AS_modifier_capacite(idUE, numeroGroupe, 0)
        self.UE_modifiees = True               #5/5

    def AS_ajouter_groupe(self, ueId, creneauTd, creneauTme, capacite):
        numNouveauGroupe = self.ListeDesUEs[ueId].ajouter_un_groupe(creneauTd, creneauTme, capacite)
        #MAJ_EDT
        dictCreneauTd = self.EDT[creneauTd]
        if numNouveauGroupe not in dictCreneauTd:
            dictCreneauTd[numNouveauGroupe] = set([ueId])
        else:
            dictCreneauTd[numNouveauGroupe].add(ueId)

        dictCreneauTme = self.EDT[creneauTme]
        if numNouveauGroupe not in dictCreneauTme:
            dictCreneauTme[numNouveauGroupe] = set([ueId])
        else:
            dictCreneauTme[numNouveauGroupe].add(ueId)

        self.EnsIncompatibilites.clear()
        self.generer_incompatibilites()

        self.restaurer_UEsParcours = True
        self.UE_modifiees = True

    def AD_afficher_carte_augmentee_incompatibilites(self, nomParcours, taille=5):

        indexParcours = 0
        while nomParcours != self.ListeDesParcours[indexParcours].get_intitule():
            indexParcours += 1

        self.ListeDesParcours[indexParcours].afficher_carte_augmentee_incompatibilites(taille)

    def maj_interets_etudiants_pour_les_ues(self):
        for Etu in self.ListeDesEtudiants:
            Etu.enregistrer_interet_pour_UE()

    def RL_introduire_les_indifferences_etudiants(self):
        for Etu in self.ListeDesEtudiants:
            Etu.generer_aleatoirement_mes_indifferences()

    def RL_voisinage(self):
        for Etu in self.ListeDesEtudiants:
            if Etu.get_statut():
                Etu.changer_mes_ues_non_obligatoires()

    def RL_appliquer(self, objectif, timeLimit):

        self.RL_introduire_les_indifferences_etudiants()
        time_ = 0
        while time_ < timeLimit:
            time_ += 1
            self.RL_voisinage()
            # self.restaurer_UEsParcours = True
            self.nettoyer_les_Ues_et_les_Incompatibilites()
            # for Ue in self.ListeDesUEs[1:]:
            #     print Ue
            self.maj_interets_etudiants_pour_les_ues()
            # for Ue in self.ListeDesUEs[1:]:
            #     print Ue
            #     print Ue.getEnsEtu()

            self.ListedesVarY = list()
            self.ListedesVarN = list()
            self.effacer_donnees_affectation_Parcours()
            value = self.match()
            if value > objectif:
                print "ameliore", value, objectif
                objectif = value

    def sauvegarde_UEs(self, path):
        file = open(path, "w")
        fieldnames = ["id_ue", "intitule", "nb_groupes"] + ["capac"+str(i) for i in range(1, DAK_Optimizer.Parameters.nbMaxGroupeParUE+1)]
        fieldnames += ["cours"+str(i) for i in range(1, DAK_Optimizer.Parameters.nbMaxCoursParUE+1)]


        Z = zip(["td"+str(i) for i in range(1, DAK_Optimizer.Parameters.nbMaxGroupeParUE+1)], ["tme"+str(i) for i in range(1, DAK_Optimizer.Parameters.nbMaxGroupeParUE+1)])
        fieldnames += [elem for couple in Z for elem in list(couple)]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for Ue in self.ListeDesUEs[1:]:
            csvLine = Ue.ue_sauvegarde()
            writer.writerow(csvLine)
        file.close()



Optim = DAK_Optimizer()
Optim.charger_edt("edt.csv")
Optim.charger_parcours("parcours.csv")
# print Optim.DictUEs


# Optim.match()
# Optim.eprouver_edt(nombreDeDossierGeneres=5)
# Optim.RL_appliquer(len(DAK_Optimizer.ListeDesEtudiants)/2, 35)
# Optim.RL_appliquer(len(DAK_Optimizer.ListeDesEtudiants)/2, 35)
#

# Optim.AS_ajouter_groupe(5, 23, 24, 16) #Bima
# Optim.AS_modifier_capacite(4, 1, 36)
# Optim.AS_modifier_capacite(4, 3, 36)   # AUX GROUPES DE ARES
# Optim.AS_modifier_capacite(4, 2, 36)
# Optim.traiter_dossier_voeux("../VOEUX")
# Optim.AS_supprimer_groupe(11, 3) #Groupe 3 Mapsi

Optim.AS_supprimer_groupe(13, 4)          #DEPLACEMENT DES CRENEAUX MLBDA
Optim.AS_ajouter_groupe(13,24,25,32)

Optim.AS_supprimer_groupe(6,1)
Optim.AS_ajouter_groupe(6,5,10,50)
# #
# Optim.AS_modifier_capacite(10, 1, 36)
# Optim.AS_modifier_capacite(10, 3, 36)   # AUX GROUPES DE LRC
# Optim.AS_modifier_capacite(10, 2, 36)
# Optim.AS_modifier_capacite(10, 4, 36)
# Optim.match()
# Optim.sauvegarde_UEs("edt.csv")
Optim.eprouver_edt(nombreDeDossierGeneres=25)
Optim.AD_afficher_carte_augmentee_incompatibilites("and")

print Optim.capaciteTotaleAccueil
# Optim.AD_afficher_carte_augmentee_incompatibilites("and")
# #
# Optim.AS_ajouter_groupe(6, 5, 24, 32)      #UN GROUPE DE 32 EN COMPLEX
# Optim.match()




# Optim.AS_supprimer_groupe(9, 3)           #IL3
# Optim.AS_ajouter_groupe(9, 21, 22, 32)

# Optim.AD_afficher_carte_augmentee_incompatibilites("and")
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

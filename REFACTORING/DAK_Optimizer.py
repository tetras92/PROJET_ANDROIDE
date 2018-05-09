from UE import *
from Etudiant import *
from Incompatibilite import *
from Parcours import *
from MatchingModel import *
from GenerateurDeVoeux import *
from Analyzer import *
from heapq import heappop, heappush

class DAK_Optimizer:

    class Parameters:
        nbMaxCoursParUE= 2
        nbMaxUEObligatoires = 3                #Par Etudiant
        nbMaxUEConseillees = 5                  #Par Etudiant
        nbMaxUEConseilleesParcours = 8
        nbUE = 21
        # tauxEquilibre = 0.10
        nbCreneauxParSemaine = 25
        nbMaxGroupeParUE = 5
        TailleMaxContrat = 5
        nbJoursOuvres = 5
        nbCreneauxParJour = 5


    ListeDesParcours = list()
    DictUEs = dict()
    ListedesVarY = list()
    ListedesVarN = list()
    ListeDesUEs = [None] + [None]*Parameters.nbUE
    ListeDesEtudiants = list()
    EDT = [dict()] + [generer_model_dict_creneau(Parameters.nbMaxGroupeParUE) for i in range(0, Parameters.nbCreneauxParSemaine)]
    capaciteTotaleAccueil = 0

    iModelAlea = 0
    modeleAleatoire = False

    affectationFaite = False        #EFFACER DONNEES AFFECTATION
    UE_modifiees_significativement = False
    edt_charge = False
    parcours_charge = False
    voeux_charges = False

    tauxEquilibre = 0.10

    ListeDesParcours = list()

    dict_nombre_de_contrats_incompatibles_par_parcours = dict()

    nbTotalIncompatibilites = 0
    EnsIncompatibilites = set()

    nbDossiersParDefaut = 50


    def __init__(self):
        print "DAK_Optimizer Powered by DAK"
        self.analyseur =  Analyzer(self)

    def operations_pre_chargement_edt(self):
        self.EDT = [dict()] + [generer_model_dict_creneau(DAK_Optimizer.Parameters.nbMaxGroupeParUE) for i in range(0, DAK_Optimizer.Parameters.nbCreneauxParSemaine)]
        self.DictUEs = dict()
        self.capaciteTotaleAccueil = 0
        self.ListeDesUEs = [None] + [None]*DAK_Optimizer.Parameters.nbUE
        self.EnsIncompatibilites.clear()

    def charger_edt(self, fileUE):

        self.operations_pre_chargement_edt()

        f_ue = open(fileUE)
        data = csv.DictReader(f_ue)
        for ligneUE in data:
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
        self.generer_incompatibilites()
        self.edt_charge = True

    def operations_pre_chargement_parcours(self):
        self.ListeDesParcours = list()

    def charger_parcours(self, fileParcours):

        self.operations_pre_chargement_parcours()
        if self.edt_charge:
            csvfile = open(fileParcours, 'r')
            parcoursreader = csv.DictReader(csvfile, delimiter=',')

            for parcoursCsvLine in parcoursreader:
                current_parcours = Parcours(parcoursCsvLine, self)
                self.ListeDesParcours.append(current_parcours)

            csvfile.close()
            self.parcours_charge = True
        else:
            print "Veuillez charger le fichier edt" #REMPLACER PAR UNE BOITE DE DIALOG OU DES EXCEPTIONS

    def generer_incompatibilites(self):
        #GERER LES INCOMPATIBILITES
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


    def operations_pre_traitement_voeux(self):
        self.ListeDesEtudiants = list()
        # self.effacer_donnees_affectation_Parcours()


    def traiter_dossier_voeux(self, dossierVoeux):
        self.operations_pre_traitement_voeux()

        if self.edt_charge:
            for fichierVoeux in os.listdir(dossierVoeux):
                try: #POUR EVITER LES ERREURS DE SPLIT SUR LE DOSSIER DE VOEUX PAR PARCOURS
                    parcours = fichierVoeux.split('.')[1]
                    path = dossierVoeux+"/"+fichierVoeux
                    f_voeux = open(path)
                    data = csv.DictReader(f_voeux)

                    Obj_Parcours = self.get_Parcours(parcours)
                    # print Obj_Parcours.nom
                    for ligneEtu in data:
                        currentEtu = Etudiant(ligneEtu, Obj_Parcours, self) #generation de l'objet etudiant
                        self.ListeDesEtudiants.append(currentEtu)
                        # currentEtu.enregistrer_interet_pour_UE()
                        self.voeux_charges = True
                except:
                    pass
        else:
            print "Veuillez charger le fichier edt" #REMPLACER PAR UNE BOITE DE DIALOG OU DES EXCEPTIONS

        # for p in self.ListeDesParcours:
        #     print p

    def get_Parcours(self, nom):
        for Parcours_Obj in self.ListeDesParcours:
            if Parcours_Obj.get_intitule() == nom:
                return Parcours_Obj

    def effacer_donnees_affectation_UEs(self):
        for Ue in self.ListeDesUEs[1:]:
            Ue.remise_a_zero()

    def effacer_donnees_affectation_Parcours(self):
        for Parcours_Obj in self.ListeDesParcours:
            Parcours_Obj.effacer_donnees_problemes_affectation()
            # print Parcours_Obj.nom,  Parcours_Obj.effectif

    def preparer_condition_matching_courant(self):
        self.effacer_donnees_affectation_UEs()
        self.effacer_donnees_affectation_Parcours()
        self.affectationFaite = False



    def match(self, equilibre=True, tauxEquilibre=0.10, path='',analyzer=None):
        if self.edt_charge and self.parcours_charge and self.voeux_charges:
            if self.affectationFaite:
                # print "2222222222222222222222222222222222222222222222222"
                self.preparer_condition_matching_courant()
            if self.UE_modifiees_significativement:
                self.maj_suite_a_une_modification_significative_ue()

            if tauxEquilibre >= 0 and tauxEquilibre <= 1.0:
                self.tauxEquilibre = tauxEquilibre      #un changement de taux d'equilibre persiste
            MM = MatchingModel(self,equilibre)
            if analyzer != None:
                analyzer.add_MatchingModel(MM)
            value = MM.match(path)
            self.affectationFaite = True
            print MM
            return value
        else:
            print "Etat des chargements indispensables : \nVoeux charges : {}\t EDT charge : {}\t Parcours charges : {}\n".format(self.voeux_charges, self.edt_charge, self.parcours_charge)

    # def nettoyer_les_Ues_et_les_Incompatibilites(self):
    #     for Ue in self.ListeDesUEs[1:]:
    #         Ue.remise_a_zero()
    #
    #     for Incompatibilite in self.EnsIncompatibilites:
    #         Incompatibilite.reset_incompatibilite()

    def reinitialiser_les_parcours(self, sauvegarde=True):
        for Parcours_Obj in self.ListeDesParcours:
            Parcours_Obj.reinitialiser_parcours(sauvegarde)

    def maj_suite_a_une_modification_significative_ue(self):
        self.sauvegarde_UEs(".edt.csv")
        self.charger_edt(".edt.csv")

        for Parcours_Obj in self.ListeDesParcours:
            Parcours_Obj.generer_dico_Nbconfig()

        self.UE_modifiees_significativement = False

#----------EPROUVER
    def eprouver_edt(self, nombreDeDossierGeneres=nbDossiersParDefaut, directoryName='VOEUX_RANDOM',equilibre=True, tauxEquilibre=0.10):
        print "Mesure de la resistance de l'edt avec {} dossier(s) aleatoire(s)\n".format(nombreDeDossierGeneres)
        self.analyseur.reset()
        # if self.UE_modifiees_significativement:
        #     self.maj_suite_a_une_modification_significative_ue()
            # self.AD_afficher_carte_augmentee_incompatibilites("and")

        G = GenerateurDeVoeux(directoryName, self)
        G.generer(nombreDeDossierGeneres)
        self.modeleAleatoire = True



        for dossierId in range(nombreDeDossierGeneres):
            self.traiter_dossier_voeux(directoryName+"/"+str(dossierId))
            self.match(equilibre,tauxEquilibre,path=directoryName+"/"+str(dossierId),analyzer=self.analyseur)
            self.iModelAlea += 1

        self.analyseur.analyze()
        self.modeleAleatoire = False


    def AS_modifier_capacite(self, idUE, numeroGroupe, nouvelleCapacite):
        # if nouvelleCapacite != 0:
        self.ListeDesUEs[idUE].modifier_capacite_groupe(numeroGroupe, nouvelleCapacite)
        # self.affectationFaite = True
        # else:
        #     print "pour supprimer un groupe utiliser la fonction adequate"

    def AS_supprimer_groupe(self, idUE, numeroGroupe):
        self.AS_modifier_capacite(idUE, numeroGroupe, 0)
        self.UE_modifiees_significativement = True              #5/5

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

        self.affectationFaite = True
        self.UE_modifiees_significativement = True

    def AS_deplacer_groupe(self, ueId, numeroGroupe, new_creneautd, new_creneautme):
        capacite = self.ListeDesUEs[ueId].ListeCapacites[numeroGroupe-1]
        self.AS_supprimer_groupe(ueId, numeroGroupe)
        self.AS_ajouter_groupe(ueId, new_creneautd, new_creneautme, capacite)

    def AD_afficher_carte_incompatibilites(self, nomParcours, taille=5):

        indexParcours = 0
        while nomParcours != self.ListeDesParcours[indexParcours].get_intitule():
            indexParcours += 1

        self.ListeDesParcours[indexParcours].afficher_carte_incompatibilites(taille)

    # def maj_interets_etudiants_pour_les_ues(self):
    #     for Etu in self.ListeDesEtudiants:
    #         Etu.enregistrer_interet_pour_UE()

    def RL_introduire_les_indifferences_etudiants(self):
        for Etu in self.ListeDesEtudiants:
            Etu.generer_aleatoirement_mes_indifferences()

    def RL_voisinage(self):
        for Etu in self.ListeDesEtudiants:
            if Etu.get_statut():
                Etu.changer_mes_ues_non_obligatoires()

    def RL_appliquer(self, timeLimit=50):

        self.RL_introduire_les_indifferences_etudiants()
        objectif = self.match()
        time_ = 0
        while time_ < timeLimit:
            time_ += 1
            self.RL_voisinage()
            value = self.match()
            if value > objectif:
                print "ameliore", value, objectif
                objectif = value


    def AD_interets_ue_conseillees_par_parcours(self, dossierVoeux):
        self.analyseur.calculer_interet_pour_ue_conseillees_par_parcours(dossierVoeux)


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

    def afficher_EDT(self):
        if self.UE_modifiees_significativement:
            self.maj_suite_a_une_modification_significative_ue()

        EDT_str = [[] for i in range(DAK_Optimizer.Parameters.nbCreneauxParSemaine+1)]
        for creneauId in range(1, DAK_Optimizer.Parameters.nbCreneauxParSemaine+1):
            Dict_creneau = self.EDT[creneauId]

            for num_group, setUE in Dict_creneau.items():
                if num_group == 0: #il s'agit d'un cours
                    for ue_ayant_cours in setUE:
                        heappush(EDT_str[creneauId], self.ListeDesUEs[ue_ayant_cours].intitule.upper())
                else:
                    for ue_ayant_td_tme in setUE:
                        heappush(EDT_str[creneauId], self.ListeDesUEs[ue_ayant_td_tme].intitule +str(num_group))

        def prochain_element_creneau(T):
            if len(T) == 0:
                return ''
            return heappop(T)

        def une_ligne(j):
            s = ""
            for i in range(0, DAK_Optimizer.Parameters.nbCreneauxParSemaine, DAK_Optimizer.Parameters.nbJoursOuvres):
                s += '{:12s}| '.format(prochain_element_creneau(EDT_str[i+j]))
            s += "\n"
            return s
        def un_bloc(j_):
            s = ""
            nb_max_ligne = max([len(EDT_str[i + j_]) for i in range(0, DAK_Optimizer.Parameters.nbCreneauxParSemaine, DAK_Optimizer.Parameters.nbJoursOuvres)])
            for i in range(nb_max_ligne):
                s += une_ligne(j_)
            s += "\n\n"

            return s

        def en_tete():
            s = "{:12s}| {:12s}| {:12s}| {:12s}| {:12s}\n".format("Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi")
            s += "_"*14*5
            s += "\n"
            return s
        s = en_tete()
        for bloc in range(1, DAK_Optimizer.Parameters.nbCreneauxParJour+1):
            s += un_bloc(bloc)
            s += "_"*14*5
            s += "\n"



        return s



Optim = DAK_Optimizer()
Optim.charger_edt("edt.csv")


# Optim.charger_parcours("parcours.csv")
# # # # # print Optim.DictUEs
# # # #
# # # # Optim.AD_afficher_carte_incompatibilites("and")
# # # # # Optim.match()
# # # # Optim.eprouver_edt(nombreDeDossierGeneres=5)
# # # #
# # # # Optim.eprouver_edt(nombreDeDossierGeneres=10)
# # # # Optim.RL_appliquer(len(DAK_Optimizer.ListeDesEtudiants)/2, 35)
# # # # Optim.RL_appliquer(len(DAK_Optimizer.ListeDesEtudiants)/2, 35)
# Optim.traiter_dossier_voeux("../VOEUX")
#
# # # print Optim.dict_nombre_de_contrats_incompatibles_par_parcours
# # Optim.RL_appliquer(10)
# Optim.AS_ajouter_groupe(5, 23, 24, 16) #Bima
# Optim.AS_modifier_capacite(5, 1, 33)
# # Optim.AS_modifier_capacite(4, 3, 36)   # AUX GROUPES DE ARES
# # Optim.AS_modifier_capacite(4, 2, 36)
# # Optim.AD_interets_ue_conseillees_par_parcours("VOEUX_RANDOM/0")
# # Optim.RL_appliquer(10)
# # Optim.match()
Optim.AS_supprimer_groupe(6, 2) #Groupe 3 Mapsi
# Optim.match()
print Optim.afficher_EDT()
# Optim.match()
# Optim.AD_afficher_carte_incompatibilites("and")
# # Optim.AS_supprimer_groupe(13, 4)          #DEPLACEMENT DES CRENEAUX MLBDA
# # Optim.AS_ajouter_groupe(13,24,25,32)
# #
# # Optim.AS_supprimer_groupe(6,1)
# Optim.AS_deplacer_groupe(6,2,5,10)
# # Optim.AS_deplacer_groupe(6,2,5,10)
# # #
# Optim.AS_modifier_capacite(10, 1, 36)
# Optim.AS_modifier_capacite(10, 3, 36)   # AUX GROUPES DE LRC
# Optim.AS_modifier_capacite(10, 2, 36)
# Optim.AS_modifier_capacite(10, 4, 36)
# Optim.match()
# Optim.AD_afficher_carte_incompatibilites("and")
# # Optim.sauvegarde_UEs("edt.csv")
# Optim.eprouver_edt(nombreDeDossierGeneres=5)

#
# print Optim.capaciteTotaleAccueil
# Optim.AD_afficher_carte_augmentee_incompatibilites("and")
# #
# Optim.AS_ajouter_groupe(11,5,13,16)      #UN GROUPE DE 32 EN COMPLEX
# Optim.match()
#
# Optim.AS_deplacer_groupe(11, 3, 5, 13)
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

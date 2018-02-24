import numpy as np
import matplotlib.pyplot as plt
import csv
import copy
import os

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

            s += "\n\nEDT:\n{}".format(MainModel.EDT)

            return s


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



    def __str__(self):
        """Affiche les UES du Modele"""
        s = ""
        for intitule,ue in MainModel.DictUEs.items():
            s += str(ue)
        # print(MainModel.EDT)
        return s

    #     STOP HERE

    # def __init__(self,fetu,fedt_ue,fue,max_groupe):
    #     self.ListeDesUEs = ["null"] #A ACTUALISER
    #     self.model = Model("Affectation")
    #     self.max_groupe = max_groupe
    #     self.ens_ue,self.edt = self.read_ue_edt(fedt_ue)     #dictionnaire cle: intitule valeur:objet UE
    #     self.ens_etu = self.read_etu(fetu)  # liste d'objet ETU
    #     self.code_ue = self.encode_UE(fue)
    #     self.model.update()
    #     for ue in self.ens_ue:
    #         self.ens_ue[ue].add_constrs(self.model)
    #     self.model.update()
    #     self.model.optimize()
    #
    #     for etu in self.ens_etu:
    #         print(etu.get_affectation(self.model))
    #
    # def read_ue_edt(self,fue):
    #     f = open(fue)
    #     data = csv.DictReader(f)
    #     edt = [{i:set() for i in range(self.max_groupe+1)} for j in range(25)]
    #
    #     ens_ue = dict()
    #     for ue in data:
    #         ens_ue[ue["intitule"]] = UE(ue)
    #
    #         for i in [1,2] :
    #             if ue["cours"+str(i)] !="" :
    #                 edt[int(ue["cours"+str(i)])][0].add(int(ue["id_ue"]))
    #
    #
    #         for i in range(1,int(ue["nb_groupes"])+1):
    #             if ue["td"+str(i)] !="" :
    #                 edt[int(ue["td"+str(i)])][i].add(int(ue["id_ue"]))
    #
    #             if ue["tme"+str(i)] !="" :
    #                 edt[int(ue["tme"+str(i)])][i].add(int(ue["id_ue"]))
    #
    #     #supprimer les ensembles vide pour plus de lisibilite de l'edt
    #     edt_update = copy.deepcopy(edt)
    #     for i in range(25):
    #         for c,v in edt[i].items():
    #             if len(v) == 0:
    #                 edt_update[i].pop(c)
    #     edt = edt_update
    #     return ens_ue,edt
    #
    #
    # def encode_UE(self,filename):
    #     f = open(filename)
    #     data_file = csv.DictReader(f)
    #
    #     dico= dict()
    #     for ue in data_file:
    #         dico[ue['intitule']]=ue['num']
    #     return dico
    #
    # def read_etu(self,filename):  #le nom du parcours = nom fichier
    #     f = open(filename)
    #     data_file = csv.DictReader(f)
    #     id_etu=0
    #     Liste_Etu = list()
    #     for etu in data_file:
    #         id_etu+=1
    #         l = {'oblig':list(),'voeux':list()}
    #         for c,v in etu.items():
    #             if "oblig" in c and v != '':
    #                 l['oblig'].append(self.ens_ue[v])
    #             elif 'cons' in c and v !='':
    #                 l['voeux'].append(self.ens_ue[v])
    #         etu = ETU(id_etu, filename, l['oblig'], l['voeux'])
    #         etu.add_constr_ue_obl(self.model)
    #         etu.add_constr_ue_voeux(self.model)
    #         Liste_Etu.append(etu)
    #
    #     return Liste_Etu
    #
    


    
m = MainModel("../VOEUX", "edt.csv")
print(m)

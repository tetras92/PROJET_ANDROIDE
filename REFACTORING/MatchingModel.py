import random

import numpy as np
from gurobipy import *


class Etudiant:
        """ Classe representant un etudiant"""
        def __init__(self,csv_line, Parcours_Obj, optimizer):
            self.optimizer_Params = optimizer.Parameters
            self.optimizer = optimizer
            self.idRelatif = int(csv_line["num"])
            self.Parcours = Parcours_Obj
            self.indexParcours = Parcours_Obj.get_index()
            self.ue_obligatoires = [self.optimizer.DictUEs[csv_line["oblig"+str(id)]].get_id() for id in range(1, self.optimizer_Params.nbMaxUEObligatoires+1) if csv_line["oblig"+str(id)] != ""]
            self.ue_non_obligatoires = [self.optimizer.DictUEs[csv_line["cons"+str(id)]].get_id() for id in range(1, self.optimizer_Params.nbMaxUEConseillees+1) if csv_line["cons"+str(id)] != ""]
            self.nombreDeVoeux = len(self.ue_obligatoires) + len(self.ue_non_obligatoires)
            self.varName = "x_{}_{}".format(self.indexParcours, self.idRelatif)
            self.ListeDesInscriptions = list()
            # Parcours_Obj.rajouter_etudiant(self) #L'etudiant se rajoute a son parcours
            self.non_entierement_satisfait = False

        def s_inscrire_dans_son_parcours(self):
            self.Parcours.rajouter_etudiant(self)

        def gerer_variables_contraintes_ue_obligatoires(self, matchingModel):
            """ajoute les contraintes relatives aux ue obligatoires"""
            # objectif = modelGurobi.getObjective()
            modelGurobi = matchingModel.modelGurobi
            for id_ue in self.ue_obligatoires:
                var = modelGurobi.addVar(vtype=GRB.BINARY, lb=0, name="y_%d"%self.indexParcours+"_%d"%self.idRelatif+"_%d"%id_ue)
                # self.optimizer.ListedesVarY.append(var) #append("y_{}_{}_{}".format(self.indexParcours, self.idRelatif, id_ue))
                matchingModel.ListedesVarY.append(var)
                contrainte = LinExpr()
                for num_group in range(1, self.optimizer.ListeDesUEs[id_ue].get_nb_groupes()+1):
                    contrainte += modelGurobi.addVar(vtype=GRB.BINARY, lb=0, name=self.varName+"_%d"%id_ue+"_%d"%num_group)
                contrainte -= var

                # objectif += var

                modelGurobi.addConstr(var , GRB.EQUAL, 1)   #y_i_j = 1
                modelGurobi.addConstr(contrainte, GRB.EQUAL, 0)

            # modelGurobi.setObjective(objectif,GRB.MAXIMIZE) # NE PEUt-ON PAS S'EN PASSER
            modelGurobi.update()

        def gerer_variables_contraintes_ue_non_obligatoires(self, matchingModel):
            """ajoute les contraintes relatives aux ue non obligatoires"""
            # objectif = modelGurobi.getObjective()
            modelGurobi = matchingModel.modelGurobi
            varN = modelGurobi.addVar(vtype=GRB.BINARY, lb=0, name="n_%d"%self.indexParcours+"_%d"%self.idRelatif)
            matchingModel.ListedesVarN.append(varN)

            ListeCouranteVarYij = list()
            for id_ue in self.ue_non_obligatoires:
                var = modelGurobi.addVar(vtype=GRB.BINARY, lb=0, name="y_%d"%self.indexParcours+"_%d"%self.idRelatif+"_%d"%id_ue)
                ListeCouranteVarYij.append(var)
                # self.optimizer.ListedesVarY.append("y_{}_{}_{}".format(self.indexParcours, self.idRelatif, id_ue))
                matchingModel.ListedesVarY.append(var)
                contrainte = LinExpr()
                for num_group in range(1, self.optimizer.ListeDesUEs[id_ue].get_nb_groupes()+1):
                    contrainte += modelGurobi.addVar(vtype=GRB.BINARY, lb=0, name=self.varName+"_%d"%id_ue+"_%d"%num_group)
                contrainte -= var

                # objectif += var
                #VERIFIER LES CONTRAINTES DU MODELES
                modelGurobi.addConstr(contrainte, GRB.EQUAL, 0)
            #contrainte ETUDIANT ENTIEREMENT SATISFAIT
            # if ListeCouranteVarYij != []:
            modelGurobi.addConstr(quicksum(varYij for varYij in ListeCouranteVarYij) >= len(self.ue_non_obligatoires)*varN)
            # modelGurobi.setObjective(objectif,GRB.MAXIMIZE) # NE PEUt-ON PAS S'EN PASSER
            modelGurobi.update()

        def enregistrer_interet_pour_UE(self):
            for ue in self.ue_non_obligatoires + self.ue_obligatoires:
                self.optimizer.ListeDesUEs[ue].ajouterEtuInteresses(self.varName)

        def get_nombreDeVoeux(self):
            return self.nombreDeVoeux

        def get_index_parcours(self):
            return  self.indexParcours

        def get_varName(self):
            return self.varName

        def get_id_relatif(self):
            return self.idRelatif

        def entrer_inscription(self, ue, numeroGroup):
            if numeroGroup != 0:  #numeroGroup 0 signifie non accepte
                    chaine = self.optimizer.ListeDesUEs[ue].get_intitule()+str(numeroGroup)
                    self.optimizer.ListeDesUEs[ue].inscrire(str(self), numeroGroup)
            else:
                    chaine = self.optimizer.ListeDesUEs[ue].get_intitule()+"X"
                    self.non_entierement_satisfait = True

            if ue in self.ue_obligatoires:
                self.ListeDesInscriptions = [chaine] + self.ListeDesInscriptions
            else:
                self.ListeDesInscriptions.append(chaine)

        def get_ListeDesInscriptions(self):
            return self.ListeDesInscriptions

        def enregistrer_affectation(self, file):
            """enregistre l'etat des inscriptions de l'etudiant dans le fichier des affectations corresopondant a son parcours"""
            file.write(str(self.idRelatif)+" ")
            for aff in self.ListeDesInscriptions:
                file.write(aff + " ")
            file.write("\n")

        def get_contrat(self):
            return self.ue_obligatoires + self.ue_non_obligatoires

        def get_ue_obligatoires(self):
            return self.ue_obligatoires

        def get_ue_conseillees(self):
            return self.ue_non_obligatoires


        def generer_aleatoirement_mes_indifferences(self):
            def indifferenceValide(mesIndifferences):
                for i in range(len(mesIndifferences)):
                    if mesIndifferences[i] == self.ue_non_obligatoires[i]:
                        return False
                return True
            ListeDesUeConseilleesDeMonParcours = self.Parcours.get_Liste_ue_conseillees()
            self.mesIndifferences = np.random.choice(ListeDesUeConseilleesDeMonParcours, len(self.ue_non_obligatoires))

            while not indifferenceValide(self.mesIndifferences):
                self.mesIndifferences = np.random.choice(ListeDesUeConseilleesDeMonParcours, len(self.ue_non_obligatoires))


        def changer_mes_ues_non_obligatoires(self):
            self.non_entierement_satisfait = False
            self.ue_non_obligatoires_copy = [ue for ue in self.ue_non_obligatoires] #pour s'assurer qu'elle n'est pas incompatible

            def is_nouveau_contrat_incompatible(optimizer, ue_obligatoires, ue_non_obligatoires):
                LOblig = [optimizer.ListeDesUEs[ueO].get_intitule() for ueO in ue_obligatoires]
                LOblig.sort()
                LCons = [optimizer.ListeDesUEs[ueC].get_intitule() for ueC in ue_non_obligatoires]
                LCons.sort()
                try:                  #Juste pour les ecarts par rapport aux ues conseillees retenues dans parcours
                    # print(tuple(LOblig + LCons))
                    if self.Parcours.get_dico_configurations()[tuple(LOblig + LCons)] == 0:
                        # print "incompatibilite introduite"
                        return True
                except:
                    pass
                return False


            for i in range(len(self.ue_non_obligatoires)):
                if random.random() <= 0.5:# and ue_indifference_non_encore_introduite(self.ue_non_obligatoires,i, self.mesIndifferences[i]):
                    aux = self.mesIndifferences[i]
                    self.mesIndifferences[i] = self.ue_non_obligatoires[i]
                    self.ue_non_obligatoires[i] = aux
            if len(set(self.ue_non_obligatoires)) != len(self.ue_non_obligatoires):
                self.ue_non_obligatoires = self.ue_non_obligatoires_copy
                return

            if is_nouveau_contrat_incompatible(self.optimizer, self.ue_obligatoires, self.ue_non_obligatoires):
                self.ue_non_obligatoires = self.ue_non_obligatoires_copy
            # print "a la fin"
            # print self.mesIndifferences
            # print self.ue_non_obligatoires

        def get_statut(self):
            return self.non_entierement_satisfait

        def __str__(self):
            s = str(self.idRelatif)+"("+self.Parcours.get_intitule()+")"
            return s
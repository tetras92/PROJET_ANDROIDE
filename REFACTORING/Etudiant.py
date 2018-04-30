from gurobipy import *


class Etudiant:
        """ Classe representant un etudiant"""
        def __init__(self,csv_line, Parcours_Obj, optimizer):
            self.optimizer_Params = optimizer.Parameters
            self.optimizer = optimizer
            self.idRelatif = int(csv_line["num"])
            self.Parcours = Parcours_Obj
            self.indexParcours = int(csv_line["index"])
            self.ue_obligatoires = [self.optimizer.DictUEs[csv_line["oblig"+str(id)]].get_id() for id in range(1, self.optimizer_Params.nbMaxUEObligatoires+1) if csv_line["oblig"+str(id)] != ""]
            self.ue_non_obligatoires = [self.optimizer.DictUEs[csv_line["cons"+str(id)]].get_id() for id in range(1, self.optimizer_Params.nbMaxUEConseillees+1) if csv_line["cons"+str(id)] != ""]
            self.nombreDeVoeux = len(self.ue_obligatoires) + len(self.ue_non_obligatoires)
            self.varName = "x_{}_{}".format(self.indexParcours, self.idRelatif)
            self.ListeDesInscriptions = list()
            Parcours_Obj.rajouter_etudiant(self) #L'etudiant se rajoute a son parcours


        def gerer_variables_contraintes_ue_obligatoires(self,modelGurobi):
            """ajoute les contraintes relatives aux ue obligatoires"""
            # objectif = modelGurobi.getObjective()

            for id_ue in self.ue_obligatoires:
                var = modelGurobi.addVar(vtype=GRB.BINARY, lb=0, name="y_%d"%self.indexParcours+"_%d"%self.idRelatif+"_%d"%id_ue)
                self.optimizer.ListedesVarY.append("y_{}_{}_{}".format(self.indexParcours, self.idRelatif, id_ue))
                contrainte = LinExpr()
                for num_group in range(1, self.optimizer.ListeDesUEs[id_ue].get_nb_groupes()+1):
                    contrainte += modelGurobi.addVar(vtype=GRB.BINARY, lb=0, name=self.varName+"_%d"%id_ue+"_%d"%num_group)
                contrainte -= var

                # objectif += var
                self.optimizer.objectif1 += var

                modelGurobi.addConstr(var , GRB.EQUAL, 1)   #y_i_j = 1
                modelGurobi.addConstr(contrainte, GRB.EQUAL, 0)

            # modelGurobi.setObjective(objectif,GRB.MAXIMIZE) # NE PEUt-ON PAS S'EN PASSER
            modelGurobi.update()

        def gerer_variables_contraintes_ue_non_obligatoires(self, modelGurobi):
            """ajoute les contraintes relatives aux ue non obligatoires"""
            # objectif = modelGurobi.getObjective()
            varN = modelGurobi.addVar(vtype=GRB.BINARY, lb=0, name="n_%d"%self.indexParcours+"_%d"%self.idRelatif)
            self.optimizer.ListedesVarN.append(varN)

            ListeCouranteVarYij = list()
            for id_ue in self.ue_non_obligatoires:
                var = modelGurobi.addVar(vtype=GRB.BINARY, lb=0, name="y_%d"%self.indexParcours+"_%d"%self.idRelatif+"_%d"%id_ue)
                ListeCouranteVarYij.append(var)
                self.optimizer.ListedesVarY.append("y_{}_{}_{}".format(self.indexParcours, self.idRelatif, id_ue))
                contrainte = LinExpr()
                for num_group in range(1, self.optimizer.ListeDesUEs[id_ue].get_nb_groupes()+1):
                    contrainte += modelGurobi.addVar(vtype=GRB.BINARY, lb=0, name=self.varName+"_%d"%id_ue+"_%d"%num_group)
                contrainte -= var

                # objectif += var
                self.optimizer.objectif1 += var
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
                    self.optimizer.count += 1
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

                    # pattern = ""
                    # ListeTrieeDesUE = self.ue_obligatoires + self.ue_non_obligatoires
                    # ListeTrieeDesUE.sort()
                    # # print(ListeTrieeDesUE)
                    # for ue in ListeTrieeDesUE:
                    #     pattern += self.optimizer.ListeDesUEs[ue].get_intitule() + " "
                    #
                    # self.optimizer.DictionnaireDesInsatisfactionsParParcours[self.parcours].append([str(self),ListeTrieeDesUE]) #remplacer ListeTrieeDesUEs par pattern if pertinent
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

        def get_contrat(self):
            return self.ue_obligatoires + self.ue_non_obligatoires

        def get_ue_obligatoires(self):
            return self.ue_obligatoires

        def get_ue_conseillees(self):
            return self.ue_non_obligatoires

        def __str__(self):
            s = str(self.idRelatif)+"("+self.Parcours.get_intitule()+")"
            return s

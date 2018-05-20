from gurobipy import *

from HelpingFunctions import *


class CompatibilityModel():

    def __init__(self, ListeVoeux, optimizer):
        """Initialise le model principal A COMPLeTER"""

        self.ListeDesUEs = optimizer.ListeDesUEs
        self.EnsIncompatibilites = optimizer.EnsIncompatibilites


        self.modelGurobi = Model("MODELE DE COMPATIBILITE (PAR DAK)")

        # self.ListeVarObj = list()

        self.ListeVoeux = [optimizer.DictUEs[voeu] for voeu in ListeVoeux]
        self.ListeVoeuxId = [Ue.get_id() for Ue in self.ListeVoeux]

        for ue_ in self.ListeVoeuxId:#range(1, len(CompatibilityModel.ListeDesUEs)):
            self.ListeDesUEs[ue_].EnsEtuInteresses.add("x")

        self.instancier_var_Xij()



    def instancier_var_Xij(self): #GREAT CE 20/04
        self.modelGurobi.setParam( 'OutputFlag', False )
        self.LVarXij = list()

        for voeuUE in self.ListeVoeux:
            for idG in range(1, voeuUE.get_nb_groupes()+1):
                #cREATION DES VARIABLES XIJ
                # print (idG, voeuUE)
                var = self.modelGurobi.addVar(vtype=GRB.BINARY, lb=0, name="x_%d"%voeuUE.get_id()+"_%d"%idG)
                self.LVarXij.append(var)
            self.modelGurobi.update()

        for Incompatibilite in self.EnsIncompatibilites:
            Incompatibilite.m_a_j_EnsEtuConcernes()
            Incompatibilite.ajouterContrainteModeleGurobi(self.modelGurobi)


    def resoudre(self):

        L_L_Groupe_ListeVoeux = [[i + 1 for i in range(self.ListeDesUEs[ueId].get_nb_groupes())] for ueId in self.ListeVoeuxId]
        L_Combi = produit_cartesien_mult(L_L_Groupe_ListeVoeux)

        nbConfig = len(L_Combi)          #nombre Max
        for L_gr_combi in L_Combi:
            #cREATION DES VARIABLES N_I
            varname = "n"
            for idG in L_gr_combi:
                varname = varname + "_" + str(idG)
            var = self.modelGurobi.addVar(vtype=GRB.BINARY, lb=0, name=varname)
            # CompatibilityModel.modelGurobi.update()

            # self.ListeVarObj.append(var)
            self.modelGurobi.update()

            Z = zip(L_gr_combi, self.ListeVoeuxId)
            # print Z
            cst1 = self.modelGurobi.addConstr(quicksum(self.modelGurobi.getVarByName("x_%d"%ue+"_%d"%gr) for gr,ue in Z) >= len(self.ListeVoeux)*var)
            cst2 = self.modelGurobi.addConstr(var, GRB.EQUAL, 1)
            #Pas d'objectif: juste un modele de realisabilite
            self.modelGurobi.update()
            self.modelGurobi.optimize()

            status = self.modelGurobi.Status
            if status == GRB.Status.INFEASIBLE:
                # print [self.ListeDesUEs[ueI].get_intitule() for ueI in self.ListeVoeuxId]
                nbConfig -= 1
            else:
                return [self.ListeDesUEs[ueI].get_intitule() for ueI in self.ListeVoeuxId], 1   #soi-disant au moins un

            self.modelGurobi.reset()
            self.modelGurobi.remove(var)
            self.modelGurobi.remove(cst1)
            self.modelGurobi.remove(cst2)
            self.modelGurobi.update()
            # print(cst)
        ListeVoeux = [self.ListeDesUEs[ueI].get_intitule() for ueI in self.ListeVoeuxId]
        return ListeVoeux, nbConfig
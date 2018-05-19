import csv

from gurobipy import *


class ModelEffectif:

    nombreMaxGroupesParUE = 5
    nombreMaxUEObligatoiresParParcours = 3
    nombreMaxUEConseilleesParParcours = 8
    modelGurobi = Model("MODELEFFECTIF (PAR DAK)")

    def __init__(self, fichierParcours, fichierUEs):
        self.dictCapacitesUE = dict()
        self.dictProbaConseilles = dict()
        self.dictParcoursUEObligatoires = dict()
        self.setParcours = set()
        fileUE = open(fichierUEs, "r")
        self.initialiser_dictCapacitesUE(fileUE)
        self.dictProbaConseilles = self.initialiser_dictProbaConseilles()
        fileParcours = open(fichierParcours, "r")
        self.m_a_j_dictParcoursObligatoiresEtdictProbaConseilles(fileParcours)
        # print len(self.setParcours)

        self.ajouter_var_effectifs_parcours()
        # print ModelEffectif.modelGurobi.NumVars

        self.ajouter_contrainte_capacite_par_ue()
        # self.ajouter_contrainte_Min()
        self.ajouterObjectif()

        self.resoudre()
        print self.dictCapacitesUE
        print self.dictProbaConseilles
        print self.dictParcoursUEObligatoires
        # for csv_line in data:




    def initialiser_dictCapacitesUE(self, fileUE):
        data = csv.DictReader(fileUE)
        for csv_line in data:
            self.dictCapacitesUE[csv_line["intitule"]] = sum([int(csv_line["capac"+str(i)]) for i in range(1,ModelEffectif.nombreMaxGroupesParUE+1) if csv_line["capac"+str(i)] != ""])

        somme = 0
        for n, p in self.dictCapacitesUE.items():
            somme += p
        print "cumul", somme

    def initialiser_dictProbaConseilles(self):
        return {ue : list() for ue in self.dictCapacitesUE}

    def m_a_j_dictParcoursObligatoiresEtdictProbaConseilles(self, fileParcours):
        self.dictParcoursUEObligatoires = {ue : list() for ue in self.dictCapacitesUE}
        data = csv.DictReader(fileParcours)
        for csv_line in data:
            nom_parcours = csv_line["parcours"]
            self.setParcours.add(nom_parcours)
            ListeUEObligatoires = [csv_line["oblig" + str(i)] for i in range(1, ModelEffectif.nombreMaxUEObligatoiresParParcours + 1) if csv_line["oblig" + str(i)] != ""]
            for ue in ListeUEObligatoires:
                self.dictParcoursUEObligatoires[ue].append(nom_parcours)
            ListeUECOnseillees = [csv_line["cons" + str(i)] for i in range(1, ModelEffectif.nombreMaxUEConseilleesParParcours + 1) if csv_line["cons" + str(i)] != ""]
            ListeProbaUEConseillees = [float(csv_line["Pcons" + str(i)]) for i in range(1, ModelEffectif.nombreMaxUEConseilleesParParcours + 1) if csv_line["Pcons" + str(i)] != ""]
            for i in range(len(ListeUECOnseillees)):
                self.dictProbaConseilles[ListeUECOnseillees[i]].append((nom_parcours, ListeProbaUEConseillees[i]))

    def ajouter_var_effectifs_parcours(self):
        # print self.setParcours
        for parcours in self.setParcours:
            # print parcours
            var = ModelEffectif.modelGurobi.addVar(vtype=GRB.INTEGER, name=parcours)
        ModelEffectif.modelGurobi.update()

    def ajouter_contrainte_capacite_par_ue(self):
        for ue, ListeCouple in self.dictProbaConseilles.items():
            Constr = LinExpr()
            for parcours, proba in ListeCouple:

                Constr += proba*ModelEffectif.modelGurobi.getVarByName(parcours)
            ListeParcoursOuUEEstObligatoire = self.dictParcoursUEObligatoires[ue]
            for parcours in ListeParcoursOuUEEstObligatoire:
                Constr += ModelEffectif.modelGurobi.getVarByName(parcours)

            ModelEffectif.modelGurobi.addConstr(Constr <= self.dictCapacitesUE[ue], name=ue)

            ModelEffectif.modelGurobi.update()

    def ajouter_contrainte_Min(self):

        varMin = ModelEffectif.modelGurobi.addVar(vtype=GRB.INTEGER, name="Min")
        ModelEffectif.modelGurobi.update()
        for var in ModelEffectif.modelGurobi.getVars():
            ModelEffectif.modelGurobi.addConstr(varMin <= var)
        ModelEffectif.modelGurobi.update()


    def ajouterObjectif(self):
        # for c in ModelEffectif.modelGurobi.getConstrs():
        #     print c

        for const in ModelEffectif.modelGurobi.getConstrs():
            print const

        objectif = ModelEffectif.modelGurobi.getObjective()
        # # objectif += ModelEffectif.modelGurobi.getVarByName('dac')
        for var in ModelEffectif.modelGurobi.getVars():
            objectif += var
        print objectif
        # self.modelGurobi.NumObj = 2
        # objectif1 = ModelEffectif.modelGurobi.getVarByName("Min")
        # objectif2 = LinExpr()
        # for var in ModelEffectif.modelGurobi.getVars():
        #     if var.VarName != "Min":
        #         objectif2 += var
        ModelEffectif.modelGurobi.setParam( 'OutputFlag', False)
        ModelEffectif.modelGurobi.update()
        # self.modelGurobi.setObjectiveN(objectif1,0,1)
        # self.modelGurobi.setObjectiveN(objectif2,1,0)
        # self.modelGurobi.modelSense = -1
        # ModelEffectif.modelGurobi.optimize()


        ModelEffectif.modelGurobi.setObjective(objectif,GRB.MAXIMIZE)


    def resoudre(self):
        ModelEffectif.modelGurobi.optimize()
        for var in ModelEffectif.modelGurobi.getVars():
            print var
        print ModelEffectif.modelGurobi.getObjective()

m = ModelEffectif("parcours8PC.csv", "edt.csv")


from gurobipy import *
import csv
class MatchingModel:

    def __init__(self, optimizer, equilibre=True):
        self.optimizer = optimizer
        self.Params = optimizer.Parameters
        self.modelGurobi = Model("OPTIMISATION DES INSCRIPTIONS AUX UE (PAR DAK)")
        self.tauxEquilibre = self.Params.tauxEquilibre
        self.ListeDesUEs = optimizer.ListeDesUEs
        self.EnsIncompatibilites = optimizer.EnsIncompatibilites
        self.ListeDesEtudiants = optimizer.ListeDesEtudiants
        self.ListeDesParcours = optimizer.ListeDesParcours
        self.objectif1 = LinExpr()
        self.objectif2 = LinExpr()
        self.numeroModele = optimizer.iModelAlea

        #Contraintes s'appliquant aux etudiants
        for Etu in self.ListeDesEtudiants:
            Etu.gerer_variables_contraintes_ue_non_obligatoires(self.modelGurobi)
            Etu.gerer_variables_contraintes_ue_obligatoires(self.modelGurobi)
        #Fin Contraintes s'appliquant aux etudiants

        #Contraintes d'incompatibilite
        for Incomp in self.EnsIncompatibilites:
            Incomp.ajouterContrainteModeleGurobi(self.modelGurobi)
        #Fin Contraintes d'incompatibilite

        #Contraintes d'UE (capacite)
        for Ue in self.ListeDesUEs:
            Ue.ajouterContrainteCapaciteModelGurobi(self.modelGurobi)
        #Fin Contraintes d'UE (capacite)

        #Contraintes d'UE (Equilibre)
        if equilibre:
            for Ue in self.ListeDesUEs:
                Ue.ajouterContraintesEquilibre(self.modelGurobi)
        #Contraintes d'UE (Equilibre)

        self.nombreTotalDemandesInscriptions = len(self.optimizer.ListedesVarY)
        self.nombreTotalEtudiants = len(self.optimizer.ListedesVarN)
        self.capaciteTotaleAccueilUEs = self.optimizer.capaciteTotaleAccueil

    def match(self):
        self.modelGurobi.NumObj = 2
        self.modelGurobi.setParam( 'OutputFlag', False)

        self.objectif1 = quicksum(var for var in self.optimizer.ListedesVarY)
        self.objectif2 = quicksum(var for var in self.optimizer.ListedesVarN)

        self.modelGurobi.setObjectiveN(self.objectif1,0,1)
        self.modelGurobi.setObjectiveN(self.objectif2,1,0)

        self.modelGurobi.modelSense = -1        #MAXIMIZE

        self.modelGurobi.optimize()
        self.modelGurobi.setParam(GRB.Param.ObjNumber, 0)
        self.objectif1_Value = self.modelGurobi.ObjNVal           #Nombre d'inscriptions satisfaites
        self.modelGurobi.setParam(GRB.Param.ObjNumber, 1)
        self.objectif2_Value = self.modelGurobi.ObjNVal           #Nombre d'etudiants entierement satisfaits


    def traitement_resolution(self, path=''):
        self.charge = round(100.0*self.objectif1_Value/self.nombreTotalDemandesInscriptions,2)
        self.proportionSatisfactionY =  round(100.*self.objectif1_Value/self.nombreTotalDemandesInscriptions, 2)
        self.proportionSatisfactionN =  round(100.*self.objectif2_Value/self.nombreTotalEtudiants, 2)
        for varName in self.optimizer.ListedesVarY:
            # print (varName)
            if self.modelGurobi.getVarByName(varName).x == 1:
                indexParcours, idRelatif, ue = varName[2:].split('_')
                self.ListeDesUEs[int(ue)].ajouterUnInscrit()
                currentEtudiant = self.ListeDesParcours[indexParcours].get_mes_etudiants()[idRelatif]
                numGroup = 1

                while self.modelGurobi.getVarByName(currentEtudiant.get_varName()+"_%d"%int(ue)+"_%d"%numGroup).x == 0:
                    numGroup += 1
                currentEtudiant.entrer_inscription(int(ue), numGroup)
            else:
                indexParcours, idRelatif, ue = varName[2:].split('_')
                self.ListeDesUEs[int(ue)].signalerNonInscrit(indexParcours, idRelatif)
                currentEtudiant = self.ListeDesParcours[indexParcours].get_mes_etudiants()[idRelatif]
                currentEtudiant.entrer_inscription(int(ue), 0)

        for varName in self.optimizer.ListeDesVarN:
            if self.modelGurobi.getVarByName(varName).x == 0:
                indexParcours, idRelatif = varName[2:].split('_')
                self.ListeDesParcours[indexParcours].signalerUnProblemeDinscription(idRelatif)

        if path != '':
            try:
                affectationDirectory = path + str(self.numeroModele)+"_MATCHING/"
                os.mkdir(affectationDirectory)
            except:
                pass
        for Parcours_Obj in self.ListeDesParcours:
            f = open(affectationDirectory + Parcours_Obj.get_intitule() + ".csv", "w")
            fieldnames = ["num"] + ["oblig"+str(i) for i in range(1,self.optimizer.Parameters.nbMaxUEObligatoires)] + ["cons"+str(i) for i in range(1,self.optimizer.Parameters.nbMaxUEConseillees)]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for Etu in Parcours_Obj.get_mes_Etudiants():
                csvLine = dict()
                csvLine["num"] = Etu.get_id_relatif()
                L_Oblig = Etu.get_ue_obligatoires()
                L_Cons = Etu.get_ue_conseillees()
                for o in range(len(L_Oblig)):
                    csvLine["oblig"+str(o+1)] = L_Oblig[o]
                for c in range(len(L_Cons)):
                    csvLine["cons"+str(c+1)] = L_Cons[c]
                writer.writerow(csvLine)

            f.close()


    def __str__(self):
        """Affiche les UES du Modele"""
        s = "**********OPTIMISATION DES INSCRIPTIONS AUX UE (PAR DAK)**********\n\n"
        s += "Nombre Total d'inscriptions a satisfaire : {} \n".format(self.nombreTotalDemandesInscriptions)
        s += "Nombre Maximal d'inscriptions pouvant etre satisfaites : {} \n".format(self.capaciteTotaleAccueilUEs)
        s += "Charge : {}% \nDesequilibre maximal autorise : {} %\n\n\t\t\t*LES RESULTATS D'AFFECTATION*\n".format(self.charge, self.tauxEquilibre*100)

        # proportionSatisfaction = round(100.0*MainModel.nbInscriptionsSatisfaites/len(MainModel.ListedesVarY),2)
        s += "Nombre d'inscriptions satisfaites : {} soit {}%\n".format(self.objectif1_Value, self.proportionSatisfactionY)
        s += "Nombre d'etudiants entierement satisfaits : {} soit {}%\n".format(self.objectif2_Value, self.proportionSatisfactionN)
        s += "Detail des inscriptions non satisfaites : \n\t\tNombre de demandes non satisfaites par parcours :\n\t\t\t"
        for Parcours_Obj in self.ListeDesParcours:
            s += Parcours_Obj.str_nb_etudiants_insatisfaits()

        s += "\n\t\t\tNombre de demandes non satisfaites par UE (**Saturee):\n\t\t\t"
        for Ue in self.ListeDesUEs:
            s += Ue.str_nb_non_inscrits()
        s += "\n\t\t\t*DETAIL DES AFFECTATIONS PAR UE*\n\n"


        for Ue in self.ListeDesUEs:
            s += str(Ue)


        return s






from gurobipy import *
import csv
class MatchingModel:

    def __init__(self, optimizer, equilibre=True):
        self.optimizer = optimizer
        self.Params = optimizer.Parameters
        self.modelGurobi = Model("OPTIMISATION DES INSCRIPTIONS AUX UE (PAR DAK)")
        self.tauxEquilibre = self.optimizer.tauxEquilibre
        self.ListeDesUEs = optimizer.ListeDesUEs
        self.EnsIncompatibilites = optimizer.EnsIncompatibilites
        self.ListeDesEtudiants = optimizer.ListeDesEtudiants
        self.ListeDesParcours = optimizer.ListeDesParcours
        self.objectif1 = LinExpr()
        self.objectif2 = LinExpr()
        self.identifiantModele = optimizer.iModelAlea
        self.ListedesVarY = list()
        self.ListedesVarN = list()

        #Contraintes s'appliquant aux etudiants
        for Etu in self.ListeDesEtudiants:
            Etu.enregistrer_interet_pour_UE()
            Etu.s_inscrire_dans_son_parcours()
            Etu.gerer_variables_contraintes_ue_non_obligatoires(self)#(self.modelGurobi)
            Etu.gerer_variables_contraintes_ue_obligatoires(self)#(self.modelGurobi)
        #Fin Contraintes s'appliquant aux etudiants

        #Contraintes d'incompatibilite
        for Incomp in self.EnsIncompatibilites:
            Incomp.m_a_j_EnsEtuConcernes()
            Incomp.ajouterContrainteModeleGurobi(self.modelGurobi)
        #Fin Contraintes d'incompatibilite

        #Contraintes d'UE (capacite)
        for Ue in self.ListeDesUEs[1:]:
            Ue.ajouterContrainteCapaciteModelGurobi(self.modelGurobi)
        #Fin Contraintes d'UE (capacite)

        #Contraintes d'UE (Equilibre)
        if equilibre:
            for Ue in self.ListeDesUEs[1:]:
                Ue.ajouterContraintesEquilibre(self.modelGurobi)
        #fIN Contraintes d'UE (Equilibre)

        #pour ANALYZER : UE SURDEMANDEES
        self.DictUeSurdemandees = dict()
        for Ue in self.ListeDesUEs[1:]:
            Ue.etat_demande(self.DictUeSurdemandees)

        self.nombreTotalDemandesInscriptions = len(self.ListedesVarY)#(self.optimizer.ListedesVarY)
        self.nombreTotalEtudiants = len(self.ListedesVarN)#(self.optimizer.ListedesVarN)
        self.capaciteTotaleAccueilUEs = self.optimizer.capaciteTotaleAccueil

    def match(self, path=''):
        self.modelGurobi.NumObj = 2
        self.modelGurobi.setParam( 'OutputFlag', False)

        self.objectif1 = quicksum(var for var in self.ListedesVarY) #(self.modelGurobi.getVarByName(var) for var in self.optimizer.ListedesVarY)
        self.objectif2 = quicksum(var for var in self.ListedesVarN)
        self.modelGurobi.setObjectiveN(self.objectif1,0,1)
        self.modelGurobi.setObjectiveN(self.objectif2,1,0)

        self.modelGurobi.modelSense = -1        #MAXIMIZE

        self.modelGurobi.optimize()

        self.modelGurobi.setParam(GRB.Param.ObjNumber, 0)
        self.objectif1_Value = self.modelGurobi.ObjNVal           #Nombre d'inscriptions satisfaites
        self.modelGurobi.setParam(GRB.Param.ObjNumber, 1)
        self.objectif2_Value = self.modelGurobi.ObjNVal           #Nombre d'etudiants entierement satisfaits

        self.traitement_resolution(path)
        return  self.objectif2_Value

    def traitement_resolution(self, path=''):
        self.charge = round(100.0*self.nombreTotalDemandesInscriptions/self.capaciteTotaleAccueilUEs,2)
        self.proportionSatisfactionY =  round(100.*self.objectif1_Value/self.nombreTotalDemandesInscriptions, 2)
        self.proportionSatisfactionN =  round(100.*self.objectif2_Value/self.nombreTotalEtudiants, 2)



        for var in self.ListedesVarY:
            varName = var.VarName
            # print (varName)
            if var.x == 1:
                indexParcours, idRelatif, ue = varName[2:].split('_')
                self.ListeDesUEs[int(ue)].ajouterUnInscrit()
                # print self.ListeDesParcours[int(indexParcours)].nom, len(self.ListeDesParcours[int(indexParcours)].get_mes_etudiants()), idRelatif
                currentEtudiant = self.ListeDesParcours[int(indexParcours)].get_mes_etudiants()[int(idRelatif)]
                numGroup = 1
                # print currentEtudiant, ue
                # try:
                while self.modelGurobi.getVarByName(currentEtudiant.get_varName()+"_%d"%int(ue)+"_%d"%numGroup).x == 0:
                    # print numGroup
                    numGroup += 1
                # except:
                #     print currentEtudiant.get_varName()+"_%d"%int(ue)+"_%d"%numGroup
                currentEtudiant.entrer_inscription(int(ue), numGroup)
            else:
                indexParcours, idRelatif, ue = varName[2:].split('_')
                self.ListeDesUEs[int(ue)].signalerNonInscrit(indexParcours, idRelatif)
                currentEtudiant = self.ListeDesParcours[int(indexParcours)].get_mes_etudiants()[int(idRelatif)]
                currentEtudiant.entrer_inscription(int(ue), 0)

        for var in self.ListedesVarN:
            if var.x == 0:
                varName = var.VarName
                indexParcours, idRelatif = varName[2:].split('_')
                self.ListeDesParcours[int(indexParcours)].signalerUnProblemeDinscription(int(idRelatif))

        if path != '':
            try:
                affectationDirectory = path + "MATCHING/" #path + str(self.identifiantModele)+"MATCHING/"
                os.mkdir(affectationDirectory)
            except:
                pass
            for Parcours_Obj in self.ListeDesParcours:
                f = open(affectationDirectory + Parcours_Obj.get_intitule() + ".csv", "w")
                fieldnames = ["num"] + ["oblig"+str(i) for i in range(1,self.optimizer.Parameters.nbMaxUEObligatoires + 1)] + ["cons"+str(i) for i in range(1,self.optimizer.Parameters.nbMaxUEConseillees + 1 )]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for Etu in Parcours_Obj.get_mes_etudiants()[1:]:
                    csvLine = dict()
                    csvLine["num"] = Etu.get_id_relatif()
                    L_inscriptions = Etu.get_ListeDesInscriptions()
                    L_Oblig = Etu.get_ue_obligatoires()
                    L_Cons = Etu.get_ue_conseillees()
                    for o in range(len(L_Oblig)):
                        csvLine["oblig"+str(o+1)] = L_inscriptions[o]
                    for c in range(len(L_Cons)):
                        csvLine["cons"+str(c+1)] = L_inscriptions[len(L_Oblig) + c]
                    writer.writerow(csvLine)

            f.close()
        #VERIFICATION DE L'EQUILIBRE DES GROUPES
        #On en profite POUR
        for Ue in self.ListeDesUEs[1:]:
            Ue.set_equilibre()
        self.calculer_nombre_total_contrats_incompatibles()


    def get_identifiantModele(self):
        return self.identifiantModele

    def get_charge(self):
        return self.charge

    def get_PsatisfactionY(self):
        return self.proportionSatisfactionY

    def get_PsatisfactionN(self):
        return self.proportionSatisfactionN

    def calculer_nombre_total_contrats_incompatibles(self):
        self.nombre_total_contrat_incompatible = 0
        for parc, eff in self.optimizer.dict_nombre_de_contrats_incompatibles_par_parcours.items():
            self.nombre_total_contrat_incompatible += eff

    def chaine_nombre_contrats_incompatible_par_parcours(self):
        s = ""
        L = list(self.optimizer.dict_nombre_de_contrats_incompatibles_par_parcours.keys())
        L.sort()
        for parc in L:
            s += "{}({})  ".format(parc, self.optimizer.dict_nombre_de_contrats_incompatibles_par_parcours[parc])
        return s

    def __str__(self):
        """Affiche les UES du Modele"""

        s = ""
        for i in range(1, len(self.ListeDesUEs)):
            s += str(self.ListeDesUEs[-i])
        s += "\t\t\t*** ^^ DETAIL DES AFFECTATIONS PAR UE ^^ ***"

        s += "\n{:150s}{}\n".format(" ", "^")
        # s += "\n{:150s}{}\n".format(" ", "^")
        if self.optimizer.modeleAleatoire:
            s += "\t\t\tDossier aleatoire n. {}\n\n".format(self.identifiantModele)
        s += "Nombre Total d'inscriptions a satisfaire : {} ".format(self.nombreTotalDemandesInscriptions)
        # s += "\n{:150s}{}\n".format(" ", "^")
        s += "Nombre Maximal d'inscriptions pouvant etre satisfaites : {}".format(self.capaciteTotaleAccueilUEs)
        # s += "\n{:150s}{}\n".format(" ", "^")
        s += "\nNombre total d'etudiants du master : {}".format(self.nombreTotalEtudiants)

        s += "\nCharge : {} % \nDesequilibre maximal autorise : {} %".format(self.charge, self.tauxEquilibre*100)
        s += "\n{:150s}{}\n".format(" ", "^")
        s += "Caracteristiques de l'EDT :\n\tNombre total de contrats incompatibles (de taille {}) : {}".format(self.optimizer.Parameters.TailleMaxContrat, self.nombre_total_contrat_incompatible)
        # s += "\n{:150s}{}\n".format(" ", "^")
        s += "\n\tPar parcours : {}".format(self.chaine_nombre_contrats_incompatible_par_parcours())
        # s += "\n\n\t\t\t*LES RESULTATS D'AFFECTATION*\n"
        s += "\n{:150s}{}\n".format(" ", "^")
        s += "\t\t\t** ^^ AUTRES INFORMATIONS ^^ **"
        s += "\n{:150s}{}\n".format(" ", "^")
        # s += "\n{:150s}{}\n".format(" ", "^")
        # proportionSatisfaction = round(100.0*MainModel.nbInscriptionsSatisfaites/len(MainModel.ListedesVarY),2)
        s += "Nombre d'inscriptions satisfaites : {} soit {}%\n".format(int(self.objectif1_Value), self.proportionSatisfactionY)
        s += "Nombre d'etudiants entierement satisfaits : {} soit {}%\n".format(int(self.objectif2_Value), self.proportionSatisfactionN)
        s += "Detail des inscriptions non satisfaites : \n\t\tNombre de demandes non satisfaites par parcours :\n\t\t\t"
        for Parcours_Obj in self.ListeDesParcours:
            s += Parcours_Obj.str_nb_etudiants_insatisfaits()
        s += "\n{:150s}{}\n".format(" ", "^")
        s += "\t\tNombre de demandes non satisfaites par UE (**Saturee):\n\t\t\t"
        for Ue in self.ListeDesUEs[1:]:
            s += Ue.str_nb_non_inscrits()
        # s += "\n\n\n\t\t\t*DETAIL DES AFFECTATIONS PAR UE*\n\n"
        s += "\n{:150s}{}\n".format(" ", "^")
        s += "\t\t\t\t\t** ^^ LES RESULTATS D'AFFECTATION ^^ **"
        s += "\n{:150s}{}\n".format(" ", "^")
        # s += "\n{:150s}{}\n".format(" ", "^")
        s += "\t\t\t*** ^^ DONNEES RECAPITULATIVES DE L'AFFECTATION ^^ ***"
        s += "\n{:150s}{}\n".format(" ", "^")
        # s += "\n{:150s}{}\n".format(" ", "^")
        # s += "\n{:150s}{}\n".format(" ", "^")
        # s += "\n{:150s}{}\n".format(" ", "^")

        s += "\033[0;32;40m ********** ^^^ OPTIMISATION DES INSCRIPTIONS AUX UE (PAR DAK) ^^^ **********"
        # for i in range(1, len(self.ListeDesUEs)):
        #     s += str(self.ListeDesUEs[-i])
        # for Ue in self.ListeDesUEs[1:]:
        #     s += str(Ue)
        return s






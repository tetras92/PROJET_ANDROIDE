from gurobipy import *


class UE:
        """Classe definissant une UE"""
        def __init__(self,csv_line,optimizer):
            self.optimizer_Params = optimizer.Parameters
            self.optimizer = optimizer
            self.id =int(csv_line["id_ue"])
            self.intitule = csv_line["intitule"]
            self.nb_groupes = int(csv_line["nb_groupes"])
            self.ListeCapacites = [int(csv_line["capac"+str(i)]) for i in range(1,int(self.nb_groupes)+1)]
            self.EnsEtuInteresses = set()
            self.ListeCreneauxCours = [int(csv_line["cours"+str(i)]) for i in range(1,self.optimizer_Params.nbMaxCoursParUE+1) if csv_line["cours"+str(i)] != ""]
            self.ListeCreneauxTdTme = [()]+[(csv_line["td"+str(i)],csv_line["tme"+str(i)]) for i in range(1,int(self.nb_groupes)+1)]
            self.ResumeDesAffectations = ["null"] + [set()]*self.nb_groupes
            self.nbInscrits = 0
            self.ListeNonInscrits = list()
            self.ListeEtudiantsGroupes = [list() for kk in range(self.nb_groupes+1)]
            self.capaciteTotale = sum(self.ListeCapacites)
            self.optimizer.capaciteTotaleAccueil += self.capaciteTotale
            self.equilibre = True

        def actualiseEDT(self, EDT):
            """MAJ de l'EDT"""
            for creneauCours in self.ListeCreneauxCours:
                EDT[creneauCours][0].add(self.id)
            for gr_i in range(1, self.nb_groupes+1):
                creneauTdTme = self.ListeCreneauxTdTme[gr_i]
                try:
                    EDT[int(creneauTdTme[0])][gr_i].add(self.id)      #Td
                    EDT[int(creneauTdTme[1])][gr_i].add(self.id)      #tme
                except:
                    pass

        def get_id(self):
            return self.id

        def get_capaciteTotale(self):
            return self.capaciteTotale

        def get_nb_groupes(self):
            return self.nb_groupes

        def ajouterEtuInteresses(self, name):
            self.EnsEtuInteresses.add(name)

        def getEnsEtu(self):
            return self.EnsEtuInteresses

        def ajouterContrainteCapaciteModelGurobi(self, modelGurobi):
            """ajoute toutes les contraintes de  capacites de groupe au modele"""
            for idGroup in range(1, self.nb_groupes+1):
                modelGurobi.addConstr(quicksum(modelGurobi.getVarByName(etu+"_%d"%self.id+"_%d"%idGroup) for etu in self.EnsEtuInteresses) <= self.ListeCapacites[idGroup-1])
            modelGurobi.update()

        def ajouterContraintesEquilibre(self, modelGurobi):
            for idGroup1 in range(1, self.nb_groupes+1):
                for idGroup2 in range(idGroup1+1, self.nb_groupes+1):
                    modelGurobi.addConstr(quicksum((1./self.ListeCapacites[idGroup1-1])*modelGurobi.getVarByName(etu+"_%d"%self.id+"_%d"%idGroup1) for etu in self.EnsEtuInteresses) + quicksum((-1./self.ListeCapacites[idGroup2-1])*modelGurobi.getVarByName(etu+"_%d"%self.id+"_%d"%idGroup2) for etu in self.EnsEtuInteresses) <= self.optimizer_Params.tauxEquilibre)
                    modelGurobi.addConstr(quicksum((1./self.ListeCapacites[idGroup1-1])*modelGurobi.getVarByName(etu+"_%d"%self.id+"_%d"%idGroup1) for etu in self.EnsEtuInteresses) + quicksum((-1./self.ListeCapacites[idGroup2-1])*modelGurobi.getVarByName(etu+"_%d"%self.id+"_%d"%idGroup2) for etu in self.EnsEtuInteresses) >= -1.*self.optimizer_Params.tauxEquilibre)
            modelGurobi.update()


        def affecterEtuGroup(self, parcours, idRelatif, idGroup):
            self.ResumeDesAffectations[idGroup].add((parcours, idRelatif))

        def ajouterUnInscrit(self):
            self.nbInscrits += 1

        def signalerNonInscrit(self, parcours, idRelatif):
            self.ListeNonInscrits.append((parcours, idRelatif))

        def get_intitule(self):
            return self.intitule

        def get_ListeDesCapacites(self):
            return self.ListeCapacites

        def inscrire(self, etuName, numeroGroupe):
                self.ListeEtudiantsGroupes[numeroGroupe].append(etuName)

        def str_nb_non_inscrits(self):
            if len(self.ListeNonInscrits) == 0:
                return ""
            s = ""
            if len(self.capaciteTotale) == self.nbInscrits:
                s += "** "
            s += self.intitule + "(" + str(len(self.EnsEtuInteresses) - self.nbInscrits) + " / " + str(len(self.capaciteTotale) - self.nbInscrits) + ")  "



        def get_nbInscrits(self):
            return self.nbInscrits

        def get_nbInteresses(self):
            return len(self.EnsEtuInteresses)

        def remise_a_zero(self):
            self.EnsEtuInteresses.clear()
            self.ResumeDesAffectations = ["null"] + [set()]*self.nb_groupes
            self.nbInscrits = 0
            self.ListeNonInscrits = list()
            self.ListeEtudiantsGroupes = [list() for kk in range(self.nb_groupes+1)]

        def set_equilibre(self):
            # print(self.intitule)
            for idL1 in range(1, self.nb_groupes):
                for idL2 in range(idL1+1, self.nb_groupes+1):
                    # print("groupe1", idL1, "groupe2", idL2)
                    difference = abs(1.0*len(self.ListeEtudiantsGroupes[idL1])/(1.0*self.ListeCapacites[idL1-1])- 1.0*len(self.ListeEtudiantsGroupes[idL2])/(1.0*self.ListeCapacites[idL2-1]))

                    if difference > self.optimizer_Params.tauxEquilibre:
                        self.equilibre = False

        def __str__(self):
            """ Retourne la chaine representant une UE"""
            s = "UE {} ({}) :\n\tNombre de groupes : {}\n\tCapacite totale d'accueil: {}\n\t".format(self.intitule, self.id, self.nb_groupes, sum(self.ListeCapacites))
            # equil = ["Oui", "Non"]
            if self.equilibre:
                s += "Equilibre? : Oui\n"
            else:
                s += "Equilibre? : Non\n"

            s += "\tNombre Etudiants interesses: {}\n\t".format(len(self.EnsEtuInteresses))
            s += "Nombre Etudiants effectivement inscrits : {}\n\t".format(self.nbInscrits)
            s += "Les ({}) Non-inscrits : ".format(len(self.ListeNonInscrits))
            for parcours, idRelatif in self.ListeNonInscrits:
                s += str(idRelatif)+"("+self.optimizer.ListeDesParcours[int(parcours)]+") "
            s += "\n\tLes Inscrits:\n"
            for numGroup in range(1, len(self.ListeEtudiantsGroupes)):
                s += "\t\tGroupe {} [{}/{}] : ".format(numGroup, len(self.ListeEtudiantsGroupes[numGroup]), self.ListeCapacites[numGroup-1])
                for etu in self.ListeEtudiantsGroupes[numGroup]:
                    s += etu + " "
                s += "\n"
            s+= "\n\n"


            return s

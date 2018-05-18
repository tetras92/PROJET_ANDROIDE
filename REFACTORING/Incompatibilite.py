from gurobipy import *

class Incompatibilite:
        """Classe definissant une incompatibilite"""
        def __init__(self, idUEI, idGroupK, idUEJ, idGroupL, optimizer):
            """Definit une incompatiblite de type ((idUEI, idGroupK),(idUEJ, idGroupL))"""
            self.optimizer = optimizer

            self.ueGroup1 = idUEI, idGroupK      #Un couple (UE, Group)
            self.ueGroup2 = idUEJ, idGroupL      #Un couple (UE, Group)
            self.ensEtuConcernes = set() # self.optimizer.ListeDesUEs[idUEI].getEnsEtu() & self.optimizer.ListeDesUEs[idUEJ].getEnsEtu()  #L'ensemble des etudiants auxquels s'applique l'incompatibilite (Etudiant sous la forme x_Parcous_idRelatif (des strings))
            self.vide = (len(self.ensEtuConcernes) == 0)    #Un booleen
            self.optimizer.nbTotalIncompatibilites += 1

        def __str__(self):
            """Retourne la chaine d'affichage de l'incompatibilite et l'effectif des etudiants concernes"""
            s = "Incompatibilite entre l'UE/Groupe {} et l'UE/Groupe {}\n\tNombre d'etudiants concernes: {}\n{}\n\n".format(self.ueGroup1, self.ueGroup2, len(self.ensEtuConcernes), self.ensEtuConcernes)

            return s

        def ajouterContrainteModeleGurobi(self, modelGurobi):
            if not self.vide:
                for etuName in self.ensEtuConcernes:
                    modelGurobi.addConstr(modelGurobi.getVarByName(etuName+"_%d"%self.ueGroup1[0]+"_%d"%self.ueGroup1[1]) + modelGurobi.getVarByName(etuName+"_%d"%self.ueGroup2[0]+"_%d"%self.ueGroup2[1]) <= 1)
                    modelGurobi.update()


        def m_a_j_EnsEtuConcernes(self):
            self.ensEtuConcernes = self.optimizer.ListeDesUEs[self.ueGroup1[0]].getEnsEtu() & self.optimizer.ListeDesUEs[self.ueGroup2[0]].getEnsEtu()
            self.vide = (len(self.ensEtuConcernes) == 0)
            # if not self.vide:
            #     print self.ensEtuConcernes

        # def reset_incompatibilite(self):
        #     #vide juste self.ensEtuConcernes
        #     self.ensEtuConcernes.clear()
        #     self.vide = (len(self.ensEtuConcernes) == 0)

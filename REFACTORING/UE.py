from gurobipy import *


class UE:
        """Classe definissant une UE"""
        colors = [1,2,5,6,112,164,7,9,14,37,70,63,96,166,124,100,209,12,190,155,81,64,127]
        def __init__(self,csv_line,optimizer):
            self.optimizer_Params = optimizer.Parameters
            self.optimizer = optimizer
            self.id =int(csv_line["id_ue"])
            self.color = str(self.colors[self.id - 1])#str(self.id+32)
            self.intitule = csv_line["intitule"]
            self.nb_groupes = int(csv_line["nb_groupes"])
            self.ListeCapacites = [int(csv_line["capac"+str(i)]) for i in range(1,int(self.nb_groupes)+1)]
            self.EnsEtuInteresses = set()
            self.ListeCreneauxCours = [int(csv_line["cours"+str(i)]) for i in range(1,self.optimizer_Params.nbMaxCoursParUE+1) if csv_line["cours"+str(i)] != ""]
            self.ListeCreneauxTdTme = [()]+[(csv_line["td"+str(i)],csv_line["tme"+str(i)]) for i in range(1,int(self.nb_groupes)+1)]
            self.nbInscrits = 0
            self.ListeNonInscrits = list()
            self.ListeEtudiantsGroupes = [list() for kk in range(self.nb_groupes+1)]

            self.capaciteTotale = sum(self.ListeCapacites)
            self.optimizer.capaciteTotaleAccueil += self.capaciteTotale
            self.equilibre = True
            self.groupes_supprimes = set()



        def get_code_couleur(self):
            return u"\033[38;5;"+self.color+"m"

        def intituleCOLOR(self,up=True):
            intitule = self.intitule
            if up:
                intitule = intitule.upper()
            return "\033[38;5;"+self.color+"m"+intitule+"\033[37;1m"

        def actualiseEDT(self, EDT):
            """MAJ de l'EDT"""
            for creneauCours in self.ListeCreneauxCours:
                # try:
                EDT[creneauCours][0].add(self.id)
                # except:
                #     pass
                    # print "Vous avez essayer d'ajouter un cours de {} au creneau {}. Creneau inexistant dans l'EDT.".format(self.intitule,creneauCours)

            for gr_i in range(1, self.nb_groupes+1):
                creneauTdTme = self.ListeCreneauxTdTme[gr_i]
                creneautd, creneautme = creneauTdTme #
                # try:
                if creneautd != '':
                    EDT[int(creneautd)][gr_i].add(self.id)      #Td
                if creneautme != '':
                    EDT[int(creneautme)][gr_i].add(self.id)      #tme
                # except:
                #     pass
                    # print "Vous avez essayer d'ajouter un TD/TME de {} au creneau {}. Creneau inexistant dans l'EDT.".format(self.intitule,creneauTdTme)

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
                    if idGroup1 not in self.groupes_supprimes and idGroup2 not in self.groupes_supprimes:
                        modelGurobi.addConstr(quicksum((1./self.ListeCapacites[idGroup1-1])*modelGurobi.getVarByName(etu+"_%d"%self.id+"_%d"%idGroup1) for etu in self.EnsEtuInteresses) + quicksum((-1./self.ListeCapacites[idGroup2-1])*modelGurobi.getVarByName(etu+"_%d"%self.id+"_%d"%idGroup2) for etu in self.EnsEtuInteresses) <= self.optimizer.tauxEquilibre)
                        modelGurobi.addConstr(quicksum((1./self.ListeCapacites[idGroup1-1])*modelGurobi.getVarByName(etu+"_%d"%self.id+"_%d"%idGroup1) for etu in self.EnsEtuInteresses) + quicksum((-1./self.ListeCapacites[idGroup2-1])*modelGurobi.getVarByName(etu+"_%d"%self.id+"_%d"%idGroup2) for etu in self.EnsEtuInteresses) >= -1.*self.optimizer.tauxEquilibre)
            modelGurobi.update()




        def ajouterUnInscrit(self):
            self.nbInscrits += 1

        def signalerNonInscrit(self, parcours, idRelatif):
            self.ListeNonInscrits.append((parcours, idRelatif))

        def get_intitule(self):
            return self.intitule

        def get_ListeDesCapacites(self):
            return self.ListeCapacites

        def inscrire(self, etuName, numeroGroupe):
            # try:
            self.ListeEtudiantsGroupes[numeroGroupe].append(etuName)
            # except:
            #     print "Inscription de l'etudiant {} a l'UE {} est impossible. Groupe {} inconnu.".format(etuName,self.intitule,numeroGroupe)

        def str_nb_non_inscrits(self):
            if len(self.ListeNonInscrits) == 0:
                return ""
            s = ""
            if self.capaciteTotale == self.nbInscrits:
                s += "** "
            s += self.intitule + "(" + str(len(self.EnsEtuInteresses) - self.nbInscrits) + " / " + str(self.capaciteTotale - self.nbInscrits) + ")  "
            return s


        #--------------------------------------------------------------#
        def ajouter_un_groupe(self, creneauTd, creneauTme, capacite):
            if creneauTme != creneauTd: #Les exceptions
                # numero_nouveau_groupe = 0
                # if len(self.groupes_supprimes) != 0:
                #     L = list(self.groupes_supprimes)
                #     L.sort()
                #     numero_nouveau_groupe = L[0]
                # if numero_nouveau_groupe != 0:
                #     self.ListeCreneauxTdTme[numero_nouveau_groupe-1] = (creneauTd, creneauTme)
                #     self.ListeCapacites[numero_nouveau_groupe-1] = capacite
                #     self.groupes_supprimes.remove(numero_nouveau_groupe)
                #     self.maj_capacite_totale()
                #     self.optimizer.capaciteTotaleAccueil += capacite
                #     return numero_nouveau_groupe

                self.ListeCreneauxTdTme.append((creneauTd, creneauTme))
                self.ListeCapacites.append(capacite)
                self.nb_groupes += 1
                self.maj_capacite_totale()
                self.optimizer.capaciteTotaleAccueil += capacite

                return self.nb_groupes

        def maj_capacite_totale(self):
            self.capaciteTotale = sum(self.ListeCapacites)

        def get_nbInscrits(self):
            return self.nbInscrits

        def get_nbInteresses(self):
            return len(self.EnsEtuInteresses)

        def restaurer_places_apres_affectation(self):
            # self.ResumeDesAffectations = ["null"] + [set()]*self.nb_groupes
            self.nbInscrits = 0
            self.ListeNonInscrits = list()
            self.ListeEtudiantsGroupes = [list() for kk in range(self.nb_groupes+1)]

        def remise_a_zero(self):
            self.EnsEtuInteresses.clear()
            self.restaurer_places_apres_affectation()

        def set_equilibre(self):
            # print(self.intitule)
            for idL1 in range(1, self.nb_groupes):
                if idL1 not in self.groupes_supprimes:
                    for idL2 in range(idL1+1, self.nb_groupes+1):
                        if idL2 not in self.groupes_supprimes:
                        # print("groupe1", idL1, "groupe2", idL2)
                            difference = abs(1.0*len(self.ListeEtudiantsGroupes[idL1])/(1.0*self.ListeCapacites[idL1-1])- 1.0*len(self.ListeEtudiantsGroupes[idL2])/(1.0*self.ListeCapacites[idL2-1]))

                            if difference > self.optimizer.tauxEquilibre:
                                self.equilibre = False
                                break

        def modifier_capacite_groupe(self, numeroGroupe, nouvelleCapacite):
            self.optimizer.capaciteTotaleAccueil -= self.ListeCapacites[numeroGroupe - 1]
            self.optimizer.capaciteTotaleAccueil += nouvelleCapacite
            self.ListeCapacites[numeroGroupe - 1] = nouvelleCapacite
            self.maj_capacite_totale()
            # if nouvelleCapacite == 0:
            #     self.groupes_supprimes.add(numeroGroupe)

        def supprimer_groupe(self, numero_groupe):
            self.ListeCreneauxTdTme.pop(numero_groupe)
            self.ListeCapacites.pop(numero_groupe-1)
            self.nb_groupes -= 1
            self.maj_capacite_totale()

        def modifier_creneau_cours(self, ancien_creneau, nouveau_creneau):
            pos_ancien_creneau = self.ListeCreneauxCours.index(ancien_creneau) #0 ou 1
            self.ListeCreneauxCours[pos_ancien_creneau] = nouveau_creneau

        def ue_sauvegarde(self):
            Dict_Ue = dict()
            Dict_Ue["id_ue"] = self.id
            Dict_Ue["intitule"] = self.intitule
            Dict_Ue["nb_groupes"] = self.nb_groupes - len(self.groupes_supprimes)

            numI = 1
            for capacite in self.ListeCapacites:
                if capacite != 0:
                    Dict_Ue["capac"+str(numI)] = capacite
                    numI += 1
            nbCours = 1
            for creneau_cours in self.ListeCreneauxCours:
                Dict_Ue["cours"+str(nbCours)] = creneau_cours
                nbCours += 1

            tdtmeId = 1
            id_a_inscrire = 1
            for creneautd,creneautme in self.ListeCreneauxTdTme[1:]:

                if tdtmeId not in self.groupes_supprimes:
                    Dict_Ue["td"+str(id_a_inscrire)] = creneautd
                    Dict_Ue["tme"+str(id_a_inscrire)] = creneautme
                    id_a_inscrire += 1
                tdtmeId += 1

            return Dict_Ue

        def etat_demande(self, D):
            D[self.intitule] = len(self.EnsEtuInteresses) - self.capaciteTotale

        def __str__(self):
            """ Retourne la chaine representant une UE"""
            s = u"\033[38;5;"+self.color+"m UE {} ({}) :\n\tNombre de groupes : {}\n\tCapacite totale d'accueil: {}\n\t".format(self.intitule, self.id, self.nb_groupes - len(self.groupes_supprimes), sum(self.ListeCapacites))
            if self.equilibre:
                s += "Equilibre? : Oui\n"
            else:
                s += "Equilibre? : Non\n"

            s += "\tNombre Etudiants interesses: {}\n\t".format(len(self.EnsEtuInteresses))
            s += "Nombre Etudiants effectivement inscrits : {}\n\t".format(self.nbInscrits)
            s += "Les ({}) Non-inscrits : ".format(len(self.ListeNonInscrits))
            for parcours, idRelatif in self.ListeNonInscrits:
                s += str(idRelatif)+"("+self.optimizer.ListeDesParcours[int(parcours)].get_intitule()+") "
            s += "\n\tLes Inscrits:\n"
            for numGroup in range(1, len(self.ListeEtudiantsGroupes)):
                s += "\t\tGroupe {} [{}/{}] : ".format(numGroup, len(self.ListeEtudiantsGroupes[numGroup]), self.ListeCapacites[numGroup-1])
                for etu in self.ListeEtudiantsGroupes[numGroup]:
                    s += etu + " "
                s += "\n"
            s+= "\n\n\033[37;1m"


            return s


        def print_groupe(self):
            s = ""
            s += "\t   Les Creneaux [Capacites]\n\n\t"
            for cours in self.ListeCreneauxCours:
                s += self.get_code_couleur()
                s += "\t{:6s}: {:4s}\n\t".format("Cours",str(cours))
                s += u"\033[37;1m"

            s += "\t"
            s += "-"*14
            s += "\n\t"
            #LES CRENEAUX
            for i in range(1, len(self.ListeCreneauxTdTme)):                                     #LES CRENEAUX
                td, tme = self.ListeCreneauxTdTme[i]
                #LES CRENEAUX
                s += self.get_code_couleur()
                s += "\t{:3s} {:2s}:{:4s}\n\t".format("Gr.", str(i), " [ "+str(self.ListeCapacites[i-1])+" ]")

                s += u"\033[37;1m"

                s += "\t{:5s} : {:4s}\n\t".format("TD", str(td))
                s += "\t{:5s} : {:4s}\n\t".format("TME", str(tme))
                s += "\t"
                s += "-"*14
                s += "\n\t"
            return s
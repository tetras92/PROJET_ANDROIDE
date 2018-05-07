import matplotlib.pyplot as plt
import os
import csv
import matplotlib
import random


class Analyzer:

    def __init__(self, optimizer):
        self.ListeMatchingModel = list()
        self.optimizer = optimizer
        self.dico_recapitulatif_interet_ue_conseillees_par_parcours = dict()

        self.id_subplot = 1

    def add_MatchingModel(self, MM):
        self.ListeMatchingModel.append(MM)


    def analyze(self):
        Liste_idMM = list()
        Liste_charge = list()
        Liste_satisfaction_Y = list()
        Liste_satisfaction_N = list()

        for MM in self.ListeMatchingModel:
            Liste_idMM.append(MM.get_identifiantModele())
            Liste_charge.append(MM.get_charge())
            Liste_satisfaction_N.append(MM.get_PsatisfactionN())
            Liste_satisfaction_Y.append(MM.get_PsatisfactionY())

        L_Y_copy = [val for val in Liste_satisfaction_Y]
        L_Y_copy.sort()
        L_N_copy = [val for val in Liste_satisfaction_N]
        L_N_copy.sort()
        labelY = '%Inscriptions_satisfaites. Min : {}% Mediane : {}% Max : {}%'.format(L_Y_copy[0], L_Y_copy[len(L_Y_copy)//2], L_Y_copy[-1])
        labelN = '%Etudiants_satisfaits. Min : {}% Mediane : {}% Max : {}%'.format(L_N_copy[0], L_N_copy[len(L_N_copy)//2], L_N_copy[-1])
        plt.scatter(Liste_charge, Liste_satisfaction_Y, c='y', label=labelY)

        plt.scatter(Liste_charge, Liste_satisfaction_N, c='r', label=labelN)

        for i in range(len(Liste_idMM)):
            plt.annotate(Liste_idMM[i], (Liste_charge[i], Liste_satisfaction_Y[i]))
        for i in range(len(Liste_idMM)):
            plt.annotate(Liste_idMM[i], (Liste_charge[i], Liste_satisfaction_N[i]))

        plt.title("Mesure de la resistance d'un EDT : Evolution des pourcentages de satisfaction en fonction de la charge.")
        plt.legend()
        plt.grid(True)
        plt.show()

    def calculer_interet_pour_ue_conseillees_par_parcours(self, dossierVoeux=''):
        if dossierVoeux == '':
            print "analyse des donnees courantes"
        else:
            for fichierVoeux in os.listdir(dossierVoeux):
                try: #POUR EVITER LES ERREURS DE SPLIT SUR LE DOSSIER DE VOEUX PAR PARCOURS
                    parcours = fichierVoeux.split('.')[1]
                    path = dossierVoeux+"/"+fichierVoeux
                    f_voeux = open(path)
                    data = csv.DictReader(f_voeux)
                    D = dict()
                    for ligneEtu in data:
                        ListeUEsConseilleesDeEtudiant = [ligneEtu["cons"+str(id)] for id in range(1, self.optimizer.Parameters.nbMaxUEConseillees+1) if ligneEtu["cons"+str(id)] != ""]
                        for ue in ListeUEsConseilleesDeEtudiant:
                            if ue not in D:
                                D[ue] = 1
                            else:
                                D[ue] += 1
                    self.dico_recapitulatif_interet_ue_conseillees_par_parcours[parcours] = D
                except:
                    print "Erreur lors de la lecture du dossier : {}".format(dossierVoeux)
                    pass
            for parcours, D in self.dico_recapitulatif_interet_ue_conseillees_par_parcours.items():
                self.generer_histogramme_des_interest(parcours, D)
            plt.show()

    def generer_histogramme_des_interest(self, parcours, D):
        Liste_ues = list()
        Liste_effectif = list()
        colorNames = matplotlib.colors.cnames.keys()
        colorNames = list(colorNames)
        color = random.randint(0,len(colorNames)-1)
        plt.figure(1)
        for ue, effectif in D.items():
            Liste_ues.append(ue)
            Liste_effectif.append(effectif)
        plt.subplot(3,3,self.id_subplot)
        self.id_subplot += 1
        plt.bar(range(len(Liste_ues)), Liste_effectif, width = 0.4, color=colorNames[color], label=parcours)# color=[colorNames[random.randint(0,len(colorNames)-1)] for i in range(len(Liste_effectif))])
        plt.xticks([x for x in range(len(Liste_effectif))],[str(Liste_ues[i])+"("+str(Liste_effectif[i])+")" for i in range(len(Liste_ues))], rotation=15)
        plt.legend()
        # plt.title("Mesure du choix des UE conseillees en fonction du parcours")
        # plt.title("Mesure du choix des UE conseillees en fonction du parcours : {}".format(parcours))
        # plt.show()

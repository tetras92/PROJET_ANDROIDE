import csv
import matplotlib
import matplotlib.pyplot as plt
import os
import random


class Analyzer:

    def __init__(self, optimizer):
        self.ListeMatchingModel = list()
        self.optimizer = optimizer
        self.dico_recapitulatif_interet_ue_conseillees_par_parcours = dict()
        self.id_subplot = 1
        self.colorNames = list(matplotlib.colors.cnames.keys())

    def add_MatchingModel(self, MM):
        self.ListeMatchingModel.append(MM)


    def analyze(self):
        self.dico_etat_demande_ue = {ue.intitule : 0 for ue in self.optimizer.ListeDesUEs[1:]}
        Liste_idMM = list()
        Liste_charge = list()
        Liste_satisfaction_Y = list()
        Liste_satisfaction_N = list()



        for MM in self.ListeMatchingModel:
            Liste_idMM.append(MM.get_identifiantModele())
            Liste_charge.append(MM.get_charge())
            Liste_satisfaction_N.append(MM.get_PsatisfactionN())
            Liste_satisfaction_Y.append(MM.get_PsatisfactionY())
            for ue, surbook in MM.DictUeSurdemandees.items():
                self.dico_etat_demande_ue[ue] += surbook

        L = list(self.dico_etat_demande_ue.keys())
        L.sort()
        plt.bar(range(len(L)), [self.dico_etat_demande_ue[ue] for ue in L], width = 0.4, color=[self.colorNames[random.randint(0,len(self.colorNames)-1)] for i in range(len(L))], edgecolor = 'black')
        plt.xticks([x for x in range(len(L))], L, rotation=15)
        plt.title("Analyse UE susceptibles d'etre saturees : Mesure de la sur-demande")
        plt.legend()
        plt.show()

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
            plt.suptitle("Mesure du choix des UE conseillees en fonction du parcours")
            plt.show(block=False)

    def generer_histogramme_des_interest(self, parcours, D):
        Liste_ues = list()
        Liste_effectif = list()

        color = random.randint(0,len(self.colorNames)-1)
        plt.figure(1)
        for ue, effectif in D.items():
            Liste_ues.append(ue)
            Liste_effectif.append(effectif)
        plt.subplot(3,3,self.id_subplot)
        self.id_subplot += 1
        plt.bar(range(len(Liste_ues)), Liste_effectif, width = 0.4, color=self.colorNames[color], edgecolor = 'black', label=parcours)# color=[colorNames[random.randint(0,len(colorNames)-1)] for i in range(len(Liste_effectif))])
        plt.xticks([x for x in range(len(Liste_effectif))],[str(Liste_ues[i])+"("+str(Liste_effectif[i])+")" for i in range(len(Liste_ues))], rotation=15)
        plt.legend()
        #
        # plt.title("Mesure du choix des UE conseillees en fonction du parcours : {}".format(parcours))
        # plt.show()

    def reset(self):
        self.ListeMatchingModel = list()
        self.dico_recapitulatif_interet_ue_conseillees_par_parcours = dict()
        self.id_subplot = 1
        self.dico_etat_demande_ue = dict()

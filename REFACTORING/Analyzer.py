import matplotlib.pyplot as plt

class Analyzer:

    def __init__(self, optimizer):
        self.ListeMatchingModel = list()
        self.optimizer = optimizer

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

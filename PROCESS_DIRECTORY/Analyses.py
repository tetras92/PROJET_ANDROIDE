
class Analyses:


    def __init__(self, ListeDesParcours, ListeDesUEs):
        self.nb_calculs = 0
        self.nb_graphes = 0
        self.ListeDesParcours = ListeDesParcours
        self.ListeDesUes = ListeDesUEs
        self.resumeDesInscriptionsNonSatisfaites = dict()

    def incrementer_nb_calculs(self):
        self.nb_calculs += 1

    def incrementer_nb_graphes(self):
        self.nb_graphes += 1

    def maj_resumeDesInscriptionsNonSatisfaites(self, ue, parcours, etu):
        """ue, parcours des entiers"""
        if ue not in self.resumeDesInscriptionsNonSatisfaites:
            self.resumeDesInscriptionsNonSatisfaites[self.ListeDesUes[ue]]#LIGNE A COMPLETER

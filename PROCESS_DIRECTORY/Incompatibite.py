

class Incompatibilite:

    #L : Liste des UEs definies dans le MainModel

    def __init__(self, idUEI, idGroupK, idUEJ, idGroupL):
        """Définit une incompatiblité de type ((idUEI, idGroupK),(idUEJ, idGroupL))"""

        #
        L = list()                                                          #A SUPPRIMER
        self.ueGroup1 = idUEI, idGroupK
        self.ueGroup2 = idUEJ, idGroupL
        self.ensEtuConcernes = L[idUEI].getEnsEtu() & L[idUEJ].getEnsEtu()  #getEnsEtu  à définir dans UE

    def __str__(self):
        """Retourne la chaîne d'affichage de l'incompatibilité et l'effectif des étudiants concernés"""
        s = "Incompatibilité entre l'UE/Groupe {} et l'UE/Groupe {}\n\tNombre d'étudiants concernés: {}\n\n".format(self.ueGroup1, self.ueGroup2, len(self.ensEtuConcernes))

        return s

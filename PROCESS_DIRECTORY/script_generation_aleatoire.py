from  MainModel import *
from Generateur_Voeux import *


if __name__ == "__main__":
    generateur = Generateur_Voeux("parcours.csv", "edt.csv")

    for i in range(2):
        dossierVoeux, ListeParcours = generateur.generer()
        m = MainModel(dossierVoeux, "edt.csv")

        m.resoudre()
        f = open(dossierVoeux+"_detail_affectation.txt", "w")
        f.write(str(m))
        m.remise_a_zero()
        f.close()

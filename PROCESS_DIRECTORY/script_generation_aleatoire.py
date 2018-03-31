from  MainModel import *
from Generateur_Voeux import *
import matplotlib.pyplot as plt

if __name__ == "__main__":
    # generateur = Generateur_Voeux("parcours8PC.csv", "edt.csv")
    generateur = Generateur_Voeux("parcours8PC_mapsi.csv", "edt.csv")
    Liste_charge = list()
    Liste_ProportionSatis = list()
    nbExecutions = 100
    # I = set()
    for i in range(nbExecutions):
        dossierVoeux, ListeParcours = generateur.generer()
        m = MainModel(dossierVoeux, "edt.csv")
        charge, p = m.resoudre()
        # for s in m.JCVV:
        #     L = list(s)
        #     L.sort()
        #     I.add(tuple(L))

        Liste_charge.append(charge)
        Liste_ProportionSatis.append(p)

        f = open(dossierVoeux+"_detail_affectation.txt", "w")
        f.write(str(m))
        m.remise_a_zero()
        f.close()

    # print(I)
    plt.scatter(Liste_charge, Liste_ProportionSatis)
    for i in range(nbExecutions):
        plt.annotate(str(i+1), (Liste_charge[i], Liste_ProportionSatis[i]))
    plt.show()


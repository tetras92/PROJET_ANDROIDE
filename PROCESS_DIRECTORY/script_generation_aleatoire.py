from  MainModel import *
from Generateur_Voeux import *
import matplotlib.pyplot as plt

if __name__ == "__main__":
    # generateur = Generateur_Voeux("parcours8PC.csv", "edt.csv")
    generateur = Generateur_Voeux("parcours8PC_1.csv", "edt.csv")
    Liste_charge = list()
    Liste_ProportionSatis = list()
    Liste_chargeE = list()
    Liste_ProportionSatisE = list()
    nbExecutions = 50
    # I = set()
    for i in range(nbExecutions):
        dossierVoeux, ListeParcours = generateur.generer()
        m = MainModel(dossierVoeux, "edt.csv")
        charge, p = m.resoudre()
        Liste_charge.append(charge)
        Liste_ProportionSatis.append(p)
        f = open(dossierVoeux+"_detail_affectation.txt", "w")
        f.write(str(m))
        f.close()
        m.remise_a_zero()
        #
        #
        mE = MainModel(dossierVoeux, "edt.csv", equilibre=True)
        chargeE, pE = mE.resoudre()
        Liste_chargeE.append(chargeE)
        Liste_ProportionSatisE.append(pE)
        f = open(dossierVoeux+"_detail_affectation_eq.txt", "w")
        f.write(str(mE))
        f.close()
        mE.remise_a_zero()







    # print(I)
    plt.scatter(Liste_charge, Liste_ProportionSatis)
    plt.scatter(Liste_chargeE, Liste_ProportionSatisE,c='g')
    #
    for i in range(nbExecutions):
        plt.annotate(str(i+1)+"O", (Liste_charge[i], Liste_ProportionSatis[i]))
    for i in range(nbExecutions):
        plt.annotate(str(i+1)+"#", (Liste_chargeE[i], Liste_ProportionSatisE[i]))
    #
    #
    #
    plt.show()
    #

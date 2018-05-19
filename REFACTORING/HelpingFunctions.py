#Modele d'un dictionnaire Creneau
def generer_model_dict_creneau(nbMaxGroupeParUE):
        modelDict = dict()
        modelDict[0] = set()
        for k in range(nbMaxGroupeParUE):
            modelDict[k+1] = set()
        return modelDict
#Fin Modele
def produit_cartesien(L1, L2):
    def f(a, L):
        if len(L) == 1:
            return [[a, L[0]]]
        return [[a, L[0]]] + f(a, L[1:])
    return [u for a in L1 for u in f(a, L2)]


def produit_cartesien_mult(LL):
    if len(LL) < 2:
        return []

    PC = produit_cartesien(LL[0], LL[1])

    def final(PC, LLR):
        if len(LLR) == 0:
            return PC
        PC = [couple+[elem] for couple in PC for elem in LLR[0]]
        return final(PC, LLR[1:])

    return final(PC, LL[2:])


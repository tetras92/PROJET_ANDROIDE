from gurobipy import *
import numpy as np
import matplotlib.pyplot as plt

class UE:
    
    def __init__(self,csv_line):
        self.id =int(csv_line["id_ue"])
        self.intitule = csv_line["intitule"]
        self.nb_gr = int(csv_line["nb_groupes"])
        self.cap_group = [int(csv_line["capac"+str(i)]) for i in range(1,int(self.nb_gr)+1)]
        self.ens_etu = list()
        
        
    def add_etu_to_ensEtu(self,no_etu,model):
         self.ens_etu.append(no_etu)
         
         
    def add_constr_capacity(self,id_gr,model):
        if len(self.ens_etu) != 0:
            model.addConstr(quicksum(model.getVarByName("x_%d"%i+"_%d"%self.id+"_%d"%id_gr) for i in self.ens_etu) <= self.cap_group[id_gr-1]) 
            model.update()

        
    def add_constrs(self,model):
        for i in range(1,self.nb_gr+1):
            self.add_constr_capacity(i,model)
        model.update()

    def getId(self):
        return self.id
        
    def getNbGr(self):
        return self.nb_gr
        
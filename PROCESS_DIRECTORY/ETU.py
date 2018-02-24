from gurobipy import *
import numpy as np
import matplotlib.pyplot as plt



class ETU:
    
    
    def __init__(self,id_etu,parcours,ue_obl,ue_voeux):
        self.id = id_etu
        self.parcours = parcours
        self.ue_obl = ue_obl  #objets UE
        self.ue_voeux = ue_voeux #objets UE
    
    
    def add_constr_ue_obl(self,model):
        constr = LinExpr()
        obj = model.getObjective()
       
        for ue in self.ue_obl :
            ue.add_etu_to_ensEtu(self.id,model)
            j,nb_gr = ue.getId(),ue.getNbGr()
            
            constr = 0           
            for k in range(1,nb_gr+1):            
                constr += model.addVar(vtype=GRB.BINARY, lb=0, name="x_%d"%self.id+"_%d"%j+"_%d"%k)
            obj += constr
            
            model.addConstr(constr , GRB.EQUAL, 1)

        model.setObjective(obj,GRB.MAXIMIZE)
        model.update()
    
    def add_constr_ue_voeu(self,ue,model):
        constr = LinExpr()
        constr = 0   
        obj = model.getObjective()
        j,nb_gr = ue.getId(),ue.getNbGr()
        
        ue.add_etu_to_ensEtu(self.id,model)
        
        for k in range(1,nb_gr+1):
            constr += model.addVar(vtype=GRB.BINARY, lb=0, name="x_%d"%self.id+"_%d"%j+"_%d"%k)
        obj += constr      
        model.addConstr(constr <= 1)

        model.setObjective(obj,GRB.MAXIMIZE)
        model.update()
    
    
    def add_constr_ue_voeux(self,model):
        for ue in self.ue_voeux:
            self.add_constr_ue_voeu(ue,model)
        model.update()

        
    def get_affectation(self,model):
        affectation =  list()
        for ue in self.ue_obl+self.ue_voeux:
            j,nb_gr = ue.getId(),ue.getNbGr()
            for k in range(1,nb_gr+1):
                if model.getVarByName("x_%d"%self.id+"_%d"%j+"_%d"%k).x == 1 :
                    affectation.append((j,k))
                    
        return affectation
        
        
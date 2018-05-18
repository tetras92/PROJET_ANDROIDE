import Tkinter
import os
import tkFileDialog

from DAK_Optimizer import DAK_Optimizer


# !/usr/bin/env python
# _*_ coding:utf-8 _*_


class Script():


    def __init__(self):
        os.system("clear")
        print u"\033[33;1mDAK_Optimizer Powered by DAK\n\n"


        self.dirname_dossier_voeux = ''
        # self.dirname_tout_dossier = ''
        self.optimizer = DAK_Optimizer()
        self.dernier_taux_equilibre = DAK_Optimizer.tauxEquilibre

        print "\t\tP-ANDROIDE : OPTIMISATION DES INSCRIPTIONS AUX UES (PAR DAK)\n\n"
        # while True:
        self.menu_chargement()
        # self.menu_principal()



    def appuyer_entree_pour_continuer(self):
        print "\t\t\"Entree\" pour Continuer.\n"
        raw_input(">>> ")


    def menu_chargement(self):

        valider = False
        self.file_edt = "..."
        self.file_parcours = "..."
        while not valider: #("..." in [self.file_parcours,self.file_edt]):
            s = u"\033[34;1m---------------------------- Chargement des fichiers ----------------------------\n\n" \
                u"\033[37;1m\t\t{:50s}{}\n\t\t{:50s}{}\n\n".format("(1) Charger le fichier EDT",self.file_edt,"(2) Charger le fichier decrivant les parcours",self.file_parcours)
            s += "\t\t(0) Quitter\n "
            print (s)
            if self.file_edt != "..." and self.file_parcours != "...":
                valider = True
                self.appuyer_entree_pour_continuer()
                continue

            root = Tkinter.Tk()
            root.withdraw()
            chargement = raw_input(">>> ")

            if chargement == '0':
                exit(0)
            elif chargement == '1':
                edtfile = tkFileDialog.askopenfilename(title="Veuillez selectionne le fichier EDT",filetypes=[('CSV', '.csv')])
                if edtfile != () :#and edtfile != "":
                    try:
                        self.optimizer.charger_edt(edtfile)
                        self.file_edt = edtfile #JUSTE POUR L'AFFICHAGE
                        print u"\033[32;1m\n============================ Chargement EDT termine =============================\n"
                    except:
                        print u"\033[31;1mERREUR SURVENUE LORS DU CHARGEMENT DU FICHIER EDT!\n"
                        self.file_edt = "..."
            elif chargement == '2':
                file_parcours = tkFileDialog.askopenfilename(title="Veuillez selectionne le fichier Parcours",filetypes=[('CSV', '.csv')])
                if file_parcours != () :#and file_parcours != "":
                    try:
                        self.optimizer.charger_parcours(file_parcours)
                        self.file_parcours = file_parcours
                        print u"\033[32;1m\n============== Chargement fichier descriptif des parcours termine ===============\n"
                    except:
                        print u"\033[31;1mERREUR SURVENUE LORS DU CHARGEMENT DU FICHIER DESCRIPTIF DES PARCOURS!\n"
                        self.file_parcours = "..."
            else:
                print u"\033[31;1mCommande incorrecte.\n\n"

        os.system("clear")
        self.menu_principal()




    def menu_principal(self):

        while True:
            #         "\t(6) Recharger un fichier EDT\t\t ( courant : {} ) \n\t(7) Recharger un fichier Parcours\t\t ( courant : {} ) \n\t(8) Recharger un dossier de voeux\t\t ( courant : {} )\n".format(file_edt,file_parcours,dir_dossier_voeux)+\

            print u"\n\n\033[34;1m__________________________________Menu principal__________________________________\n\n" + \
                 u"\033[37;1m\t(1) Charger un dossier de voeux et effectuer les inscriptions pedagogiques\n\t(2) Mesurer la resistance de l'EDT actif : Generation aleatoire de dossiers de voeux\n\t(3) EDT : Afficher, Modifier, Sauvegarder\n" \
                "\t(4) Contrats incompatibilites par parcours : Visualiser\n\n\t(5) Retour au Menu chargement\n\t(0) Quitter\nSaisir une valeur (0-5) : \n\n"

            choix = raw_input(">>> ")

            if choix == '0':
                exit(0)

            elif choix == '1':
                if self.charger_voeux() == False:
                    continue
                try:
                    self.optimizer.AD_interets_ue_conseillees_par_parcours(self.dirname_dossier_voeux)
                    print u"\n\n\033[32;1m* * * * * * * Generation du graphique representant les interets des etudiants aux UE non-obligatoires de leur parcours * * * * * * *\n\n\033[37;1m"
                except:
                    print u"\n\033[31;1mERREUR LORS DU CALCUL DE L'INTERET DES ETUDIANTS DE CHAQUE PARCOURS POUR LEURS UE NON-OBLIGATOIRES\n033[37;1m"
                try:
                    self.faire_le_matching()
                except:
                    print u"\n\033[31;1mERREUR LORS DE LA REALISATION DES INSCRIPTIONS PEDAGOGIQUES (MATCHING)\n\033[37;1m"

            elif choix == '2': #_________________________NEW
                self.eprouver_edt()

            elif choix == '3': #_________________________NEW             ICI CE 18/05

                def get_all_ue_name():
                    Liste_id_ues = list(self.optimizer.DictUEs.keys())
                    Liste_id_ues.sort()
                    s = "\n"
                    nb_ue = len(Liste_id_ues)
                    for ue,i in zip(Liste_id_ues,range(1,nb_ue + 1)):
                        s += "\t({}) {}\t\t".format(i,ue)
                        if ((i-1)%(nb_ue/2))==0:
                          s+="\n"
                    return s

                while True:
                    print"\n\n__________________________ Operation sur l'EDT __________________________\n\n\t(1) Afficher l'EDT\n\t(2) Modifications sur les groupes d'UE\n\t(3) Sauvegarder les modifications apportees sur l'EDT\n\t" \
                            "(0) Retour au Menu principal\n\n"
                    changement_edt = input(" >>> ")
                    if changement_edt == 1:
                        print self.optimizer.afficher_EDT()
                    elif changement_edt == 2:
                        print "\n\n_______________________ Modification des groupes d'UE _______________________\n\n"
                        intit_ue = get_all_ue_name()
                        while True:
                            print "\tVeuillez selectionner une UE a modifie : \n\n"+intit_ue
                            try:
                                ue_a_modifie = input(">>> ")
                            except:
                                print"im in expction input"
                                continue
                            break
                        if ue_a_modifie <= len(self.optimizer.DictUEs) or ue_a_modifie >0 :
                            while True:
                                print "\n\t(1) Ajouter un nouveau groupe\n\t(2) Supprimer un groupe\n\t(3) Modifier la capacite d'un groupe\n\t(0) Retour au menu precedent\n"
                                choix = raw_input(">>> ")
                                if choix == '1':
                                    self.ajouter_groupe(ue_a_modifie)
                                elif choix == '2':
                                    self.supprimer_groupe(ue_a_modifie)
                                elif choix == '3':
                                    self.modifier_capacite_groupe(ue_a_modifie)
                                elif choix == '0':
                                   break

                    elif changement_edt == 3:
                        self.sauvegarder()
                    elif changement_edt == 0:
                        break
                    else:
                        print u"\033[31;1\nCommande incorrecte.\n"


            elif choix == '4':
                print"_____________________ Afficher la carte d'incompatibilites dans un Parcours "

                parcours = raw_input("Veuillez indiquer le nom du parcours : ")
                if parcours !='':
                    taille = input(" Veuillez indiquez la taille : ")
                    self.optimizer.AD_afficher_carte_incompatibilites(parcours,taille)
            elif choix == '5':
                self.menu_chargement()


    def print_equilibrage(self):
        while True:
            print u"\033[34;1m\n\n____________ Option Equilibrage au sein des groupes de chaque UE ____________ \n\033[37;1m"
            option = raw_input("Choisir le pourcentage maximal de desequilibre a tolerer :\n\t(1) 5.0%\n\t(2) 10.0%\n\t(3) 20.0%\n\t(4) Sans equilibrage (100%)\n"
                            "\n\t(0) Retour au Menu Principal\n\"Entree\" pour {}% : \n >>> ".format(self.dernier_taux_equilibre*100))
            if option == '' or option == ():
                return -1
            option = int(option)
            if option not in range(5):          #NE PAS SORTIR TANT QUE VALEUR NON VALIDE SAISIE
                print u"\033[31;1mCommande incorrecte.\033[37;1m"
                return self.print_equilibrage()
        return option

    def rematcher(self):
        print "\n\033[37;1mSouhaitez-vous reeffectuer les inscriptions pedagogiques? (avec un autre pourcentage de desequilibre par exemple)\n\t(1) Oui\n\t(0) Non\nSaisir une valeur (0-1):"
        choix = raw_input(">>> ")
        if choix == '1':
            return True
        elif choix == '0':
            return False
        else:
            print "\033[31;1mCommande incorrecte.\033[37;1m"
            return self.rematcher()

    def faire_le_matching(self):
        # while True:
        options = self.print_equilibrage()
        if options == 1:
            self.optimizer.match(equilibre=True, tauxEquilibre=0.05)
            self.dernier_taux_equilibre = 0.05
        elif options == 2:
            self.optimizer.match(equilibre=True, tauxEquilibre=0.1)
            self.dernier_taux_equilibre = 0.1
        elif options == 3:
            self.optimizer.match(equilibre=True,tauxEquilibre=0.20)
            self.dernier_taux_equilibre = 0.20
        elif options == 4:
            self.optimizer.match(equilibre=True, tauxEquilibre=1)
            self.dernier_taux_equilibre = 1
        elif options == -1:
            self.optimizer.match(equilibre=True, tauxEquilibre=self.dernier_taux_equilibre)
        elif options == 0:
            return
        else:
            print u"\033[31;1mCommande incorrecte.\033[37;1m"
            self.faire_le_matching()
            return
        if self.rematcher():
            self.faire_le_matching()


    def charger_voeux(self):
        annuler = False
        while not annuler:
            print u"\033[34;1m\n\n____________________ Chargement du dossier des voeux ____________________\033[37;1m\n\n"
            # print "\t\n\n"
            root = Tkinter.Tk()
            root.withdraw()
            dossier_voeux = tkFileDialog.askdirectory(title =" Veuillez selectionner l'emplacement du dossier des voeux")

            if dossier_voeux != "":#dossier_voeux != () and
                try:
                    self.optimizer.traiter_dossier_voeux(dossier_voeux)
                    self.dirname_dossier_voeux = dossier_voeux
                    print u"\033[32;1m\n Dossier de voeux charge : {}\n\033[37;1m".format(self.dirname_dossier_voeux)
                except:
                    print u"\033[31;1mERREUR LORS DU CHARGEMENT DU DOSSIER DE VOEUX\033[37;1m"
                    return False

            else:
                annuler = True
                continue
            chargement = raw_input("\t(0) Retour au Menu Principal\n\n\"Entree\" pour realiser les affectations.\n>>> ")

            if chargement == '0':
                annuler = True
            elif chargement == '':
                break
            else :
                print u"\033[31;1mCommande incorrecte.\033[37;1m\n\n"
                continue

        return not annuler

    def eprouver_edt(self):
        annuler = False
        print u"\n\n\033[34;1m_________________________________ Eprouver l'EDT _________________________________\033[37;1m\n\n"+\
            u"\033[33;1mLes dossiers de voeux aleatoires generes sont stockes automatiquement dans le repertoire ~/VOEUX_RANDOM\033[37;1m\n"

        while not annuler:
            nbDossier = raw_input(u"\033[37;1mVeuillez selectionner le nombre de dossiers voeux a generer.\n"
                          "(1) {:3s} dossiers aleatoires (~ {} minute(s))\n(2) {:3s} dossiers aleatoires (~ {} minute(s))\n(3) {:3s} dossiers aleatoires (~ {} minute(s))\n"
                              "(4) {:3s} dossiers aleatoires (~ {} minute(s))\n(5) {:3s} dossiers aleatoires (~ {} minute(s))\n(6) {:3s} dossiers aleatoires (~ {} minute(s))\n"
                              "(0) Retour au Menu Principal\nSaisir une valeur (0-6) : ".format('20', 1, '50', 2, '75', 3, '100', 4, '150', 7, '200', 9))
            if nbDossier == '1':
                nbDossier = 20
            elif nbDossier == '2':
                nbDossier = 50
            elif nbDossier == '3':
                nbDossier = 75
            elif nbDossier == '4':
                nbDossier = 100
            elif nbDossier == '5':
                nbDossier = 150
            elif nbDossier == '6':
                nbDossier = 200
            elif nbDossier == '0':
                annuler = True
                continue
            else:
                print u"\033[31;1mCommande incorrecte.\033[37;1m\n\n"
                continue

            ##########################################################################################################""
            #MEME MODELE QUE LE MATCHING
            edt_eprouve = False
            while not edt_eprouve:
                option = self.print_equilibrage()
                if option == 1:
                    self.optimizer.eprouver_edt(nombreDeDossierGeneres=nbDossier,equilibre=True, tauxEquilibre=0.05)
                    edt_eprouve = True
                    self.dernier_taux_equilibre = 0.05
                elif option == 2:
                    self.optimizer.eprouver_edt(nombreDeDossierGeneres=nbDossier,equilibre=True)
                    edt_eprouve = True
                    self.dernier_taux_equilibre = DAK_Optimizer.tauxEquilibre
                elif option == 3:
                    self.optimizer.eprouver_edt(nombreDeDossierGeneres=nbDossier,equilibre=True,tauxEquilibre=0.20)
                    edt_eprouve = True
                    self.dernier_taux_equilibre = 0.20
                elif option == 4:
                    self.optimizer.eprouver_edt(nombreDeDossierGeneres=nbDossier,equilibre=True, tauxEquilibre=1)
                    edt_eprouve = True
                    self.dernier_taux_equilibre = 1
                elif option == -1:
                    self.optimizer.eprouver_edt(nombreDeDossierGeneres=nbDossier,equilibre=True, tauxEquilibre=self.dernier_taux_equilibre)
                elif option == 0:
                    annuler = True
                    break              #RETOURNE DANS LA BOUCLE DU MENU PRINCIPAL
            ##############################################################################################################

    def sauvegarder(self):
        root = Tkinter.Tk()
        root.withdraw()
        save_file_edt = tkFileDialog.asksaveasfile(title="Veuillez indiquer l'emplacement de la sauvegarde")
        if save_file_edt !='':
            print "save file  "+save_file_edt.name
            self.optimizer.sauvegarde_UEs(save_file_edt.name)
            print u"\033[32;1m============================== SAUVEGARDE REUSSIE ==============================\n\n\033[37;1m"
        else:
            print u"\033[31;1m!!!____ SAUVEGARDE ECHOUEE ____!!!\n\n\033[37;1m"

    def ajouter_groupe(self,id_ue):
        while True:
            print"\n\n___________________________ Ajouter un nouveau groupe _____________________________\n\n"
            print self.optimizer.ListeDesUEs[id_ue].print_groupe()+"\n\n"+\
                "Veuillez indiquer les creneaux TD, TME et la capacite du nouveau groupe.\nNB : Les creneaux sont numerotes de 1 a 25 (5 creneaux par jour ex: Mardi 10h45 - 12h45 est note 7)\n\n"
            try:
                creneau_td = input("Creneau TD  : ")
                creneau_tme = input("Creneau TME  : ")
                capacite = input("Capacite du groupe  : ")
            except:
                continue

            self.optimizer.AS_ajouter_groupe(id_ue, creneau_td, creneau_tme, capacite)
            print"\n============================ AJOUT ENREGISTRE ============================\n\n"
            print self.optimizer.ListeDesUEs[id_ue].print_groupe()
            break


    def supprimer_groupe(self,id_ue):
        while True:
            print"\n\n___________________________ Supprimer un groupe _____________________________\n\n"
            print self.optimizer.ListeDesUEs[id_ue].print_groupe()+"\n\n"
            try:
                numGroupe = input("Numero du groupe a supprimer  : ")
            except:
                continue
            self.optimizer.AS_supprimer_groupe(id_ue,numGroupe)
            print"\n============================ SUPPRESSION ENREGISTREE ============================\n\n"
            print self.optimizer.ListeDesUEs[id_ue].print_groupe()
            break


    def modifier_capacite_groupe(self,id_ue):
        while True:
            print"\n\n___________________________ Modifier capacite d'un groupe _____________________________\n\n"
            print self.optimizer.ListeDesUEs[id_ue].print_groupe()+"\n\n"
            try:
                numGroupe = input("Numero du groupe  : ")
                nouvelle_capacite = input("Nouvelle capacite du groupe : ")
            except:
                continue
            self.optimizer.AS_modifier_capacite(id_ue,numGroupe,nouvelle_capacite)
            print"\n\033[32;1m============================ MODIFICATION ENREGISTREE ============================\033[37;1m\n\n"
            print self.optimizer.ListeDesUEs[id_ue].print_groupe()
            break





Script()

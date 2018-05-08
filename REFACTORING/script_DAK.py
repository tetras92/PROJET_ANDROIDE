import Tkinter
import tkFileDialog

from DAK_Optimizer import DAK_Optimizer


# !/usr/bin/env python
# _*_ coding:utf-8 _*_


class Script():


    def __init__(self):
        print "DAK_Optimizer Powered by DAK"

        self.file_edt = ()
        self.file_parcours = ()
        self.dirname_dossier_voeux = ''
        # self.dirname_tout_dossier = ''
        self.optimizer = DAK_Optimizer()



        while True:
            print"__________________________________Bienvenue au DAK_OPTIMIZER__________________________________\n\n"
            self.charger_donnees(recharge=False)
            self.optimizer.charger_edt(self.file_edt)
            self.optimizer.charger_parcours(self.file_parcours)
            self.menu_principal()




    def charger_donnees(self,recharge=True):

        while not(() in [self.file_parcours,self.file_edt]) or not(recharge):
            s = "---------------------------- Chargement des fichiers ----------------------------\n\n\t\t(1) Charger le fichier EDT\t\t{} \n\t\t(2) Charger le fichier Parcours\t\t{} \n\n".format(self.file_edt, self.file_parcours)
            # if recharge :
            #     s+="\t\t(3) Retourner au Menu principal\n"
            s += "\t\t(0) Quitter\n\n " + "Tapez Entree pour valider votre saisie.\n\n"
            print (s)

            root = Tkinter.Tk()
            root.withdraw()
            chargement = raw_input(">>> ")

            if chargement == '0':
                exit(0)
            elif chargement == '1':
                self.file_edt  = tkFileDialog.askopenfilename(filetypes=[('CSV', '.csv')])

            elif chargement == '2':
                self.file_parcours = tkFileDialog.askopenfilename(filetypes=[('CSV', '.csv')])
            # elif chargement == '3' and recharge:
            #     self.menu_principal()
            elif chargement == '':          #Entree
                if not(() in [self.file_edt,self.file_parcours]):
                    break
                else:
                    print "Vous n'avez pas entre toutes les donnees necessaires.\n\n"
                    continue
            else:
                print "Commande incorrecte.\n\n"
                continue
            print "\n\n ================== fichier enregistre ==================\n\n"



    def print_equilibrage(self):
        print "\n\n_________________________________ Parametre d'equilibrage _________________________________\n\n"
        options = input("(1) Equilibrage avec valeur par defaut ({}%)\n(2) Equilibrage avec taux max desequilibre a 1 specifier\n(3) Sans equilibrage\n"
                        "(0) Quitter\nSaisir une valeur (0-3) : ".format(self.optimizer.tauxEquilibre*100))
        return options


    def faire_le_matching(self):
        while True:
            print "\n\n____________________________ Affectation ____________________________\n\n"
            # eq_qst = raw_input("\tActiver l'equilibrage dans les groupes ? (Par defaut 0.1)\n\t\t\t (1) Oui \t\t (0) Non\n\n>>> ")
            options = self.print_equilibrage()
            if options == 1:
                self.optimizer.match()

            elif options == 2:
                while True:
                    tauxMaxDesequilibre = raw_input("\nSaisir taux max desequilibre : ")
                    if tauxMaxDesequilibre.replace('.','',1).isdigit():
                        print"\n\n================= Modification de l'equilibrage enregistre =================\n\n"
                        tauxMaxDesequilibre = float(tauxMaxDesequilibre)
                        self.optimizer.match(equilibre=True,tauxEquilibre=tauxMaxDesequilibre)
                        break

            elif options == 3:
                self.optimizer.match(equilibre=False)
            elif options == 0:
                break
            else:
                print "Saisir une valeur valide!"
                continue

            print"\n\n================= - - - - - MATCHING - - - - - =================\n\n"

    def charger_dossier_voeux(self):
        while True:
            print"\n\n____________________ Chargement du dossier des voeux ____________________\n\n"
            print "\t(0) Retour au Menu Principal\n\n"
            chargement = raw_input("Veuillez specifier l'emplacement du dossier voeux (Tapez sur Entree)  : ")
            if chargement == '':
                root = Tkinter.Tk()
                root.withdraw()
                self.dirname_dossier_voeux = tkFileDialog.askdirectory(title =" Veuillez indiquer l'emplacement du dossier des voeux")
                if self.dirname_dossier_voeux != '':
                    print "\n\n ================== dossier enregistre ==================\n\n"
                    return True
            elif chargement == '0':
                return False
            else :
                print "Commande incorrecte.\n\n"
                continue

    def eprouver_edt(self):
        print "\n\n_________________________________ Eprouver l'EDT _________________________________\n\n"+\
            "Veuillez renseigner un chemin pour stocker les donnees qui seront generees par le test \n"
        root = Tkinter.Tk()
        root.withdraw()
        self.dirname_dossier_voeux = tkFileDialog.askdirectory()
        print"\n\n========================== Chemin enregistre ==========================\n\n"
        nbDossier = raw_input("Veuillez indiquer le nombre de dossier voeux a generer afin de mesurer la robustesse de l'EDT.\n"
                          " Par defaut le nombre de dossiers est a {}\n(Tapez Entree si par defaut)  : ".format(self.optimizer.nombreDeDossierGeneres))
        if nbDossier=='':
            nbDossier = 50
        else:
            nbDossier = int(nbDossier)

        while True:
            option = self.print_equilibrage()
            if option == 1:
                self.optimizer.eprouver_edt(nbDossier,directoryName=self.dirname_dossier_voeux)
                pass
            elif option == 2:

                while True:
                    tauxMaxDesequilibre = raw_input("\nSaisir taux max desequilibre : ")
                    print"\n\n================= Modification de l'equilibrage enregistre =================\n\n"
                    if tauxMaxDesequilibre.replace('.', '', 1).isdigit():
                        tauxMaxDesequilibre = float(tauxMaxDesequilibre)
                        self.optimizer.eprouver_edt(nbDossier,directoryName=self.dirname_dossier_voeux,tauxEquilibre=tauxMaxDesequilibre)
                        break
                    else:
                        print"\n Erreur taux max desequilibre. Veuillez reessayer, ou tapez 0 pour retourner a l'etape precedente\n"
                        choice = input(">>> ")
                        if choice == 0:
                            break
            elif option == 3:
                self.optimizer.eprouver_edt(nbDossier,directoryName=self.dirname_dossier_voeux,equilibre=False)

            elif option == 0:
                return

            choix = input("\n\nSouhaiteriez vous avoir une presentation des interets aux UE a partir d'un des dossiers de voeux genere ?\n\t\t(1) Oui\t\t(0) Non\n\n >>> ")
            if choix == 1:
                idDossierVoeux = input("\nVeuillez saisir le numero du dossier de voeux souhaite\n >>> ")
                if idDossierVoeux != '' and idDossierVoeux <nbDossier and idDossierVoeux >= 0:
                    self.optimizer.AD_interets_ue_conseillees_par_parcours(idDossierVoeux)

            # elif choix == 0:
            #     break


    def sauvegarder(self):
        pass

    def operation_sur_groupes(self):
        pass









##########################################################################################################################################################################################
##########################################################################################################################################################################################


    def menu_principal(self):
        while True:
            #         "\t(6) Recharger un fichier EDT\t\t ( courant : {} ) \n\t(7) Recharger un fichier Parcours\t\t ( courant : {} ) \n\t(8) Recharger un dossier de voeux\t\t ( courant : {} )\n".format(file_edt,file_parcours,dir_dossier_voeux)+\

            print"\n\n____________________________Menu principal____________________________\n\n" + \
                "\t(1) Charger et Executer un dossier de voeux\n\t(2) Mesurer la resistance de l'EDT actif\n\t(3) Operation sur l'EDT (afficher, modifier, sauvegarder)\n" \
                "\t(4) Afficher les incompatibilites par Parcours \n\n\t(5) Retour au Menu precedent\n\t(0) Quitter\n\n"
                 # "\t(1) Modifier l'EDT (ajouter/supprimer un groupe) \n\t(2) Modifier les donnees sur les UE (capacite des groupes) \n-------------------------------------------------------------\n" + \
                 # "\t(3) Afficher la carte des incompatibilites des UE \n\t(4) Eprouver l'EDT \n\t(5) Recherche locale \n-------------------------------------------------------------\n" + \
                 # "\t(6) Recharger des fichiers (edt, parcours, dossier voeux)\n-------------------------------------------------------------\n" + \
                 # "\t(7) Reinitialiser les donnees de depart \n\t(8) Sauvegarder les modifications \n\t(0) Quitter\n\n"

            choix = raw_input(">>> ")

    ############################################################################################################################################

            if choix == '0':
                exit(0)

    ############################################################################################################################################

            elif choix == '1':
                if self.charger_dossier_voeux() == False:
                    continue

                print "\n\n=========== Generation du graphique representant les interets des etudiants aux UE par parcours ===========\n\n"
                self.optimizer.AD_interets_ue_conseillees_par_parcours(self.dirname_dossier_voeux)
                print "\n=========================== Traitement du dossier des voeux ===========================\n\n"
                self.optimizer.traiter_dossier_voeux(self.dirname_dossier_voeux)
                goto_menu2 = False
                while not goto_menu2 :
                    self.faire_le_matching()
                    print "\n\n=========================== Affectation effectue ===========================\n\n"
                    while True:
                        continuer_avec_dautre_taux_equilibre = raw_input("Voulez-vous realiser une autre affectation du meme dossier avec d'autres options par exemple?\n\n(1) Oui \t(0) Retour au Menu principal\nSaisir une valeur(0-1) : ")
                        if continuer_avec_dautre_taux_equilibre == '1':
                            break
                        if continuer_avec_dautre_taux_equilibre == '0':
                            goto_menu2 = True
                            break
                        else:
                            print "\nCommande incorrecte.\n"

    ############################################################################################################################################

            elif choix == '2': #_________________________NEW
                self.eprouver_edt()

    ############################################################################################################################################

            elif choix == '3': #_________________________NEW
                while True:
                    print"\n\n__________________________ Operation sur l'EDT __________________________\n\n\t(1) Afficher l'EDT\n\t(2) Modifier les groupes d'UE\n\t(3) Sauvegarder les modifications apporte sur l'EDT\n\t" \
                            "(0) Retour au Menu principal\n\n"
                    changement_edt = input(" >>> ")
                    if changement_edt == 1:
                        pass
                    elif changement_edt == 2:
                        self.operation_sur_groupes()
                    elif changement_edt == 3:
                        self.sauvegarder()
                    elif changement_edt == 0:
                        break
                    else:
                        print "\nCommande incorrecte.\n"

    ############################################################################################################################################
            # elif choix == '3':
            #     self.afficher_incompatibilites()

            # elif choix == '5':
            #     self.charger_donnees(True)
            # elif choix == '7':
            #     self.reinitialiser_donnees()




Script()

# def modifier_edt(self):
#     print "\n___________________________Parametre EDT______________________________________\n\n"
#     print "Veuillez selectionner une UE : \n\n\t\t(1) AAGB\t(2) ALGAV"
#     choix_ue = raw_input(">>> ")
#     idUE =2# self.optimizer.ListeDesUEs[str.lower(choix_ue)]
#
#     while True:
#
#         print "\n\n\t\t(1) Ajouter un groupe\n\t\t(2) Supprimer un groupe \n\t\t(3) Changer l'UE\n\t\t(0) Retourner au Menu Principal\n\n "
#
#         input = raw_input(">>> ")
#
#         if input == '0':
#             break
#         elif input == '1':
#             # numeroGroupe = self.optimizer.ListeDesUEs[idUE].get_nb_groupes()
#             # self.optimizer.AS_supprimer_groupe(idUE, numeroGroupe+1)
#             while True:
#                 print "\n NOTE : les creneaux sont numerotes de 1 a 25 (5 creneaux par jours)\n\n"
#                 cr_td = raw_input("Veuillez indiquer le creneau du TD  : ")
#                 cr_tme = raw_input("Veuillez indiquer le creneau du TME : ")
#                 cap = raw_input("Veuillez indiquer la capacite du nouveau groupe : ")
#                 if str.isdigit(cr_td) and str.isdigit(cr_tme) and str.isdigit(cap):
#                     # self.optimizer.AS_ajouter_groupe(self, idUE, int(cr_td), int(cr_tme), int(cap))
#                     print "\n\n===================== AJOUT GROUPE {} UE {} ENREGISTRE =====================\n\n".format(numeroGroupe+1,idUE)
#         elif input == '2':
#             done = False
#             while not(done) :
#                 numeroGroupe = raw_input("Veuillez indiquer le numero du groupe a supprimer : ")
#                 if str.isdigit(numeroGroupe):
#                     # self.optimizer.AS_supprimer_groupe(idUE,int(numeroGroupe))
#                     done = True
#                     print "\n\n===================== SUPPRESSION DU GROUPE {} UE {} ENREGISTRE =====================\n\n".format(numeroGroupe, idUE)
#
#         elif input == '3':
#             continue


# def sauvegarder(self):
#
#     def save_file():
#         save_dialog_name = tkFileDialog.asksaveasfile()
#         return save_dialog_name.name
#
#     input = 't'
#     while input !='':
#         print "\n\n\t\t(1) Sauvegarder les modifications sur le fichier EDT\n\t\t(2) Sauvegarder les modifications sur le fichier Parcours \n\t\t(3) Sauvegarder la carte des incompatabilites\n\t\t"+\
#               "(0) Quitter\n\n " + "Tapez Entree pour retourner au Menu Principal.\n\n"
#         # "(4) Sauvegarder les donnees generees\n\t\t
#
#         input = raw_input(">>> ")
#
#         if input == '0':
#             exit(0)
#         elif input == '1':
#             self.path_to_save_edt = save_file()
#         elif input == '2' :
#             self.path_to_save_parcours = save_file()
#         elif input == '3':
#             self.path_to_save_incompabilite = save_file()
#         # elif input == '4':
#         #     self.path_to_save_donnees_generees = save_file()  ##_____________________________________________NOT A FILE BUT A DIRECTORY
#         else:
#             continue
#         print "--------------------------------------- ENREGISTRE ---------------------------------------"
#
#     self.menu_principal()


# def modifier_cap(self) :
#     print "\n___________________________Parametre UE______________________________________\n\n"
#     print "Veuillez selectionner une UE : \n\n\t\t(1) AAGB\t(2) ALGAV"
#     choix_ue = raw_input(">>> ")
#     idUE =2# self.optimizer.ListeDesUEs[str.lower(choix_ue)]
#
#     while True:
#         numeroGroupe = raw_input("Veuillez le numero du groupe : ")
#         cap = raw_input("Veuillez indiquer la nouvelle capacite du groupe : ")
#         if str.isdigit(numeroGroupe) and str.isdigit(cap):
#             # self.optimizer.AS_modifier_capacite(idUE,int(numeroGroupe),int(cap))
#             print "\n\n===================== MODIFICATION DU GROUPE {} UE {} ENREGISTRE =====================\n\n".format(numeroGroupe, idUE)
#             self.menu_principal()

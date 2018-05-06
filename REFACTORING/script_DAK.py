import tkFileDialog

from DAK_Optimizer import *


class Script():


    def __init__(self):
        print "DAK_Optimizer Powered by DAK"

        self.fichiers_chargees = set()
        self.file_edt = ''
        self.file_parcours = ''
        self.dir_dossier_voeux = ''
        self.optimizer = DAK_Optimizer()


    def start(self):
        while True:
            print"__________________________________Bienvenue au DAK_OPTIMIZER__________________________________\n\n"
            # self.charger_donnees(recharge=False)
            # self.optimizer.charger_edt(self.file_edt)
            # self.optimizer.charger_parcours(self.file_parcours)
            # self.optimizer.generer_incompatibilites()
            self.menu_principal()



    def modifier_edt(self):
        print "\n___________________________Parametre EDT______________________________________\n\n"
        print "Veuillez selectionner une UE : \n\n\t\t(1) AAGB\t(2) ALGAV"
        choix_ue = raw_input(">>> ")
        idUE =2# self.optimizer.ListeDesUEs[str.lower(choix_ue)]

        while True:

            print "\n\n\t\t(1) Ajouter un groupe\n\t\t(2) Supprimer un groupe \n\t\t(3) Changer l'UE\n\t\t(0) Retourner au Menu Principal\n\n "

            input = raw_input(">>> ")

            if input == '0':
                self.menu_principal()
            elif input == '1':
                # numeroGroupe = self.optimizer.ListeDesUEs[idUE].get_nb_groupes()
                # self.optimizer.AS_supprimer_groupe(idUE, numeroGroupe+1)
                while True:
                    print "\n NOTE : les creneaux sont numerotes de 1 a 25 (5 creneaux par jours)\n\n"
                    cr_td = raw_input("Veuillez indiquer le creneau du TD  : ")
                    cr_tme = raw_input("Veuillez indiquer le creneau du TME : ")
                    cap = raw_input("Veuillez indiquer la capacite du nouveau groupe : ")
                    if str.isdigit(cr_td) and str.isdigit(cr_tme) and str.isdigit(cap):
                        # self.optimizer.AS_ajouter_groupe(self, idUE, int(cr_td), int(cr_tme), int(cap))
                        print "\n\n===================== AJOUT GROUPE {} UE {} ENREGISTRE =====================\n\n".format(numeroGroupe+1,idUE)
            elif input == '2':
                done = False
                while not(done) :
                    numeroGroupe = raw_input("Veuillez indiquer le numero du groupe a supprimer : ")
                    if str.isdigit(numeroGroupe):
                        # self.optimizer.AS_supprimer_groupe(idUE,int(numeroGroupe))
                        done = True
                        print "\n\n===================== SUPPRESSION DU GROUPE {} UE {} ENREGISTRE =====================\n\n".format(numeroGroupe, idUE)

            elif input == '3':
                self.modifier_edt()


    def modifier_cap(self) :
        print "\n___________________________Parametre UE______________________________________\n\n"
        print "Veuillez selectionner une UE : \n\n\t\t(1) AAGB\t(2) ALGAV"
        choix_ue = raw_input(">>> ")
        idUE =2# self.optimizer.ListeDesUEs[str.lower(choix_ue)]

        while True:
            numeroGroupe = raw_input("Veuillez le numero du groupe : ")
            cap = raw_input("Veuillez indiquer la nouvelle capacite du groupe : ")
            if str.isdigit(numeroGroupe) and str.isdigit(cap):
                # self.optimizer.AS_modifier_capacite(idUE,int(numeroGroupe),int(cap))
                print "\n\n===================== MODIFICATION DU GROUPE {} UE {} ENREGISTRE =====================\n\n".format(numeroGroupe, idUE)
                self.menu_principal()


    def afficher_incompatibilites(self):
        pass

    def eprouver_edt(self):
        print "\n\n_________________________________ Eprouver l'EDT _________________________________\n\n"+\
            "Veuillez renseigner un chemin pour stocker les donnees qui seront generes par le test \n"

        pass

    def appliquer_rl(self) :
        pass

    def reinitialiser_donnees(self):
        pass

    def sauvegarder(self):
        def save_file():
            save_dialog_name = tkFileDialog.asksaveasfile()
            return save_dialog_name.name

        input = 't'
        while input !='':
            print "\n\n\t\t(1) Sauvegarder les modifications sur le fichier EDT\n\t\t(2) Sauvegarder les modifications sur le fichier Parcours \n\t\t(3) Sauvegarder la carte des incompatabilites\n\t\t"+\
                  "(0) Quitter\n\n " + "Tapez Entree pour retourner au Menu Principal.\n\n"
            # "(4) Sauvegarder les donnees generees\n\t\t

            input = raw_input(">>> ")

            if input == '0':
                exit(0)
            elif input == '1':
                self.path_to_save_edt = save_file()
            elif input == '2' :
                self.path_to_save_parcours = save_file()
            elif input == '3':
                self.path_to_save_incompabilite = save_file()
            # elif input == '4':
            #     self.path_to_save_donnees_generees = save_file()  ##_____________________________________________NOT A FILE BUT A DIRECTORY
            else:
                continue
            print "--------------------------------------- ENREGISTRE ---------------------------------------"

        self.menu_principal()


    def charger_donnees(self,recharge=True):

        fichiers_chargees = [self.file_edt,self.file_parcours,self.dir_dossier_voeux]
        while not('' in fichiers_chargees) or not(recharge):

            s = "---------------------------- Chargement des fichiers ----------------------------\n\n\t\t(1) Charger le fichier EDT\t\t{} \n\t\t(2) Charger le fichier Parcours\t\t{} \n\t\t(3) Charger le dossier de voeux (donnees de depart)\t\t{}\n".format(self.file_edt, self.file_parcours, self.dir_dossier_voeux)
            if recharge :
                s+="\t\t(4) Retourner au Menu principal\n"
            s += "\t\t(0) Quitter\n\n " + "Tapez Entree pour valider votre saisie.\n\n"

            print (s)

            chargement = raw_input(">>> ")

            if chargement == '0':
                exit(0)
            elif chargement == '1':
                self.file_edt = tkFileDialog.askopenfilename(filetypes=[('CSV', '.csv')])
                if self.file_edt==():
                 fichiers_chargees[0]= ''
            elif chargement == '2':
                self.file_parcours = tkFileDialog.askopenfilename(filetypes=[('CSV', '.csv')])
                if self.file_parcours==():
                  fichiers_chargees[1]= self.file_parcours
            elif chargement == '3':
                self.dir_dossier_voeux = tkFileDialog.askdirectory(title='Choisissez un repertoire')
                fichiers_chargees[2]= self.dir_dossier_voeux
            elif chargement == '4' and recharge:
                self.menu_principal()
            elif chargement == '':
                if not('' in fichiers_chargees):
                    break
                else:
                    print "Vous n'avez pas entre toutes les donnees necessaires.\n\n"
                    continue
            else:
                print "Commande incorrecte.\n\n"
                continue

            print "\n\n ================== fichier enregistre ==================\n\n"



    def menu_principal(self):
        while True:
            #         "\t(6) Recharger un fichier EDT\t\t ( courant : {} ) \n\t(7) Recharger un fichier Parcours\t\t ( courant : {} ) \n\t(8) Recharger un dossier de voeux\t\t ( courant : {} )\n".format(file_edt,file_parcours,dir_dossier_voeux)+\

            print"____________________________Menu principal____________________________\n\n" + \
                 "\t(1) Modifier l'EDT (ajouter/supprimer un groupe) \n\t(2) Modifier les donnees sur les UE (capacite des groupes) \n-------------------------------------------------------------\n" + \
                 "\t(3) Afficher la carte des incompatibilites des UE \n\t(4) Eprouver l'EDT \n\t(5) Recherche locale \n-------------------------------------------------------------\n" + \
                 "\t(6) Recharger des fichiers (edt, parcours, dossier voeux)\n-------------------------------------------------------------\n" + \
                 "\t(7) Reinitialiser les donnees de depart \n\t(8) Sauvegarder les modifications \n\t(0) Quitter\n\n"

            choix = raw_input(">>> ")

            if choix == '0':
                exit(0)
            elif choix == '1':
                self.modifier_edt()
            elif choix == '2':
                self.modifier_cap()
            elif choix == '3':
                self.afficher_incompatibilites()
            elif choix == '4':
                self.eprouver_edt()
            elif choix == '5':
                self.appliquer_rl()
            elif choix == '6':
                self.charger_edt(True)
            elif choix == '7':
                self.reinitialiser_donnees()
            elif choix == '8':
                self.sauvegarder()



s = Script()
s.start()


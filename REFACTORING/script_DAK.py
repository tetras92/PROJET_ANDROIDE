import Tkinter
import tkFileDialog

from DAK_Optimizer import DAK_Optimizer


# !/usr/bin/env python
# _*_ coding:utf-8 _*_


class Script():


    def __init__(self):
        print "DAK_Optimizer Powered by DAK"


        self.dirname_dossier_voeux = ''
        # self.dirname_tout_dossier = ''
        self.optimizer = DAK_Optimizer()
        self.dernier_taux_equilibre = DAK_Optimizer.tauxEquilibre
        self.dernier_nb_dossiers = DAK_Optimizer.nbDossiersParDefaut

        print"\t\tP-ANDROIDE : OPTIMISATION DES INSCRIPTIONS AUX UES (PAR DAK)\n\n"
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
            s = "---------------------------- Chargement des fichiers ----------------------------\n\n\t\t{:50s}{}\n\t\t{:50s}{}\n\n".format("(1) Charger le fichier EDT",self.file_edt,"(2) Charger le fichier decrivant les parcours",self.file_parcours)
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
                edtfile = tkFileDialog.askopenfilename(filetypes=[('CSV', '.csv')])

                if edtfile != () and edtfile != "":
                    try:
                        self.optimizer.charger_edt(edtfile)
                        self.file_edt = edtfile #JUSTE POUR L'AFFICHAGE
                        print "\n================== Chargement EDT termine ==================\n"
                    except:
                        print "ERREUR SURVENUE LORS DU CHARGEMENT DU FICHIER EDT!\n"
                        self.file_edt = "..."
            elif chargement == '2':
                file_parcours = tkFileDialog.askopenfilename(filetypes=[('CSV', '.csv')])
                if file_parcours != () and file_parcours != "":
                    try:
                        self.optimizer.charger_parcours(file_parcours)
                        self.file_parcours = file_parcours
                        print "\n ================== Chargement fichier descriptif des parcours termine ==================\n"
                    except:
                        print "ERREUR SURVENUE LORS DU CHARGEMENT DU FICHIER DESCRIPTIF DES PARCOURS!\n"
                        self.file_parcours = "..."
            else:
                print "Commande incorrecte.\n\n"

        self.menu_principal()

    def menu_principal(self):
        while True:
            #         "\t(6) Recharger un fichier EDT\t\t ( courant : {} ) \n\t(7) Recharger un fichier Parcours\t\t ( courant : {} ) \n\t(8) Recharger un dossier de voeux\t\t ( courant : {} )\n".format(file_edt,file_parcours,dir_dossier_voeux)+\

            print"\n\n____________________________Menu principal____________________________\n\n" + \
                "\t(1) Charger un dossier de voeux et effectuer les inscriptions pedagogiques\n\t(2) Mesurer la resistance de l'EDT actif : Generation aleatoire de dossiers de voeux\n\t(3) EDT : Afficher, Modifier, Sauvegarder\n" \
                "\t(4) Contrats incompatibilites par parcours : Visualiser\n\n\t(5) Retour au Menu chargement\n\t(0) Quitter\nSaisir une valeur (0-5) : \n\n"

            choix = raw_input(">>> ")

            if choix == '0':
                exit(0)

            elif choix == '1':
                if self.charger_voeux() == False:
                    continue
                try:
                    self.optimizer.AD_interets_ue_conseillees_par_parcours(self.dirname_dossier_voeux)
                    print "\n\n=========== Generation du graphique representant les interets des etudiants aux UE non-obligatoires de leur parcours ===========\n\n"
                except:
                    print "\nERREUR LORS DU CALCUL DE L'INTERET DES ETUDIANTS DE CHAQUE PARCOURS POUR LEURS UE NON-OBLIGATOIRES\n"
                try:
                    self.faire_le_matching()
                except:
                    print "\nERREUR LORS DE LA REALISATION DES INSCRIPTIONS PEDAGOGIQUES (MATCHING)\n"

            elif choix == '2': #_________________________NEW
                self.eprouver_edt()

            elif choix == '3': #_________________________NEW             ICI CE 18/05

                # def get_all_ue_name():
                #     Liste_id_ues = list(self.optimizer.DictUEs.keys())
                #     Liste_id_ues.sort()
                #     s = "\n"
                #     nb_ue = len(Liste_id_ues)
                #     for ue,i in zip(Liste_id_ues,range(1,nb_ue + 1)):
                #         s += "\t({}) {}\t\t".format(i,ue)
                #         if ((i-1)%(nb_ue/2))==0:
                #           s+="\n"
                #     return s
                #
                # while True:
                #     print"\n\n__________________________ Operation sur l'EDT __________________________\n\n\t(1) Afficher l'EDT\n\t(2) Modifications sur les groupes d'UE\n\t(3) Sauvegarder les modifications apportees sur l'EDT\n\t" \
                #             "(0) Retour au Menu principal\n\n"
                #     changement_edt = input(" >>> ")
                #     if changement_edt == 1:
                #         print self.optimizer.afficher_EDT()
                #     elif changement_edt == 2:
                #         print "\n\n_______________________ Modification des groupes d'UE _______________________\n\n"
                #         intit_ue = get_all_ue_name()
                #         while True:
                #             print "\tVeuillez selectionner une UE a modifie : \n\n"+intit_ue
                #             try:
                #                 ue_a_modifie = input(">>> ")
                #             except:
                #                 print"im in expction input"
                #                 continue
                #             break
                #         if ue_a_modifie <= len(self.optimizer.DictUEs) or ue_a_modifie >0 :
                #             while True:
                #                 print "\n\t(1) Ajouter un nouveau groupe\n\t(2) Supprimer un groupe\n\t(3) Modifier la capacite d'un groupe\n\t(0) Retour au menu precedent\n"
                #                 choix = raw_input(">>> ")
                #                 if choix == '1':
                #                     self.ajouter_groupe(ue_a_modifie)
                #                 elif choix == '2':
                #                     self.supprimer_groupe(ue_a_modifie)
                #                 elif choix == '3':
                #                     self.modifier_capacite_groupe(ue_a_modifie)
                #                 elif choix == '0':
                #                    break
                #
                #     elif changement_edt == 3:
                #         self.sauvegarder()
                #     elif changement_edt == 0:
                #         break
                #     else:
                #         print "\nCommande incorrecte.\n"

                self.delagateur_operations_edt(self.message_operations_EDT())
            elif choix == '4':
                print"_____________________ Afficher la carte d'incompatibilites dans un Parcours "

                parcours = raw_input("Veuillez indiquer le nom du parcours : ")
                if parcours !='':
                    taille = input(" Veuillez indiquez la taille : ")
                    self.optimizer.AD_afficher_carte_incompatibilites(parcours,taille)
            elif choix == '5':
                self.menu_chargement()


    def print_equilibrage(self):
        print "\n\n_________________________________ Option Equilibrage au sein des groupes de chaque UE _________________________________\n"
        option = raw_input("Choisir le pourcentage maximal de desequilibre a tolerer :\"Entree\" pour {}%\n(1) 5.0%\n(2) 10.0%\n(3) 20.0%\n(4) Sans equilibrage (100%)\n"
                        "(0) Retour au Menu Principal\nSaisir une valeur (0-4) : ".format(self.dernier_taux_equilibre*100))
        if option == '' or option == ():
            return -1
        option = int(option)
        if option not in range(5):          #NE PAS SORTIR TANT QUE VALEUR NON VALIDE SAISIE
            print "Saisir une valeur valide!"
            return self.print_equilibrage()
        return option

    def rematcher(self):
        print "\nSouhaitez-vous reeffectuer les inscriptions pedagogiques? (avec un autre pourcentage de desequilibre par exemple)\n(1) Oui\n(0) Non\nSaisir une valeur (0-1):"
        choix = raw_input(">>> ")
        if choix == '1':
            return True
        elif choix == '0':
            return False
        else:
            print "\t\tSaisir une valeur valide!"
            return self.rematcher()

    def reeprouver_edt(self):
        print "\nSouhaitez-vous a nouveau eprouver la resistance de l'EDT? " \
              "(avec un autre pourcentage de desequilibre ou en generant plus de dossiers aleatoires par exemple)\n(1) Oui\n(0) Non\nSaisir une valeur (0-1):"
        choix = raw_input(">>> ")
        if choix == '1':
            return True
        elif choix == '0':
            return False
        else:
            print "\t\tSaisir une valeur valide!"
            return self.reeprouver_edt()


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
            print "\t\tSaisir une valeur valide!"
            self.faire_le_matching()
            return
        if self.rematcher():
            self.faire_le_matching()


    def message_operations_EDT(self):
        choix = raw_input("\n\n__________________________ Operations sur l'EDT __________________________\n\n" \
              "(1) Afficher\n" \
              "(2) Modifier\n" \
              "(3) Sauvegarder\n" \
              "(0) Retour au Menu Principal\n" \
              "Saisir une valeur (0-3) : ")
        if choix not in [str(i) for i in range(4)]:
            print 'Saisie Incorrecte!'
            return self.message_operations_EDT()
        choix = int(choix)
        return choix

    def delagateur_operations_edt(self, choix):
        if choix == 1:
            try:
                self.optimizer.afficher_EDT()
            except:
                print "\nERREUR LORS DE L'AFFICHAGE DE L'EDT\n"
        elif choix == 2:
            ue_a_modifierOuAnnuler = self.message_modifier_edt()
            if ue_a_modifierOuAnnuler == 0:
                self.delagateur_operations_edt(self.message_operations_EDT())
            else:
                self.delegateur_modifier_ue(ue_a_modifierOuAnnuler, self.message_modification_a_appliquer_une_UE(ue_a_modifierOuAnnuler))

        elif choix == 3:
            self.sauvegarder()
            self.delagateur_operations_edt(self.message_operations_EDT())
        elif choix == 0:        #PAS BESOIN J'AVAIS LA GARANTIE QUE soit 1, 2, 3 ou 0 seront saisies
            return

    def delegateur_modifier_ue(self, idUE, choix):
        if choix == 1:
            self.modifier_capacite_groupe(idUE)
        elif choix == 2:
            self.ajouter_groupe(idUE)
        elif choix == 3:
            self.supprimer_groupe(idUE)
        else:
            print "NOT YET IMPLEMENTED"



    def message_modification_a_appliquer_une_UE(self, idUE):
        s = "Vous avez choisi l'UE : {}.\n" \
            "Que voulez-vous faire?\n" \
            "(1) Modifier la capacite d'un ou plusieurs groupe(s)\n" \
            "(2) Ajouter un groupe\n" \
            "(3) Supprimer un groupe\n" \
            "(4) Deplacer les seances de td/tme d'un groupe\n" \
            "(5) Deplacer un cours\n" \
            "(0) Annuler\n" \
            "Saisir une valeur (0-5): ".format(self.optimizer.ListeDesUEs[idUE].get_intitule())
        choix = raw_input(s)
        if choix not in [str(i) for i in range(6)]:
            print "\t\tSaisie incorrecte!"
            return self.message_modification_a_appliquer_une_UE(idUE)
        choix = int(choix)
        return choix


    def message_modifier_edt(self):
        s = "\nSORBONNE UNIVERSITE : LES UE DU MASTER INFORMATIQUE\n" + self.chaine_ues_listees(5)
        nbUEs = len(self.optimizer.ListeDesUEs[1:])
        choix = raw_input(s + "Choisir l'UE a laquelle vous souhaitez appliquer des modifications.\n(0) pour \"Annuler\".\nSaisir une valeur (0-{}): ".format(nbUEs))
        if choix not in [str(i) for i in range(nbUEs+1)]:
            print "\t\tSaisie incorrecte!\n"
            return self.message_modifier_edt()
        return int(choix)



    def charger_voeux(self):
        annuler = False
        while not annuler:
            print"\n\n____________________ Chargement du dossier des voeux ____________________\n\n"
            # print "\t\n\n"
            root = Tkinter.Tk()
            root.withdraw()
            dossier_voeux = tkFileDialog.askdirectory(title =" Veuillez selectionner l'emplacement du dossier des voeux")
            if dossier_voeux != () and dossier_voeux != "":
                try:
                    self.optimizer.traiter_dossier_voeux(dossier_voeux)
                    self.dirname_dossier_voeux = dossier_voeux
                    print "\n ================== Dossier de voeux charge : {} ==================\n".format(self.dirname_dossier_voeux)
                except:
                    print "ERREUR LORS DU CHARGEMENT DU DOSSIER DE VOEUX"
                    return False

            else:
                annuler = True
                continue
            chargement = raw_input("(0) Retour au Menu Principal\n\"Entree\" pour realiser les affectations.\n>>> ")

            if chargement == '0':
                annuler = True
            elif chargement == '':
                break
            else :
                print "Commande incorrecte.\n\n"
                continue

        return not annuler

    def affichage_avant_eprouver_edt(self):
        nbDossier = raw_input("Veuillez selectionner le nombre de dossiers voeux a generer. \"Entree\" pour {} dossiers aleatoires\n"
                          "(1) {:3s} dossiers aleatoires (~ {} minute(s))\n(2) {:3s} dossiers aleatoires (~ {} minute(s))\n(3) {:3s} dossiers aleatoires (~ {} minute(s))\n"
                              "(4) {:3s} dossiers aleatoires (~ {} minute(s))\n(5) {:3s} dossiers aleatoires (~ {} minute(s))\n(6) {:3s} dossiers aleatoires (~ {} minute(s))\n"
                              "(0) Retour au Menu Principal\nSaisir une valeur (0-6) : ".format(self.dernier_nb_dossiers, '20', 1, '50', 2, '75', 3, '100', 4, '150', 7, '200', 9))

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
            nbDossier = 0
        elif nbDossier == '' or nbDossier == ():
            nbDossier = self.dernier_nb_dossiers
        else:
            print "Saisir une valeur valide!\n"
            return self.affichage_avant_eprouver_edt()
        if nbDossier != 0:       #Ne pas considerer le cas annuler
            self.dernier_nb_dossiers = nbDossier
        return nbDossier

    def eprouver_edt(self):
        annuler = False
        print "\n\n_________________________________ Eprouver l'EDT _________________________________\n\n"+\
            "Les dossiers de voeux aleatoires generes sont stockes automatiquement dans le repertoire ~/VOEUX_RANDOM\n"

        while not annuler:
            nbDossier = self.affichage_avant_eprouver_edt()
            if nbDossier == 0:
                annuler = True
                continue

            option = self.print_equilibrage()
            if option == 1:
                self.optimizer.eprouver_edt(nombreDeDossierGeneres=nbDossier,equilibre=True, tauxEquilibre=0.05)

                self.dernier_taux_equilibre = 0.05
            elif option == 2:
                self.optimizer.eprouver_edt(nombreDeDossierGeneres=nbDossier,equilibre=True)

                self.dernier_taux_equilibre = DAK_Optimizer.tauxEquilibre
            elif option == 3:
                self.optimizer.eprouver_edt(nombreDeDossierGeneres=nbDossier,equilibre=True,tauxEquilibre=0.20)

                self.dernier_taux_equilibre = 0.20
            elif option == 4:
                self.optimizer.eprouver_edt(nombreDeDossierGeneres=nbDossier,equilibre=True, tauxEquilibre=1)

                self.dernier_taux_equilibre = 1
            elif option == -1:
                self.optimizer.eprouver_edt(nombreDeDossierGeneres=nbDossier,equilibre=True, tauxEquilibre=self.dernier_taux_equilibre)
            elif option == 0:
                annuler = True
                continue          #RETOURNE DANS LA BOUCLE DU MENU PRINCIPAL
            if not self.reeprouver_edt():
                annuler = True
                continue



    def sauvegarder(self):
        root = Tkinter.Tk()
        root.withdraw()
        save_file_edt = tkFileDialog.asksaveasfile(title="Enregistrer sous ...", filetypes=[('CSV', '.csv')])
        if save_file_edt != None: # Quand pas Annuler
            try:
                self.optimizer.sauvegarde_UEs(save_file_edt.name)
                print "============================== SAUVEGARDE REUSSIE ==============================\n\n"
            except:
                print "!!!________________ SAUVEGARDE ECHOUE ________________!!\n\n"


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
            print"\n============================ MODIFICATION ENREGISTREE ============================\n\n"
            print self.optimizer.ListeDesUEs[id_ue].print_groupe()
            break

    def chaine_ues_listees(self, nombreParligne):
        ListeUes = self.optimizer.ListeDesUEs
        s = ""
        for i in range(1, len(ListeUes)):
            s += "{:4s} {:12s}\t".format("("+str(i)+")", ListeUes[i].get_intitule())
            if i % nombreParligne == 0:
                s += "\n"
        s += "\n\n"
        return s









##########################################################################################################################################################################################
##########################################################################################################################################################################################



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

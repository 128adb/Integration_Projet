import utile.config as config


def print_menu():
    print("GESTION DES CONFIGURATIONS")
    print("==========================")
    print("1) Charger une configuration")
    print("2) Afficher la configuration courante")
    print("3) Modifier ou ajouter un paramètre à la configuration courante")
    print("4) Supprime un paramètre de la configuration courante")
    print("5) Créez une nouvelle configuration courante")
    print("6) Sauvegarder la configuration courante")
    print("7) Quitter")


def main():
    choix = 0
    while choix != 7:
        print_menu()
        choix = int(input("1 a 7 ?"))
        if choix == 1:
            # Chargement d'une configuration sur disque
            print("Chargement d'une configuration sur disque")
            print("=========================================")
            config_file = input("Entrez le nom de la configuration à charger :")
            config.load_config(config_file + ".cfg",config_file + ".key")
        if choix == 2:
            # Affichage de la configuration courante
            print("Affichage de la configuration courante")
            print("======================================")
            config.print_config()
        if choix == 3:
            # Modification ou ajout d'un paramètre à la configuration courante
            print("Ajout ou modification d'un paramètre")
            print("====================================")
            setting = input("Paramètre : ")
            value = input("Valeur : ")
            if value == "True":
                value = True
            elif value == "False":
                value = False
            elif value[0] == '[':
                # Converting string to list
                value = value.strip('][').split(', ')
            elif value.upper() == 'NONE':
                # Converting string to NoneObject
                value = None
            elif value.isdigit():
                # Converting string to int
                value = int(value)
            config.set_config(setting, value)
        if choix == 4:
            print("Suppression d'un paramètre de la configuration courante")
            print("=======================================================")
            setting = input("Paramètre : ")
            config.remove_config(setting)
        if choix == 5:
            print("La configuration courante est réinitialisée")
            print("===========================================")
            config.reset_config()
        if choix == 6:
            print("Sauvegarde de la configuration courante")
            print("=======================================")
            config_file = input("Entrez le nom de la configuration à sauvegarder :")
            config.save_config("config/" + config_file + ".cfg", "config/" + config_file + ".key")
        if choix == 7:
            print("\nFermeture de l'application'.")


if __name__ == '__main__':
    main()
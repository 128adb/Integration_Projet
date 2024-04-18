import json
import utile.security as security
import pickle

# Constante
DEBUG_MODE = True
AES_GCM = True

# Variable globale
config = {}


def load_config(config_file='config/config.cfg', key_file='config/key.bin'):
    """
    Fonction permettant de charger la configuration au format JSON avec cryptage AES-GCM
    :param config_file: (str) Fichier d'enregistrement de la configuration
    :param key_file: (str) Fichier d'enregistrement de la clé de chiffrement AES-GCM
    :return: (dict) La configuration chargée
    """
    global config
    if AES_GCM:
        with open(key_file, 'rb') as k:
            key = k.read()

    with open(config_file, 'rb') as c:
        data = c.read()

    data = pickle.loads(data)
    if AES_GCM:
        data = security.aes_decrypt(data, key)
    config = json.loads(data)
    return config


def save_config(config_file='config/config.cfg', key_file='config/key.bin'):
    """
    Fonction permettant de sauvegarder la configuration au format JSON avec cryptage AES-GCM
    :param config_file: (str) Fichier d'enregistrement de la configuration
    :param key_file: (str) Fichier d'enregistrement de la clé de chiffrement AES-GCM
    :return: néant
    """
    global config
    key = b''
    if config != {}:
        if AES_GCM:
            # Génère et enregistre la clé de chiffrement
            key = security.gen_key()
            with open(key_file, 'wb') as k:
                k.write(key)

        # Chiffre et enregistre la configuration
        data = json.dumps(config)
        if DEBUG_MODE:
            print(f"Data : {data} {type(data)}")
            print(f"Key file : {key_file}")
            print(f"Config file : {config_file}")
        if AES_GCM:
            data = security.aes_encrypt(data, key)
        data = pickle.dumps(data)

        with open(config_file, 'wb') as c:
            c.write(data)


def get_config(setting):
    """
    Renvoie la valeur de la clé de configuration chargée en mémoire (voir fonction load_config ou
    configuration en construction)
    :param setting: (str) clé de configuration à retourner
    :return: valeur associée à la clé demandée
    """
    global config
    if setting in config.keys():
        return config[setting]
    else:
        return None


def set_config(setting, value):
    """
    Initialise la valeur de la clé de configuration chargée en mémoire (voir fonction load_config ou
    configuration en construction)
    :param setting: (str) clé de configuration à retourner
    :param value: Valeur à enregistrer
    :return: Néant
    """
    global config
    config[setting] = value


def print_config():
    """
    Affiche la configuration en mémoire
    :return: Néant
    """
    print(json.dumps(config, indent=4))


def reset_config():
    """
    Efface la configuration courante en mémoire
    :return: Néant
    """
    global config
    config.clear()


def remove_config(setting):
    global config
    if setting in config.keys():
        config.pop(setting)


def validate(msg):
    """
    Devamnde de confirmation par O ou N
    :param msg: (str) Message à afficher pour la demande de validation
    :return: (boolean) Validé ou pas
    """
    valide = False
    while not valide:
        response = input(f"{msg} (O/N)")
        response = response.upper()
        if response == 'O':
            return True
        elif response == 'N':
            return False
        print("Erreur : Veuillez répondre par O ou N")

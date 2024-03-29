import json
import utile.security as security
import pickle

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
    try:
        # Chargement de la clé de chiffrement
        with open(key_file, 'rb') as kf:
            key = kf.read()

        # Lecture et déchiffrement du fichier de configuration
        with open(config_file, 'rb') as cf:
            encrypted_data = cf.read()
            decrypted_data = security.aes_decrypt(encrypted_data, key)
            config = json.loads(decrypted_data)
    except Exception as e:
        print(f"Erreur lors du chargement de la configuration: {e}")
        config = {}
def save_config(config_file='config/config.cfg', key_file='config/key.bin'):
    """
    Fonction permettant de sauvegarder la configuration au format JSON avec cryptage AES-GCM
    :param config_file: (str) Fichier d'enregistrement de la configuration
    :param key_file: (str) Fichier d'enregistrement de la clé de chiffrement AES-GCM
    :return: néant
    """
    global config
    try:
        # Chargement de la clé de chiffrement
        with open(key_file, 'rb') as kf:
            key = kf.read()

        # Chiffrement et enregistrement du fichier de configuration
        encrypted_data = security.aes_encrypt(json.dumps(config).encode(), key)
        with open(config_file, 'wb') as cf:
            cf.write(encrypted_data)
    except Exception as e:
        print(f"Erreur lors de la sauvegarde de la configuration: {e}")

def get_config(setting):
    """
    Renvoie la valeur de la clé de configuration chargée en mémoire (voir fonction load_config ou
    configuration en construction)
    :param setting: (str) clé de configuration à retourner
    :return: valeur associée à la clé demandée
    """
    return config.get(setting, None)

def set_config(setting, value):
    """
    Initialise la valeur de la clé de configuration chargée en mémoire (voir fonction load_config ou
    configuration en construction)
    :param setting: (str) clé de configuration à retourner
    :param value: Valeur à enregistrer
    :return: Néant
    """
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
    config = {}

def remove_config(setting):
    """
    Retire un paire de clé (setting) / valeur de la configuration courante en mémoire
    :param setting: la clé à retirer du la config courante
    :return: Néant
    """
    config.pop(setting, None)

def validate(msg):
    """
    Demande de confirmation par O ou N
    :param msg: (str) Message à afficher pour la demande de validation
    :return: (boolean) Validé ou pas
    """
    response = input(f"{msg} (O/N): ").strip().upper()
    return response == 'O'

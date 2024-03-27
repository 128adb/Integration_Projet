import json  # Importation du module json pour travailler avec des données au format JSON
import utile.security as security  # Importation du module de sécurité pour le chiffrement AES-GCM
import pickle  # Importation du module pickle pour sérialiser et désérialiser des objets Python

# Variable globale pour stocker la configuration
#global config 'accéder et de modifier la variable config
config = {}


def load_config(config_file='config/config.cfg', key_file='config/key.bin'):
    """
    Charge la configuration à partir d'un fichier au format JSON avec cryptage AES-GCM.
    :param config_file: Chemin du fichier de configuration.
    :param key_file: Chemin du fichier contenant la clé de chiffrement AES-GCM.
    """
    global config
    # Lecture de la clé de chiffrement depuis le fichier
    with open(key_file, 'rb') as f:
        key = f.read()
    # Lecture des données chiffrées depuis le fichier de configuration
    with open(config_file, 'rb') as f:
        encrypted_data = f.read()
    # Décryptage des données et désérialisation au format JSON
    decrypted_data = security.aes_decrypt(pickle.loads(encrypted_data), key)
    config = json.loads(decrypted_data)


def save_config(config_file='config/config.cfg', key_file='config/key.bin'):
    """
    Enregistre la configuration au format JSON avec cryptage AES-GCM.
    :param config_file: Chemin du fichier de configuration.
    :param key_file: Chemin du fichier contenant la clé de chiffrement AES-GCM.
    """
    global config
    # Lecture de la clé de chiffrement depuis le fichier
    with open(key_file, 'rb') as f:
        key = f.read()
    # Sérialisation de la configuration en JSON et chiffrement des données
    encrypted_data = pickle.dumps(security.aes_encrypt(json.dumps(config), key))
    # Écriture des données chiffrées dans le fichier de configuration
    with open(config_file, 'wb') as f:
        f.write(encrypted_data)


def get_config(setting):
    """
    Renvoie la valeur d'un paramètre de configuration.
    :param setting: Clé du paramètre de configuration.
    :return: Valeur du paramètre de configuration.
    """
    global config
    return config.get(setting)


def set_config(setting, value):
    """
    Initialise la valeur d'un paramètre de configuration.
    :param setting: Clé du paramètre de configuration.
    :param value: Valeur à enregistrer.
    """
    global config
    config[setting] = value


def print_config():
    """
    Affiche la configuration actuelle.
    """
    global config
    print(json.dumps(config, indent=4))


def reset_config():
    """
    Réinitialise la configuration.
    """
    global config
    config = {}


def remove_config(setting):
    """
    Supprime un paramètre de configuration.
    :param setting: Clé du paramètre à supprimer.
    """
    global config
    if setting in config:
        del config[setting]


def validate(msg):
    """
    Demande de confirmation avec la saisie de 'O' pour Oui ou 'N' pour Non.
    :param msg: Message à afficher pour la demande de validation.
    :return: True si validé, False sinon.
    """
    while True:
        response = input(f"{msg} [O/N]: ").strip().lower()
        if response == 'o':
            return True
        elif response == 'n':
            return False
        else:
            print("Veuillez entrer 'O' pour Oui ou 'N' pour Non.")


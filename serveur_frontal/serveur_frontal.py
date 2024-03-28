import string
import random
import utile.network as network
import utile.message as message
import utile.security as security
import utile.config as config

# Constantes
DEBUG_MODE = False
AES_GCM = True
IP_SERV_CLES = ''  # Mettre à jour avec l'adresse réelle du serveur de clés
PORT_SERV_CLES = 8380  # Mettre à jour avec le port réel du serveur de clés
aes_key = b''


def print_menu():
    print("\nSIMULATION SERVEUR FRONTAL")
    print("==========================")
    print("1) Création d'une victime fictive")
    print("2) Envoi du INITIALIZE_REQ")
    print("3) Quitter")


def simulate_hash(longueur=64):  # Longueur par défaut ajustée pour un hash typique
    letters = string.hexdigits[:-6]  # Exclure 'abcdef' pour simuler un hash hexadécimal
    return ''.join(random.choice(letters) for i in range(longueur))


def main():
    # global AES_GCM, DEBUG_MODE, IP_SERV_CLES, PORT_SERV_CLES, aes_key

    # # Chargement de la configuration
    # config.load_config('config/serveur_frontal.cfg', 'config/serveur_frontal.key')
    # AES_GCM = config.get_config('AES_GCM')
    # DEBUG_MODE = config.get_config('DEBUG_MODE')
    # IP_SERV_CLES = config.get_config('IP_SERV_CLES')
    # PORT_SERV_CLES = int(config.get_config('PORT_SERV_CLES'))

    # Connexion vers le serveur de clés
    s_client = network.connect_to_serv(port=PORT_SERV_CLES)
    print("Connexion OK")
    aes_key = security.diffie_hellman_recv_key(s_client)
    print("ok")
    print(f"Clé de chiffrement réceptionnée : {aes_key} {type(aes_key)}")

    choix = 0
    print("Choix")
    hash_victim, os, disks = '', '', ''
    print_menu()
    choix = int(input("Votre choix ?"))

    if choix == 1:
        hash_victim = simulate_hash(256)
        disks = input("Renseignez les disques (exemple : c:,d:,f:) : ")
        os = input("Renseignez le type d'OS (SERVER ou WORKSTATION) : ")
    elif choix == 2 and hash_victim:
        msg = message.set_message('initialize_req', [hash_victim, os, disks])
        if AES_GCM:
            msg = security.aes_encrypt(msg, aes_key)
        network.send_message(s_client, msg)
        msg = network.receive_message(s_client)
        if AES_GCM:
            msg = security.aes_decrypt(msg, aes_key)
        msg_type = message.get_message_type(msg)
        if msg_type == 'INITIALIZE_KEY':
            print(f"L'ID de la nouvelle victime est : {msg['KEY_RESP']}")
            print("Sa clé de chiffrement est :")
            print(msg['KEY'])
    elif choix == 3:
        print("\nFermeture de la session.")
        s_client.close()


if __name__ == '__main__':
    main()

import string
import random
import utile.network as network
import utile.message as message
import utile.security as security
import utile.config as config


# Constantes
DEBUG_MODE = False
AES_GCM = True
aes_key = b''

def print_menu():
    print("SIMULATION SERVEUR FRONTAL")
    print("==========================")
    print("1) Création d'une victime fictive")
    print("2) Envoi du INITIALIZE_REQ")
    print("3) Quitter")


def simulate_hash(longueur=0):
    letters = string.hexdigits
    return ''.join(random.choice(letters) for i in range(longueur))


def main():
    s_client = network.connect_to_serv()
    aes_key = network.receive_message(s_client)
    print(f"Clé de chiffrement réceptionnée : {aes_key} {type(aes_key)}")

    choix = 0
    hash_victim = ''
    os = ''
    disks = ''
    while choix != 3:
        print_menu()
        choix =int(input("Votre choix "))

        if choix == 1:
            hash_victim = simulate_hash(256)
            disks = input("Renseignez les disques (exemple : c:,d:,f:) : ")
            os = input("Renseignez le type d'OS (SERVER ou WORKSTATION) : ")
        if choix == 2:
            # Envoi de la requête
            msg = message.set_message('initialize_req', [hash_victim, os, disks])
            msg = security.aes_encrypt(msg, aes_key)
            network.send_message(s_client, msg)

            # Réception de la réponse
            msg = network.receive_message(s_client)
            msg = security.aes_decrypt(msg, aes_key)
            msg_type = message.get_message_type(msg)
            if msg_type == 'INITIALIZE_KEY':
                print(f"L'ID de la nouvelle victime est : {msg['KEY_RESP']}")
                print(f"Sa clé de chiffrement est :")
                print(f"{msg['KEY']}")
        if choix == 3:
            print("\nFermeture de la session.")
            s_client.close()
    exit(0)


if __name__ == '__main__':
    main()
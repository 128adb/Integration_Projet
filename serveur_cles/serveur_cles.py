import utile.network as network
import utile.message as message
import utile.data as data
import socket

def main():
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
                # Le client s'est déconnecté, sortir de la boucle
                break

            # Afficher le message reçu
            print(f"Message du client : {message}")
        # Fermer la connexion avec le client
        client_socket.close()

    exit(0)

if __name__ == '__main__':
    main()

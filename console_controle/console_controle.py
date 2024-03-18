from datetime import datetime
import utile.network as network
import utile.message as message

# Constantes
IP_SERV_CONSOLE = ''
PORT_SERV_CONSOLE = 0

def main():
    client_socket = network.connect_to_serv()
    print("Connexion établie avec le serveur.")
    while True:
        message = input("Entrez votre message : ")

        # Envoyer le message au serveur
        network.send_message(client_socket, message)

        # Recevoir le message de confirmation du serveur
        confirmation_message = network.receive_message(client_socket)
        print("Confirmation du serveur :", confirmation_message)

    # Fermer la connexion avec le serveur
    client_socket.close()
    print("Connexion fermée.")

    exit(0)

if __name__ == '__main__':
    main()

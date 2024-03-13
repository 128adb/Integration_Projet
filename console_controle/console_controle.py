from datetime import datetime
import utile.network as network
import utile.message as message


# Constantes
IP_SERV_CONSOLE = ''
PORT_SERV_CONSOLE = 0



def main():
    client_socket = network.connect_to_serv()
    message = input("Entrez votre message : ")

        # Envoyer le message au serveur
    network.send_message(client_socket, message.encode('utf-8'))

        # Fermer la connexion avec le serveur
    client_socket.close()

    exit(0)

if __name__ == '__main__':
    main()

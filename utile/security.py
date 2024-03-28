from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
from Crypto.Util.number import getPrime
from random import randint
from hashlib import sha256
import utile.network as network
import pickle

def aes_encrypt(msg, key):
    """
    Fonction de chiffrement AES-GCM
    :param msg: (dict) Message au format de dictionnaire à chiffrer
    :param key: (bytes) Clé de chiffrement
    :return: (list) Liste des éléments nécessaires au déchiffrement --> [nonce, header, ciphertext, tag]
    """
    cipher = AES.new(key, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(msg.encode())
    liste = []
    liste.append(cipher.nonce, ciphertext, tag)
    return liste
def aes_decrypt(msg, key):
    """
    Fonction de déchiffrement AES-GCM
    :param msg: (list) Liste des éléments nécessaires au déchiffrement --> [nonce, header, ciphertext, tag]
    :param key: (bytes) Clé de chiffrement
    :return: (dict) Message déchiffré sous forme de dictionnaire
    """
    cipher = AES.new(key, AES.MODE_GCM, nonce=msg[0])
    plaintext = cipher.decrypt_and_verify(msg[1], msg[2])
    return plaintext.decode()
def gen_key(size=256):
    """
    Fonction générant une clé de chiffrement
    :param size: (bits) taille de la clé à générer
    :return: (bytes) nouvelle clé de chiffrement
    """
    return get_random_bytes(size // 8)


def diffie_hellman_send_key(s_client):
    """
    Fonction d'échange de clé via le protocole de Diffie Hellman (côté client).

    :param s_client: (socket) Connexion TCP du client avec qui échanger les clés.
    :return: (bytes) Clé partagée calculée.
    """

    # Génération d'un nombre premier de 1024 bits
    p = getPrime(1024)
    # Définition du générateur g (ici, 2)
    g = 2  # ou tout autre générateur approprié
    # Choix aléatoire de la clé privée du client
    a = randint(2, p - 1)
    # Calcul de la clé publique du client
    A = pow(g, a, p)
    # Envoi des paramètres (p, g, A) au serveur
    s_client.send(pickle.dumps((p, g, A)))
    # Réception de la clé publique du serveur
    B = pickle.loads(s_client.recv(4096))
    # Calcul de la clé partagée
    key = pow(B, a, p)
    # Conversion de la clé partagée en octets
    key_bytes = key.to_bytes((key.bit_length() + 7) // 8, byteorder='big')
    # Hachage de la clé partagée pour assurer une taille fixe
    return sha256(key_bytes).digest()


def diffie_hellman_recv_key(s_serveur):
    """
    Fonction d'échange de clé via le protocole de Diffie Hellman
    :param s_serveur: (socket) Connexion TCP du serveur avec qui échanger les clés
    :return: (bytes) Clé de 256 bits calculée
    """
    msg_init = network.receive_message(s_serveur)
    g = msg_init['g']   # g est un entier aléatoire
    p = msg_init['p']   # p est un nombre premier sur 256 bits
    public_key_a = msg_init['A']
    secret_key_b = randint(11, 20)

    key_calculate_b = (public_key_a ** secret_key_b) % p

    # Envoi de la clé publique de B
    network.send_message(s_serveur, {'B': (g ** secret_key_b) % p})

    return sha256(str(key_calculate_b).encode()).digest()
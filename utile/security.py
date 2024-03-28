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
    aad = b"Ceci est le head"
    nonce = get_random_bytes(12)

    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    cipher.update(aad)
    ciphertext, tag = cipher.encrypt_and_digest(pad(pickle.dumps(msg), AES.block_size))

    result = [cipher.nonce, aad, ciphertext, tag]
    return result
def aes_decrypt(msg, key):
    """
    Fonction de déchiffrement AES-GCM
    :param msg: (list) Liste des éléments nécessaires au déchiffrement --> [nonce, header, ciphertext, tag]
    :param key: (bytes) Clé de chiffrement
    :return: (dict) Message déchiffré sous forme de dictionnaire
    """
    nonce = 0
    aad = 1
    ciphertext = 2
    tag = 3

    cipher = AES.new(key, AES.MODE_GCM, nonce=msg[nonce])
    cipher.update(msg[aad])
    plaintext = pickle.loads(unpad(cipher.decrypt_and_verify(msg[ciphertext], msg[tag]), AES.block_size))
    return plaintext
def gen_key(size=256):
    """
    Fonction générant une clé de chiffrement
    :param size: (bits) taille de la clé à générer
    :return: (bytes) nouvelle clé de chiffrement
    """
    octets = {256: 32, 192: 24, 128: 16}
    if size in octets.keys():
        size = octets[size]
    return get_random_bytes(size)


def diffie_hellman_send_key(s_client):
    """
    Fonction d'échange de clé via le protocole de Diffie Hellman
    :param s_client: (socket) Connexion TCP du client avec qui échanger les clés
    :return: (bytes) Clé de 256 bits calculée
    """
    g = randint(9, 99)  # g est un entier aléatoire
    p = getPrime(32)    # p est un nombre premier sur 256 bits
    secret_key_a = randint(1, 10)
    public_key_a = (g ** secret_key_a) % p

    msg_init = {'g': g, 'p': p, 'A': public_key_a}
    network.send_message(s_client, msg_init)

    msg_resp = network.receive_message(s_client)
    public_key_b = msg_resp['B']

    key_calculate_a = (public_key_b ** secret_key_a) % p

    return sha256(str(key_calculate_a).encode()).digest()


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
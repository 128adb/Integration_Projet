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
    grd = get_random_bytes(12)
    head = b"header"
    cipher = AES.new(key, AES.MODE_GCM, nonce=grd)
    cipher.update(head)
    ciphertext, tag = cipher.encrypt_and_digest(pad(pickle.dumps(msg), AES.block_size))

    result = [cipher.nonce, head, ciphertext, tag]
    return result
def aes_decrypt(msg, key):
    """
    Fonction de déchiffrement AES-GCM
    :param msg: (list) Liste des éléments nécessaires au déchiffrement --> [nonce, header, ciphertext, tag]
    :param key: (bytes) Clé de chiffrement
    :return: (dict) Message déchiffré sous forme de dictionnaire
    """
    grd = 0
    head = 1
    ciphertext = 2
    tag = 3

    cipher = AES.new(key, AES.MODE_GCM, nonce=msg[grd])
    cipher.update(msg[head])
    plaintext = pickle.loads(unpad(cipher.decrypt_and_verify(msg[ciphertext], msg[tag]), AES.block_size))
    return plaintext
def gen_key(size=256):
    """
    Fonction générant une clé de chiffrement
    :param size: (bits) taille de la clé à générer
    :return: (bytes) nouvelle clé de chiffrement
    """
    oct = {256: 32, 192: 24, 128: 16}
    if size in oct.keys():
        size = oct[size]
    return get_random_bytes(size)


def diffie_hellman_send_key(s_client):
    """
    Fonction d'échange de clé via le protocole de Diffie Hellman
    :param s_client: (socket) Connexion TCP du client avec qui échanger les clés
    :return: (bytes) Clé de 256 bits calculée
    """
    g = randint(9, 99)  # g est un entier aléatoire
    p = getPrime(32)    # p est un nombre premier sur 256 bits
    cle_pv_a = randint(1, 10)
    cle_pb_a = (g ** cle_pv_a) % p

    msg_ini = {'g': g, 'p': p, 'A': cle_pb_a}
    network.send_message(s_client, msg_ini)

    msg_rep = network.receive_message(s_client)
    cle_pb_b = msg_rep['B']

    calcul_cle_a = (cle_pb_b ** cle_pv_a) % p

    return sha256(str(calcul_cle_a).encode()).digest()


def diffie_hellman_recv_key(s_serveur):
    """
    Fonction d'échange de clé via le protocole de Diffie Hellman
    :param s_serveur: (socket) Connexion TCP du serveur avec qui échanger les clés
    :return: (bytes) Clé de 256 bits calculée
    """
    msg_ini = network.receive_message(s_serveur)
    g = msg_ini['g']   # g est un entier aléatoire
    p = msg_ini['p']   # p est un nombre premier sur 256 bits
    cle_pb_a = msg_ini['A']
    cle_pv_b = randint(11, 20)

    calcul_cle_b = (cle_pb_a ** cle_pv_b) % p

    # Envoi de la clé publique de B
    network.send_message(s_serveur, {'B': (g ** cle_pv_b) % p})

    return sha256(str(calcul_cle_b).encode()).digest()
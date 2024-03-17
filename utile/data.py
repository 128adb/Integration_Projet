import sqlite3

# Constantes
DB_FILENAME = '../serveur_cles/data/victims.sqlite'


def connect_db():
    """
    Initialise la connexion vers la base de donnée
    :return: La connexion établie avec la base de donnée
    """
    connexion = sqlite3.connect(DB_FILENAME)
    if connexion:
        print('Connexion avec la DB effectué')
    return connexion
def insert_data(conn, table, items, data):
    """
    Insère des données de type 'items' avec les valeurs 'data' dans la 'table' en utilisant la connexion 'conn' existante
    :param conn: la connexion existante vers la base de donnée
    :param table: la table dans laquelle insérer les données
    :param items: le nom des champs à insérer
    :param data: la valeur des champs à insérer
    :return: Néant
    """
    insert = "INSERT INTO " + table + " " + items + " VALUES " + data
    cursor = conn.cursor()
    cursor.execute(insert)
    conn.commit()
    cursor.close()

def select_data(conn, select_query):
    """
    Exécute un SELECT dans la base de donnée (conn) et retourne les records correspondants
    :param conn: la connexion déjà établie à la base de donnée
    :param select_query: la requête du select à effectuer
    :return: les records correspondants au résultats du SELECT
    """
    cursor = conn.cursor()
    cursor.execute(select_query)
    records = cursor.fetchall()
    cursor.close()
    return records

def get_list_victims(conn):
    """
    Retourne la liste des victimes présente dans la base de donnée
    (N'oubliez pas de vous servir de la fonction précédente pour effectuer la requête)
    :param conn: la connexion déjà établie à la base de donnée
    :return: La liste des victimes
    """
    select = f'SELECT * FROM victims '

    list_victim = select_data(conn, select)
    return list_victim  

def get_list_history(conn, hash):
    """
    Retourne l'historique correspondant à la victime 'id_victim'
    :param conn: la connexion déjà établie à la base de donnée
    :param id_victim: l'identifiant de la victime
    :return: la liste de son historique
    """
    select = f' SELECT hash, datetime, state FROM states WHERE HASH = {hash}'
    list_history = select_data(conn,select)
    return list_history
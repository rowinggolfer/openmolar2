CREATE TABLE info (
key VARCHAR(20),
value VARCHAR(20),
CONSTRAINT pk_info PRIMARY KEY (key)
);

CREATE TABLE databases (
ix SERIAL NOT NULL,
name VARCHAR(50) NOT NULL,
description VARCHAR(250),
created TIMESTAMP NOT NULL,
CONSTRAINT pk_databases PRIMARY KEY (ix)
);

CREATE TABLE users (
ix SERIAL NOT NULL,
name VARCHAR(20) NOT NULL,
store_password BOOL NOT NULL DEFAULT false,
psword bytea,
CONSTRAINT pk_users PRIMARY KEY (ix),
CONSTRAINT users_passwd CHECK((psword is NOT NULL AND store_password) OR (psword is NULL AND NOT store_password))
);

insert into info values ('version', '1.0');

grant all privileges on info to openmolar;
grant all privileges on databases to openmolar;
grant all privileges on databases_ix_seq to openmolar;
grant all privileges on users to openmolar;
grant all privileges on users_ix_seq to openmolar;


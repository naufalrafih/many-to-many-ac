CREATE TABLE certcenter (
certcenter_id INTEGER PRIMARY KEY,
certcenter_ip_address TEXT NOT NULL,
master_key INTEGER NOT NULL,
public_key INTEGER NOT NULL
);

CREATE TABLE institutes (
institute_id INTEGER PRIMARY KEY,
institute_name TEXT NOT NULL UNIQUE,
institute_ip_address TEXT NOT NULL UNIQUE,
institute_key INTEGER NOT NULL UNIQUE
);

CREATE TABLE users (
uid INTEGER PRIMARY KEY,
user_name TEXT NOT NULL UNIQUE
);
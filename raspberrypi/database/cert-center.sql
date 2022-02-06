CREATE TABLE certcenter (
certcenter_name TEXT PRIMARY KEY,
certcenter_ip_address TEXT NOT NULL,
key_b TEXT NOT NULL
);

CREATE TABLE institutes (
institute_id INTEGER PRIMARY KEY AUTOINCREMENT,
institute_name TEXT NOT NULL UNIQUE,
institute_ip_address TEXT NOT NULL UNIQUE,
key_a TEXT NOT NULL UNIQUE
);

CREATE TABLE users (
user_id INTEGER PRIMARY KEY AUTOINCREMENT,
user_name TEXT NOT NULL UNIQUE,
uid TEXT NOT NULL UNIQUE
);
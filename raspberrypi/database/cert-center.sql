CREATE TABLE certcenter (
certcenter_name TEXT PRIMARY KEY,
certcenter_ip_address TEXT NOT NULL,
key_b TEXT NOT NULL
);

CREATE TABLE institutes (
institute_id INTEGER PRIMARY KEY AUTOINCREMENT,
institute_name TEXT NOT NULL,
institute_ip_address TEXT NOT NULL,
key_a TEXT NOT NULL
);

CREATE TABLE users (
user_id INTEGER PRIMARY KEY AUTOINCREMENT,
user_name TEXT NOT NULL,
uuid TEXT NOT NULL
);


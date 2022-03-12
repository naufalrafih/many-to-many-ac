CREATE TABLE certcenter (
certcenter_id INTEGER PRIMARY KEY,
certcenter_ip_address TEXT NOT NULL
);

CREATE TABLE institute (
institute_id INTEGER PRIMARY KEY,
institute_name TEXT NOT NULL,
institute_ip_address TEXT NOT NULL,
institute_key INTEGER NOT NULL,
public_key INTEGER NOT NULL
);

CREATE TABLE assets (
asset_name TEXT PRIMARY KEY,
asset_ip_address TEXT NOT NULL UNIQUE
);

CREATE TABLE bookings (
book_id INTEGER PRIMARY KEY,
uid INTEGER NOT NULL,
asset_name TEXT NOT NULL,
start_date TEXT NOT NULL, /* #FORMAT: DDMMYYYY */
end_date TEXT NOT NULL, /* FORMAT: DDMMYYYY */
FOREIGN KEY(asset_name) REFERENCES assets(asset_name)
);

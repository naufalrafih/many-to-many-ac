CREATE TABLE certcenter (
certcenter_name TEXT PRIMARY KEY,
certcenter_ip_address TEXT NOT NULL
);

CREATE TABLE institute (
institute_id INTEGER PRIMARY KEY,
institute_name TEXT,
institute_ip_address TEXT NOT NULL,
public_key TEXT NOT NULL,
private_key TEXT NOT NULL,
key_a TEXT NOT NULL
);

CREATE TABLE assets (
asset_name TEXT PRIMARY KEY NOT NULL UNIQUE,
asset_ip_address TEXT NOT NULL UNIQUE
);

CREATE TABLE bookings (
book_id INTEGER PRIMARY KEY AUTOINCREMENT,
otp_counter INTEGER NOT NULL,
asset_name TEXT NOT NULL,
start_date TEXT NOT NULL, /* #FORMAT: YYYY/MM/DD */
end_date TEXT NOT NULL, /* FORMAT: YYYY/MM/DD */
FOREIGN KEY(asset_name) REFERENCES assets(asset_name)
);

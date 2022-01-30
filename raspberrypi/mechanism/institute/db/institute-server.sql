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
asset_id INTEGER PRIMARY KEY AUTOINCREMENT,
asset_name TEXT NOT NULL,
asset_ip_address TEXT NOT NULL
);

CREATE TABLE bookings (
book_id INTEGER PRIMARY KEY AUTOINCREMENT,
otp_counter INTEGER NOT NULL,
booked_asset_id INTEGER NOT NULL,
start_date TEXT NOT NULL, /* #FORMAT: YYYY/MM/DD */
end_date TEXT NOT NULL, /* FORMAT: YYYY/MM/DD */
FOREIGN KEY(booked_asset_id) REFERENCES assets(asset_id)
);

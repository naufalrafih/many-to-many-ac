# Database SQLite

|Database|Table|Columns|
|-------|-------|-------|
|cert-center|institutes|institute_id, institute_name, institute_ip_address, public_key|
| |users|user_id, user_name, uuid|
|institute|assets|asset_id, asset_name, asset_ip_address|
| |bookings|book_id, otp_counter, booked_asset_id, start_date, end_date|
<br>

Notes:
* Setiap connect ke database gunakan flag ```PRAGMA foreign_keys=1```

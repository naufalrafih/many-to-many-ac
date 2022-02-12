from flask import Flask, render_template, request
import requests
import sqlite3
from Crypto.PublicKey import RSA

app = Flask(__name__)

CERTCENTER_PORT=35753
INSTITUTE_PORT=35754

@app.route("/home", methods=["GET"])
def hello_world():
    try:
        response_body = render_template("home.html")
        response_code = 200
        return response_body, response_code
    except Exception as e:
        print(f"Error! Exception: {e}")
        return f"Unsuccessful", 500
    
@app.route("/home/initialize", methods=["GET"])
def initialize_institute():
    try:
        con = sqlite3.connect("db/institute-server.db")
        cur = con.cursor()
        if ((cur.execute("SELECT * FROM certcenter").fetchall()) and (cur.execute("SELECT * FROM institute").fetchall())):
            initialized = True
        else:
            initialized = False

        response_body = render_template("initialize_institute.html", initialized=initialized)
        response_code = 200
        return response_body, response_code
    except Exception as e:
        print(f"Error! Exception: {e}")
        return f"Unsuccessful", 500

@app.route("/api/initialize", methods=["POST"])
def api_initialize_institute():
    try:
        data = request.get_json()
        certcenter_ip_address = data["certcenter_ip_address"]
        institute_name = data["institute_name"]

        #Populate certcenter DB
        con = sqlite3.connect("db/institute-server.db")
        cur = con.cursor()
        cur.execute("DELETE FROM certcenter")
        cur.execute("INSERT INTO certcenter (certcenter_name, certcenter_ip_address) VALUES (?, ?)",
                    ("Cert Center", certcenter_ip_address))

        #Send request to Cert Center API /api/register/institute
        request_body = {"institute_name":institute_name}
        response = requests.post(f"https://{certcenter_ip_address}:{CERTCENTER_PORT}/api/register/institute", verify="certs/certcenter.pem", json=request_body)
        if (response.status_code == 200):        
            response_json = response.json()
            private_key = RSA.generate(2048)
            public_key = private_key.public_key()

            #Variables to insert into DB
            institute_id = response_json["institute_id"]
            institute_ip_address = response_json["institute_ip_address"]
            private_key_pem = private_key.export_key("PEM")
            public_key_pem = public_key.export_key("PEM")
            key_a = response_json["key_a"]

            cur.execute("DELETE FROM institute")
            cur.execute("INSERT INTO institute (institute_id, institute_name, institute_ip_address, public_key, private_key, key_a) VALUES (?, ?, ?, ?, ?, ?)",
                        (institute_id, institute_name, institute_ip_address, public_key_pem, private_key_pem, key_a))
        else:
            raise Exception("Request to Cert Center API /api/register/institute failed")

        con.commit()
        con.close()
        response_body = "Successful."
        response_code = 200
        return response_body, response_code
    except Exception as e:
        print(f"Error! Exception: {e}")
        return f"Unsuccessful", 500

@app.route("/api/register/asset", methods=["POST"])
def register_asset():
    try:
        data = request.get_json()
        asset_name = data["asset_name"]
        asset_ip_address = request.remote_addr

        print("Registering asset:")
        print(f"Asset name: {asset_name}")
        print(f"Asset IP address: {asset_ip_address}")

        is_ipaddress_unique = True
        con = sqlite3.connect("db/institute-server.db")
        cur = con.cursor()
        rows = cur.execute("SELECT asset_ip_address from assets").fetchall()
        for row in range(len(rows)):
            if rows[row][0] == asset_ip_address:
                is_ipaddress_unique = False

        if is_ipaddress_unique:
            cur.execute("REPLACE INTO assets (asset_name, asset_ip_address) VALUES (?, ?)",
                        (asset_name, asset_ip_address))

            #Getting key_A for the reader
            cur.execute("SELECT key_a FROM institute")
            key_a = cur.fetchall()[0][0]

            con.commit()
            con.close()

            response_body = {"key_a":key_a}
            response_code = 200
        else:
            response_body = "IP address already registered"
            response_code = 400
        return response_body, response_code
    except Exception as e:
        print(f"Error! Exception {e}")
        return f"Unsuccessful", 500

@app.route("/api/booking/data", methods=["POST"])
def booking_data():
    try:
        data = request.get_json()
        asset_name = data["asset_name"]
        start_date = data["start_date"]
        end_date = data["end_date"]
        uid = data["uid"]

        is_booking_new = True
        con = sqlite3.connect("db/institute-server.db")
        cur = con.cursor()
        rows = cur.execute("SELECT * FROM bookings").fetchall()
        for row in range(len(rows)):
            if (rows[row[2]] == asset_name) and (rows[row[3]] == start_date) and (rows[row[4]] == end_date):
                is_booking_new = False

        if is_booking_new:
            # cek lagi tanggalnya dulu barangnya kepake ga
            cur.execute("INSERT INTO bookings (otp_counter, asset_name, start_date, end_date) VALUES (0, ?, ?, ?)",
                        (asset_name, start_date, end_date))
        institute_id = cur.execute("SELECT institute_id FROM institutes WHERE institute_name=? and institute_ip_address=?", (institute_name, institute_ip_address)).fetchall()[0][0]
        book_id = cur.execute("SELECT book_id FROM bookings WHERE asset_name = ")
            #langsung siapin ttd digital dst

        cur.commit()
        con.close()

        response_body = "OK!"
        response_code = 200
    except Exception as e:
        print(f"Error! Exception {e}")
        return f"unsuccessful", 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=INSTITUTE_PORT, ssl_context=('secrets/cert.pem','secrets/key.pem'), debug=True)
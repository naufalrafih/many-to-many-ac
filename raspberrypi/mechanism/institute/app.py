from flask import Flask, render_template, request
import requests
import sqlite3
from requests.packages.urllib3.exceptions import SubjectAltNameWarning
import os
from Crypto.PublicKey import RSA

app = Flask(__name__)

CERTCENTER_PORT=35753
INSTITUTE_PORT=35754
server_directory = os.path.dirname(os.path.abspath(__file__))

@app.route("/home", methods=["GET"])
def hello_world():
    try:
        response_text = render_template("home.html")
        response_code = 200
        return response_text, response_code
    except Exception as e:
        print(f"Error! Exception: {e}")
        return f"Unsuccessful", 500
    
@app.route("/home/initialize", methods=["GET"])
def initialize_institute():
    try:
        con = sqlite3.connect("db/institute-server.db")
        cur = con.cursor()
        if (cur.execute("SELECT * FROM certcenter").fetchall()):
            initialized = True
        else:
            initialized = False

        response_text = render_template("initialize_institute.html", initialized=initialized)
        response_code = 200
        return response_text, response_code
    except Exception as e:
        print(f"Error! Exception: {e}")
        return f"Unsuccessful", 500

@app.route("/api/initialize", methods=["POST"])
def api_initialize_institute():
    try:
        data = request.get_json()
        certcenter_data = data["certcenter_data"]
        assets_data = data["assets_data"]

        requests.packages.urllib3.disable_warnings()
        r_certcenter = requests.post(request.url_root + "api/initialize/certcenter", verify=f"{server_directory}/secrets/cert.pem", json=certcenter_data)
        r_institute = requests.post(request.url_root + "api/initialize/assets", verify=f"{server_directory}/secrets/cert.pem", json=assets_data)
        if (r_certcenter.ok and r_institute.ok):
            response_text = "OK!"
            response_code = 200
            return response_text, response_code
    except Exception as e:
        print(f"Error! Exception: {e}")
        return f"Unsuccessful", 500

@app.route("/api/initialize/certcenter", methods=["POST"])
def initialize_certcenter():
    try:
        # Create cert center data
        data = request.get_json()
        certcenter_name = data["certcenter_name"]
        certcenter_ip_address = data["certcenter_ip_address"]
        print(f"Cert Center - Name: {certcenter_name}, IP: {certcenter_ip_address}")

        # Insert into DB
        con = sqlite3.connect("db/institute-server.db")
        cur = con.cursor()
        cur.execute("DELETE FROM certcenter")
        cur.execute("INSERT INTO certcenter (certcenter_name, certcenter_ip_address) VALUES (?, ?)",
                        (certcenter_name, certcenter_ip_address))
        con.commit()
        con.close()

        response_text = "OK!"
        response_code = 200
        return response_text, response_code
    except Exception as e:
        print(f"Error! Exception: {e}")
        return f"Unsuccessful", 500

@app.route("/api/initialize/assets", methods=["POST"])
def initialize_asset():
    try:
        # Create cert center data
        data = request.get_json()

        # Insert into DB
        con = sqlite3.connect("db/institute-server.db")
        cur = con.cursor()
        cur.execute("DELETE FROM assets")
        for index, asset in enumerate(data):
            print(f"Asset no. {index+1} - Name: {asset['asset_name']}, IP: {asset['asset_ip_address']}. Inserting into DB.")
            cur.execute("INSERT INTO assets (asset_name, asset_ip_address) VALUES (?, ?)",
                        (asset['asset_name'], asset['asset_ip_address']))
        con.commit()
        con.close()

        response_text = "OK!"
        response_code = 200
        return response_text, response_code
    except Exception as e:
        print(f"Error! Exception: {e}")
        return f"Unsuccessful", 500

@app.route("/api/register", methods=["POST"])
def register_institute():
    try:
        #Parse data
        data = request.get_json()
        institute_id = data["institute_id"]
        institute_name = data["institute_name"]
        institute_ip_address = data["institute_ip_address"]
        key_a = data["key_a"]

        #Generate public & private key
        private_key = RSA.generate(2048)
        public_key = private_key.public_key()
        private_key_pem = private_key.export_key("PEM").decode("utf-8")
        public_key_pem = public_key.export_key("PEM").decode("utf-8")

        #Insert into DB
        con = sqlite3.connect("db/institute-server.sql")
        cur = con.cursor()
        cur.execute("INSERT INTO institute (institute_id, institute_name, institute_ip_address, public_key, private_key, key_a) VALUES (?, ?, ?, ?, ?, ?)",
                    (institute_id, institute_name, institute_ip_address, public_key_pem, private_key_pem, key_a))
        con.commit()
        con.close()

        response_text = "OK!"
        response_code = 200
        return response_text, response_code
    except Exception as e:
        print(f"Error! Exception {e}")
        return f"Unsuccessful", 500

if __name__ == "__main__":
    requests.packages.urllib3.disable_warnings(SubjectAltNameWarning)
    app.run(host='0.0.0.0', port=INSTITUTE_PORT, ssl_context=('secrets/cert.pem','secrets/key.pem'), debug=True)
from flask import Flask, render_template, request
import sqlite3
from Crypto.PublicKey import RSA
import json

app = Flask(__name__)

CERTCENTER_PORT=35753
INSTITUTE_PORT=35754

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
        return "OK."
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

        #Inserting into database
        con = sqlite3.connect("db/institute-server.db")
        cur = con.cursor()
        cur.execute("REPLACE INTO assets (asset_id, asset_name, asset_ip_address) VALUES ((SELECT asset_id FROM assets WHERE asset_name = ?), ?, ?)",
                    (asset_name, asset_name, asset_ip_address))

        #Getting key_A for the reader
        cur.execute("SELECT key_a FROM institute")
        key_a = cur.fetchall()[0][0]

        con.commit()
        con.close()

        response_text = json.dumps({"key_a":key_a})
        response_code = 200
        return response_text, response_code
    except Exception as e:
        print(f"Error! Exception {e}")
        return f"Unsuccessful", 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=INSTITUTE_PORT, ssl_context=('secrets/cert.pem','secrets/key.pem'), debug=True)
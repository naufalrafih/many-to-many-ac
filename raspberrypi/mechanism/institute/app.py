from flask import Flask, render_template, request
import requests
import sqlite3
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

@app.route("/api/register/asset", methods=["POST"])
def register_institute():
    try:
        response_text = "OK!"
        response_code = 200
        return response_text, response_code
    except Exception as e:
        print(f"Error! Exception {e}")
        return f"Unsuccessful", 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=INSTITUTE_PORT, ssl_context=('secrets/cert.pem','secrets/key.pem'), debug=True)
from flask import Flask, render_template, request
import requests
import sqlite3
import os
import json

app = Flask(__name__)

CERTCENTER_PORT=35753
INSTITUTE_PORT=35754

@app.route("/home", methods=["GET"])
def home_page():
    try:
        con = sqlite3.connect("db/cert-center.db")
        cur = con.cursor()
        if (cur.execute('SELECT * FROM certcenter').fetchall()):
            initialized=True
        else:
            initialized=False
        response_text = render_template('home.html', initialized=initialized)
        response_code = 200
        return response_text, response_code
    except Exception as e:
        print(f"Error! Exception: {e}")
        return f"Unsuccessful", 500

@app.route("/api/initialize", methods=["POST"])
def initialize_cert_center():
    try:
        con = sqlite3.connect('db/cert-center.db')
        cur = con.cursor()
        cur.execute('SELECT * FROM certcenter')
        row = cur.fetchall()
        print(row)
        if not row:
            print("table is empty")
            certcenter_name = "certcenter"
            certcenter_ip_address = "10.0.0.3"
            key_b = os.urandom(6).hex()
            cur.execute("INSERT INTO certcenter (certcenter_name, certcenter_ip_address, key_b) VALUES (?, ?, ?)",
                (certcenter_name, certcenter_ip_address, key_b))
            response_text = "Initialized"
            response_code = 200
        else:
            print("table is not empty")
            response_text = "Already initialized"
            response_code = 500
        con.commit()
        con.close()
        return response_text, response_code
    except Exception as e:
        print(f"Error! Exception: {e}")
        return f"Unsuccessful", 500

@app.route("/api/register/institute", methods=["POST"])
def register_institute():
    try:
        data = request.get_json()
        institute_name = data["institute_name"]
        institute_ip_address = request.remote_addr
        key_a = os.urandom(6).hex()

        con = sqlite3.connect('db/cert-center.db')
        cur = con.cursor()
        cur.execute("REPLACE INTO institutes (institute_id, institute_name, institute_ip_address, key_a) VALUES ((SELECT institute_id FROM institutes WHERE institute_name = ?), ?, ?, ?)",
            (institute_name, institute_name, institute_ip_address, key_a))
        institute_id = cur.execute("SELECT institute_id FROM institutes WHERE institute_name=? and institute_ip_address=?", (institute_name, institute_ip_address)).fetchall()[0][0]
        con.commit()
        con.close()

        response_data = {"institute_id": institute_id, "key_a": key_a}
        response_data_json = json.dumps(response_data)

        response_code = 200
        return response_data_json, response_code
    except Exception as e:
        print(f"Error! Exception: {e}")
        return f"Unsuccessful", 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=CERTCENTER_PORT, ssl_context=('secrets/cert.pem','secrets/key.pem'), debug=True)
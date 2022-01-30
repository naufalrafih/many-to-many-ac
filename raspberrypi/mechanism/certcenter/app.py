from flask import Flask, render_template
import sqlite3
import requests
import os

app = Flask(__name__)

@app.route("/home")
def home_page():
    try:
        con = sqlite3.connect("cert-center.db")
        cur = con.cursor()
        if (cur.execute('SELECT * FROM certcenter')):
            initialized=True
        else:
            initialized=False
        response_text = render_template('home.html', initialized=initialized)
        response_code = 200
        return response_text, response_code
    except Exception as e:
        return f"Error! Exception: {e}", 500

@app.route("/api/initialize")
def initialize_cert_center():
    try:
        con = sqlite3.connect('cert-center.db')
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
        return f"Error! Exception: {e}", 500

if __name__ == "__main__":
    app.run(host='0.0.0.0',ssl_context=('cert.pem','key.pem'),debug=True)
from flask import Flask
import requests
import sqlite3
import os

app = Flask(__name__)

ADVERSARY_HOST="raspberrypi3"
ADVERSARY_PORT="5000"

@app.route("/")
def hello_world():
    return("Connection Successful!")

@app.route("/request")
def request():
    r = requests.get(f'https://{ADVERSARY_HOST}:{ADVERSARY_PORT}/')
    print("Status code:",r.status_code)
    print("Body:",r.content)
    return("Request Successful!")

@app.route("/api/initialize")
def initialize():
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
    else:
        print("table is not empty")
        return("already initialized")
    con.commit()
    con.close()
    return("initialized")

if __name__ == "__main__":
    app.run(host='0.0.0.0',ssl_context=('cert.pem','key.pem'),debug=True)
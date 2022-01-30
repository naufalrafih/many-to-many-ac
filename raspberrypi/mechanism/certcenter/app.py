from flask import Flask, render_template
import sqlite3
import requests

app = Flask(__name__)

@app.route("/home")
def home_page():
    con = sqlite3.connect("cert-center.db")
    cur = con.cursor()

    if (cur.execute('SELECT * FROM certcenter')):
        initialized=True
    else:
        initialized=False
    return render_template('home.html', initialized=initialized)

@app.route("/api/initialize")
def initialize_cert_center():
    return ("OK")

if __name__ == "__main__":
    app.run(host='0.0.0.0',ssl_context=('cert.pem','key.pem'),debug=True)
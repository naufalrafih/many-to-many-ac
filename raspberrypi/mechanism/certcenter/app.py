from flask import Flask, render_template
import sqlite3
import requests

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
        response_text = "OK"
        response_code = 200
        return response_text, response_code
    except Exception as e:
        return f"Error! Exception: {e}", 500

if __name__ == "__main__":
    app.run(host='0.0.0.0',ssl_context=('cert.pem','key.pem'),debug=True)
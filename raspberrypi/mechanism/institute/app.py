from flask import Flask, render_template, request
import requests
import os
import sqlite3

app = Flask(__name__)

server_directory = os.path.dirname(os.path.realpath(__file__))

@app.route("/home")
def hello_world():
    try:
        response_text = render_template("home.html")
        response_code = 200
        return response_text, response_code
    except Exception as e:
        return f"Error! Exception: {e}", 500
    
@app.route("/home/initialize", methods=("GET", "POST"))
def initialize_institute():
    try:
        con = sqlite3.connect("db/institute-server.db")
        cur = con.cursor()
        if (cur.execute("SELECT * FROM certcenter").fetchall()):
            initialized = True
        else:
            initialized = False

        response_text = render_template("initialize_institute.html")
        response_code = 200
        return response_text, response_code
    except Exception as e:
        return f"Error! Exception: {e}", 500

@app.route("/api/initialize", methods=("GET", "POST"))
def api_initialize_institute():
    try:
        if request.method == "POST":
            print(request.data)
            print(request.headers)
            data = request.get_json()
            certcenter_name = data["certcenter_name"]
            certcenter_ip_address = data["certcenter_ip_address"]
            asset_name = data["asset_name"]
            asset_ip_address =  data["asset_ip_address"]
            print(certcenter_name)
            print(certcenter_ip_address)
            print(asset_name)
            print(asset_ip_address)
            response_text = "OK!"
            response_code = 200
            return response_text, response_code
        elif request.method == "GET":
            return "GET"
    except Exception as e:
        print(e)
        return f"Error! Exception: {e}", 500

if __name__ == "__main__":
    app.run(host='0.0.0.0',ssl_context=('secrets/cert.pem','secrets/key.pem'),debug=True)
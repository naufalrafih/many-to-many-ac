from flask import Flask, render_template, request
import requests
import sqlite3

app = Flask(__name__)

@app.route("/home", methods=["GET"])
def hello_world():
    try:
        response_text = render_template("home.html")
        response_code = 200
        return response_text, response_code
    except Exception as e:
        return f"Error! Exception: {e}", 500
    
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
        return f"Error! Exception: {e}", 500

@app.route("/api/initialize", methods=["POST"])
def api_initialize_institute():
    try:
        if request.method == "POST":
            data = request.get_json()
            certcenter_data = data["certcenter_data"]
            assets_data = data["assets_data"]

            requests.packages.urllib3.disable_warnings()
            r_certcenter = requests.post(request.url_root + "api/initialize/certcenter", verify=False, json=certcenter_data)
            r_institute = requests.post(request.url_root + "api/initialize/assets", verify=False, json=assets_data)
            if (r_certcenter.ok and r_institute.ok):
                response_text = "OK!"
                response_code = 200
                return response_text, response_code
        elif request.method == "GET":
            return "GET"
    except Exception as e:
        return f"Error! Exception: {e}", 500

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
        return f"Error! Exception : {e}", 500

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
        return f"Error! Exception : {e}", 500

if __name__ == "__main__":
    app.run(host='0.0.0.0',ssl_context=('secrets/cert.pem','secrets/key.pem'),debug=True)
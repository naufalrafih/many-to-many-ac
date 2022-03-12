from flask import Flask, render_template, request
import requests
import sqlite3
import pyotp
import base64
import uuid
import datetime

app = Flask(__name__)

CERTCENTER_PORT=35753
INSTITUTE_PORT=35754

@app.route("/home", methods=["GET"])
def hello_world():
    try:
        response_body = render_template("home.html")
        response_code = 200
        return response_body, response_code
    except Exception as e:
        print(f"Error! Exception: {e}")
        return f"Unsuccessful", 500
    
@app.route("/home/initialize", methods=["GET"])
def initialize_institute():
    try:
        con = sqlite3.connect("db/institute-server.db")
        cur = con.cursor()
        if ((cur.execute("SELECT * FROM certcenter").fetchall()) and (cur.execute("SELECT * FROM institute").fetchall())):
            initialized = True
        else:
            initialized = False

        response_body = render_template("initialize_institute.html", initialized=initialized)
        response_code = 200
        return response_body, response_code
    except Exception as e:
        print(f"Error! Exception: {e}")
        return f"Unsuccessful", 500

@app.route("/api/initialize", methods=["POST"])
def api_initialize_institute():
    try:
        data = request.get_json()
        certcenter_ip_address = data["certcenter_ip_address"]
        institute_name = data["institute_name"]

        #Connect to DB
        con = sqlite3.connect("db/institute-server.db")
        cur = con.cursor()

        #Send request to Cert Center API /api/register/institute
        request_body = {"institute_name":institute_name}
        response = requests.post(f"https://{certcenter_ip_address}:{CERTCENTER_PORT}/api/register/institute", verify="certs/certcenter.pem", json=request_body)
        if (response.status_code == 200):        
            response_json = response.json()

            #Variables to insert into DB
            institute_id = response_json["institute_id"]
            institute_ip_address = response_json["institute_ip_address"]
            institute_key = response_json["institute_key"]
            public_key = response_json["public_key"]
            certcenter_id = response_json["certcenter_id"]

            cur.execute("DELETE FROM institute")
            cur.execute("INSERT INTO institute (institute_id, institute_name, institute_ip_address, institute_key, public_key) VALUES (?, ?, ?, ?, ?)",
                        (institute_id, institute_name, institute_ip_address, institute_key, public_key))
        else:
            raise Exception("Request to Cert Center API /api/register/institute failed")

        #Populate certcenter DB
        cur.execute("DELETE FROM certcenter")
        cur.execute("INSERT INTO certcenter (certcenter_id, certcenter_ip_address) VALUES (?, ?)",
                    (certcenter_id, certcenter_ip_address))

        con.commit()
        con.close()
        response_body = "Successful."
        response_code = 200
        return response_body, response_code
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

        #Registering asset to database
        con = sqlite3.connect("db/institute-server.db")
        cur = con.cursor()
        cur.execute("REPLACE INTO assets (asset_name, asset_ip_address) VALUES (?, ?)",
                    (asset_name, asset_ip_address))

        #Getting institute_key for the reader
        cur.execute("SELECT institute_key FROM institute")
        institute_key = cur.fetchall()[0][0]

        #Closing connection to database
        con.commit()
        con.close()

        response_body = {"institute_key":institute_key}
        response_code = 200
        return response_body, response_code
    except Exception as e:
        print(f"Error! Exception {e}")
        return f"Unsuccessful", 500

@app.route("/api/booking/data", methods=["POST"])
def booking_data():
    try:
        data = request.get_json()
        asset_name = data["asset_name"]
        start_date = data["start_date"]
        end_date = data["end_date"]
        uid = data["uid"]

        #Check if booking already exists or not
        is_booking_new = True
        con = sqlite3.connect("db/institute-server.db")
        con.execute("PRAGMA foreign_keys = ON")
        cur = con.cursor()
        rows = cur.execute("SELECT * FROM bookings").fetchall()
        for row in rows:
            if (row[2] == asset_name) and (row[3] == start_date) and (row[4] == end_date):
                is_booking_new = False

        #In case booking already exists
        if not is_booking_new:
            response_body = "Booking already exist."
            response_code =  400
        else: #In case booking doesn't exist yet  
            #Check if asset is already booked during those dates or not.
            is_booked = False
            rows = cur.execute("SELECT * FROM bookings WHERE asset_name = ?", (asset_name,)).fetchall()
            requested_start_date = datetime.strptime(start_date, "%d%m%Y")
            requested_end_date = datetime.strptime(end_date, "%d%m%Y")
            for row in rows:
                db_start_date = datetime.strptime(row[3], "%d%m%Y")
                db_end_date = datetime.strptime(row[4], "%d%m%Y")

                is_start_date_inbetween = db_start_date <= requested_start_date <= db_end_date
                is_end_date_inbetween = db_start_date <= requested_end_date <= db_end_date
                if (is_start_date_inbetween or is_end_date_inbetween): #If asset is already booked during those dates
                    is_booked = True

            if is_booked: #If asset is already booked
                response_body = "Asset is already booked"
                response_code = 400
            else: #If asset is unbooked
                book_id = uuid.uuid4().int
                cur.execute("INSERT INTO bookings (book_id, uid, asset_name, start_date, end_date) VALUES (?, ?, ?, ?, ?)",
                            (book_id, uid, asset_name, start_date, end_date))       
                response_body = {"book_id": book_id, "uid":uid, "asset_name":asset_name, "start_date":start_date, "end_date":end_date}
                response_code = 200

        cur.commit()
        con.close()
        return response_body, response_code
    except Exception as e:
        print(f"Error! Exception {e}")
        return f"Unsuccessful", 500

@app.route("/api/booking/getasset", methods=["GET"])
def booking_getasset():
    try:
        data = request.get_json()
        start_date = data["start_date"]
        end_date = data["end_date"]

        con = sqlite3.connect("db/institute-server.db")
        cur = con.cursor()
        rows = cur.execute("SELECT * FROM bookings").fetchall()

        #Search assets that are booked during the time window
        booked_assets = []
        requested_start_date = datetime.strptime(start_date, "%d%m%Y")
        requested_end_date = datetime.strptime(end_date, "%d%m%Y")
        for row in rows: #Iterate every booking
            db_start_date = datetime.strptime(row[3], "%d%m%Y")
            db_end_date = datetime.strptime(row[4], "%d%m%Y")
            is_start_date_inbetween = db_start_date <= requested_start_date <= db_end_date
            is_end_date_inbetween = db_start_date <= requested_end_date <= db_end_date
            if (is_start_date_inbetween or is_end_date_inbetween):
                booked_assets.append(row[2]) #Append assets that are booked during the time window to booked_assets

        #Append assets that are unbooked
        rows = cur.execute("SELECT asset_name FROM assets").fetchall()
        assets = []
        for row in rows:
            if row[0] not in booked_assets:
                assets.append(row[0])

        cur.commit()
        con.close()

        response_body = {"assets": assets}
        response_code = 200
        return response_body, response_code
    except Exception as e:
        print(f"Error! Exception {e}")
        return f"Unsuccessful", 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=INSTITUTE_PORT, ssl_context=('secrets/cert.pem','secrets/key.pem'), debug=True)
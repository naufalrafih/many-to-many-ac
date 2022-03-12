from flask import Flask, render_template, request # type: ignore
import sqlite3
import os
import time
from pirc522 import RFID # type: ignore
import RPi.GPIO as GPIO # type: ignore
import requests
from Crypto.Util import number

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
        con.commit()
        con.close()
        response_body = render_template('home.html', initialized=initialized)
        response_code = 200
        return response_body, response_code
    except Exception as e:
        print(f"Error! Exception: {e}")
        return f"Unsuccessful", 500

@app.route("/home/register/user", methods=["GET"])
def register_user():
    try:
        response_body = render_template("register_user.html")
        response_code = 200
        return response_body, response_code
    except Exception as e:
        print(f"Error! Exception: {e}")
        return f"Unsuccessful", 500

@app.route("/home/booking", methods=["GET"])
def booking_page():
    try:
        response_body = render_template("booking_page.html")
        response_code = 200
        return response_body, response_code
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
        if not row:
            certcenter_id = int.from_bytes(os.urandom(4),'big')
            certcenter_ip_address = request.host.split(':')[0]
            master_key = number.getPrime(47, os.urandom)
            public_key = number.getPrime(48, os.urandom)
            certcenter_key = generate_entity_key(master_key, certcenter_id, public_key)
            
            cur.execute("INSERT INTO certcenter (certcenter_id, certcenter_ip_address, master_key, public_key, certcenter_key) VALUES (?, ?, ?, ?, ?)",
                (certcenter_id, certcenter_ip_address, master_key, public_key, certcenter_key))
            response_body = "Initialized"
            response_code = 200
        else:
            response_body = "Already initialized"
            response_code = 500
        con.commit()
        con.close()
        return response_body, response_code
    except Exception as e:
        print(f"Error! Exception: {e}")
        return f"Unsuccessful", 500

@app.route("/api/register/institute", methods=["POST"])
def register_institute():
    try:
        data = request.get_json()
        institute_name = data["institute_name"]
        institute_id = int.from_bytes(os.urandom(4),'big')
        institute_ip_address = request.remote_addr

        con = sqlite3.connect('db/cert-center.db')
        cur = con.cursor()
        master_key = cur.execute('SELECT * FROM certcenter').fetchall()[0][2]
        public_key = cur.execute('SELECT * FROM certcenter').fetchall()[0][3]
        institute_key = generate_entity_key(master_key, institute_id, public_key)
        
        cur.execute("REPLACE INTO institutes (institute_id, institute_name, institute_ip_address, institute_key) VALUES (?, ?, ?, ?)",
            (institute_id, institute_name, institute_ip_address, institute_key))
        certcenter_id = cur.execute('SELECT * FROM certcenter').fetchall()[0][0]
        response_data = {"certcenter_id": certcenter_id, "institute_id": institute_id, "institute_ip_address": institute_ip_address, "institute_key": institute_key, "public_key": public_key}
        response_code = 200

        con.commit()
        con.close()
        return response_data, response_code
    except Exception as e:
        print(f"Error! Exception: {e}")
        return f"Unsuccessful", 500

@app.route("/api/register/user/scan", methods=["GET"])
def register_user_scan():
    try:
        rdr = RFID_timeout()
        util = rdr.util()
        util.debug = True

        timeout = 10
        print("Please place the card into the reader")
        rdr.wait_for_tag(timeout = timeout)
        (error, data) = rdr.request()
        if not error:
            print("Card detected")
            (error, uid) = rdr.anticoll()
            if not error:
                (key_error, back_data) = rdr.read(1)
                if not key_error:
                    default_key = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
                    access_bits = (0x7F, 0x07, 0x88)
                    util.set_tag(uid)
                    util.auth(rdr.auth_b, default_key)
                    print("Card read UID: "+str(uid[0])+","+str(uid[1])+","+str(uid[2])+","+str(uid[3]))

                    con = sqlite3.connect("db/cert-center.db")
                    cur = con.cursor()
                    certcenter_id = cur.execute("SELECT certcenter_id FROM certcenter").fetchall()[0][0]
                    public_key = cur.execute("SELECT public_key FROM certcenter").fetchall()[0][0]
                    certcenter_key = cur.execute("SELECT certcenter_key FROM certcenter").fetchall()[0][0]
                    con.commit()
                    con.close()

                    keyij, keyij_error = generate_keyij(certcenter_key, certcenter_id, public_key)
                    if not keyij_error:
                        keyij_array = int_to_intarray(keyij)
                        print(f"Key ij: {keyij}")

                        for i in range(16):
                            util.write_trailer(i, (default_key[0], default_key[1], default_key[2], default_key[3], default_key[4], default_key[5]),
                                                access_bits, 0x00, (keyij_array[0], keyij_array[1], keyij_array[2], keyij_array[3], keyij_array[4], keyij_array[5]))
                        util.deauth()

                        uid_int = intarray_to_int(uid)
                        response_body = {"uid": uid_int}
                        response_code = 200
                    else:
                        response_body = "Failed to generate keyij"
                        response_code = 500
                else:
                    response_body = "Key does not match default key. Card already registered?"
                    response_code = 400
            else:
                response_body = "Anticollision error"
                response_code = 504
        else:
            response_body = "Card not scanned"
            response_code = 504
        GPIO.cleanup()
        return response_body, response_code
    except Exception as e:
        print(f"Error! Exception: {e}")
        return f"Unsuccessful", 500

@app.route("/api/register/user/data", methods=["POST"])
def register_user_data():
    try:
        data = request.get_json()
        user_name = data["user_name"]
        uid = data["uid"]

        con = sqlite3.connect("db/cert-center.db")
        cur = con.cursor()

        is_uid_unique = True
        rows = cur.execute("SELECT uid from users").fetchall()
        for row in range(len(rows)):
            if rows[row][0] == uid:
                is_uid_unique = False

        is_username_unique = True
        rows = cur.execute("SELECT user_name from users").fetchall()
        for row in range(len(rows)):
            if rows[row][0] == user_name:
                is_username_unique = False

        if is_uid_unique and is_username_unique:
            cur.execute("REPLACE INTO users (uid, user_name) VALUES (?, ?)",
                (uid, user_name))
            response_body = "User registered successfully!"
            response_code = 200

        elif not is_uid_unique:
            response_body = "UID already registered"
            response_code = 400
        elif not is_username_unique:
            response_body = "Username already registered"
            response_code = 400
        con.commit()
        con.close()
        return response_body, response_code
    except Exception as e:
        print(f"Error! Exception: {e}")
        return f"Unsuccessful", 500

@app.route("/api/booking/scan", methods=["GET"])
def booking_scan():
    try:
        rdr = RFID_timeout()
        util = rdr.util()
        util.debug = True

        timeout = 10
        print("Please place the card into the reader")
        rdr.wait_for_tag(timeout = timeout)
        (error, data) = rdr.request()
        if not error:
            print("Card detected")
            (error, uid) = rdr.anticoll()
            if not error:
                util.set_tag(uid)
                print("Card read UID: "+str(uid[0])+","+str(uid[1])+","+str(uid[2])+","+str(uid[3]))
                uid_int = intarray_to_int(uid)
                response_body = {"uid": uid_int}
                response_code = 200
            else:
                response_body = "Anticollision error"
                response_code = 504
        else:
            response_body = "Card not scanned"
            response_code = 504
        GPIO.cleanup()
        return response_body, response_code
    except Exception as e:
        print(f"Error! Exception: {e}")
        return f"Unsuccessful", 500

@app.route("/api/booking/getasset", methods=["GET"])
def get_institute_asset():
    try:
        data = request.get_json()
        institute_name = data["institute_name"]
        start_date = data["start_date"]
        end_date = data["end_date"]

        #Get institute IP address from DB
        con = sqlite3.connect("db/cert-center.db")
        cur = con.cursor()
        institute_ip_address = cur.execute("SELECT institute_ip_address FROM institutes WHERE institute_name = ?",(institute_name,)).fetchall()[0][0]
        con.commit()
        con.close()

        request_body = {
            "start_date":start_date,
            "end_date":end_date
        }

        response = requests.post(f"https://{institute_ip_address}:{INSTITUTE_PORT}/api/register/institute", verify=f"certs/{institute_name}.pem", json=request_body)
        if (response.status_code == 200):        
            assets = response.json()
            response_body = assets
            response_code = 200
        else:
            raise Exception("Request to Institute API /api/booking/getasset failed")
        return response_body, response_code
    except Exception as e:
        print(f"Error! Exception: {e}")
        return f"Unsuccessful", 500

@app.route("/api/booking/data", methods=["POST"])
def api_booking_data():
    try:
        data = request.get_json()
        uid = data["uid"]
        institute_name = data["institute_name"]
        asset_name = data["asset_name"]
        start_date = data["start_date"]
        end_date = data["end_date"]
        
        #Get institute IP address from DB
        con = sqlite3.connect("db/cert-center.db")
        cur = con.cursor()
        institute_ip_address = cur.execute("SELECT institute_ip_address FROM institutes WHERE institute_name = ?",(institute_name,)).fetchall()[0][0]
        con.commit()
        con.close()

        request_body = {
            "asset_name": asset_name,
            "start_date":start_date,
            "end_date":end_date,
            "uid": uid
        }

        response = requests.post(f"https://{institute_ip_address}:{INSTITUTE_PORT}/api/booking/data", verify=f"certs/{institute_name}.pem", json=request_body)
        if (response.status_code == 200):        
            book_id = response.json()["book_id"]
        else:
            raise Exception("Request to Institute API /api/booking/data failed")

        rdr = RFID_timeout()
        util = rdr.util()
        util.debug = True

        timeout = 10
        print("Please place the card into the reader")
        rdr.wait_for_tag(timeout = timeout)
        (error, data) = rdr.request()
        if not error:
            print("Card detected")
            (error, uid) = rdr.anticoll()
            if not error:
                (key_error, back_data) = rdr.read(1)
                if not key_error:
                    con = sqlite3.connect("db/cert-center.db")
                    cur = con.cursor()
                    certcenter_id = cur.execute("SELECT certcenter_id FROM certcenter").fetchall()[0][0]
                    public_key = cur.execute("SELECT public_key FROM certcenter").fetchall()[0][0]
                    certcenter_key = cur.execute("SELECT certcenter_key FROM certcenter").fetchall()[0][0]
                    con.commit()
                    con.close()

                    keyij, keyij_error = generate_keyij(certcenter_key, certcenter_id, public_key)
                    if not keyij_error:
                        keyij_array = int_to_intarray(keyij)
                        print(f"Key ij: {keyij}")

                        util.set_tag(uid)
                        util.auth(rdr.auth_b, keyij_array)
                        print("Card read UID: "+str(uid[0])+","+str(uid[1])+","+str(uid[2])+","+str(uid[3]))

                        block = 6
                        booking_data = util.rfid.read(block)
                        while (booking_data != [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]) and (block <= 66):
                            block += 4
                            if (block <= 63):
                                booking_data = util.read_out(block)
                        
                        if (block < 66):
                            rdr.write((block-2), str_to_intarray(start_date).append(str_to_intarray(end_date)))
                            rdr.write((block-1), str_to_intarray(asset_name))
                            rdr.write(block, str_to_intarray(book_id))

                            response_body = "Data written successfully"
                            response_code = 200
                        else:
                            response_body = "Card is full"
                            response_code = 400
                        util.deauth()

                        response_body = {"book_id": book_id, "asset_name": asset_name, "start_date": start_date, "end_date": end_date}
                        response_code = 200
                    else:
                        response_body = "Failed to generate keyij"
                        response_code = 500
                else:
                    response_body = "Key does not match default key. Card already registered?"
                    response_code = 400
            else:
                response_body = "Anticollision error"
                response_code = 504
        else:
            response_body = "Card not scanned"
            response_code = 504
        GPIO.cleanup()
        
        return response_body, response_code
    except Exception as e:
        print(f"Error! Exception: {e}")
        return f"Unsuccessful", 500

def get_institute_list():
    try:
        con = sqlite3.connect("db/cert-center.db")
        cur = con.cursor()
        rows = cur.execute("SELECT institute_name FROM institutes").fetchall()
        rows = [row[0] for row in rows]

        con.commit()
        con.close()
        return rows
    except Exception as e:
        print(f"Error! Exception: {e}")
        return f"Unsuccessful", 500

def generate_entity_key(a, id, c):
    return pow(a, id, c)

def generate_keyij(key, id, c):
    keyij = pow(key, id, c)
    len_keyij = round(len(hex(keyij)[2:])/2)

    if (len_keyij == 6):
        return keyij, False
    else:
        return 0, True

# intarray merupakan integer yang diubah jadi bytes secara big endian, kemudian masing2 byte dijadikan integer
def int_to_intarray(my_int):
    return [int(key_byte) for key_byte in int.to_bytes(my_int,6,'big')]

def intarray_to_int(intarray):
    return int.from_bytes(b''.join([int.to_bytes(x,1,'big') for x in intarray]),'big')

# intarray merupakan string yang diubah jadi bytes, kemudian masing2 byte dijadikan integer
def str_to_intarray(my_str):
    return [int(byte) for byte in bytes(my_str, "utf-8")]

def intarray_to_str(intarray):
    return b''.join([int.to_bytes(x,1,'big') for x in intarray]).decode("utf-8")

if __name__ == "__main__":
    class RFID_timeout(RFID):
        def __init__(self, *args, **kwargs):
            super(RFID_timeout, self).__init__(*args, **kwargs)
        def wait_for_tag(self, timeout=0):
            # enable IRQ on detect
            start_time = time.time()
            self.init()
            self.irq.clear()
            self.dev_write(0x04, 0x00)
            self.dev_write(0x02, 0xA0)
            # wait for it
            waiting = True
            while waiting and (timeout == 0 or ((time.time() - start_time) < timeout)):
                self.init()
                #self.irq.clear()
                self.dev_write(0x04, 0x00)
                self.dev_write(0x02, 0xA0)
                self.dev_write(0x09, 0x26)
                self.dev_write(0x01, 0x0C)
                self.dev_write(0x0D, 0x87)
                waiting = not self.irq.wait(0.1)
            self.irq.clear()
            self.init()

    app.run(host='0.0.0.0', port=CERTCENTER_PORT, ssl_context=('secrets/cert.pem','secrets/key.pem'), debug=True)

from flask import Flask, render_template, request
import requests
import sqlite3
import os
import json
import time
import signal
from pirc522 import RFID
import RPi.GPIO as GPIO

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

@app.route("/api/initialize", methods=["POST"])
def initialize_cert_center():
    try:
        con = sqlite3.connect('db/cert-center.db')
        cur = con.cursor()
        cur.execute('SELECT * FROM certcenter')
        row = cur.fetchall()
        if not row:
            certcenter_name = "certcenter"
            certcenter_ip_address = request.host.split(':')[0]
            key_b = os.urandom(6).hex()
            cur.execute("INSERT INTO certcenter (certcenter_name, certcenter_ip_address, key_b) VALUES (?, ?, ?)",
                (certcenter_name, certcenter_ip_address, key_b))
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
        institute_ip_address = request.remote_addr
        key_a = os.urandom(6).hex()

        con = sqlite3.connect('db/cert-center.db')
        cur = con.cursor()
        cur.execute("REPLACE INTO institutes (institute_id, institute_name, institute_ip_address, key_a) VALUES ((SELECT institute_id FROM institutes WHERE institute_name = ?), ?, ?, ?)",
            (institute_name, institute_name, institute_ip_address, key_a))
        institute_id = cur.execute("SELECT institute_id FROM institutes WHERE institute_name=? and institute_ip_address=?", (institute_name, institute_ip_address)).fetchall()[0][0]
        con.commit()
        con.close()

        response_data = {"institute_id": institute_id, "institute_ip_address": institute_ip_address, "key_a": key_a}

        response_code = 200
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
                    uid_str = ""
                    for i in range(4):
                        if (uid[i] < 16):
                            temp_x = hex(uid[i])
                            temp_x = temp_x[:2] + "0" + temp_x[-1]
                        else:
                            temp_x = hex(uid[i])
                        uid_str += temp_x[2:] + ":"
                    uid_str = uid_str[:-1]

                    con = sqlite3.connect("db/cert-center.db")
                    cur = con.cursor()
                    db_key_b = cur.execute("SELECT key_b FROM certcenter").fetchall()[0][0]
                    hexarray = [ db_key_b[i:i+2] for i in range(0, int(len(db_key_b)),2) ]
                    key_b = [ int(hexarray[i], 16) for i in range(6) ]
                    print(f"Key B: {key_b}")

                    for i in range(16):
                        util.write_trailer(i, (default_key[0], default_key[1], default_key[2], default_key[3], default_key[4], default_key[5]),
                                            access_bits, 0x00, (key_b[0], key_b[1], key_b[2], key_b[3], key_b[4], key_b[5]))
                    util.deauth()
                    response_body = {"uid": uid_str}
                    response_code = 200
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
            cur.execute("REPLACE INTO users (user_id, user_name, uid) VALUES ((SELECT user_id FROM users WHERE user_name = ?), ?, ?)",
                (user_name, user_name, uid))
            con.commit()
            con.close()
            response_body = "User registered successfully!"
            response_code = 200

        elif not is_uid_unique:
            response_body = "UUID already registered"
            response_code = 400
        elif not is_username_unique:
            response_body = "Username already registered"
            response_code = 400
        return response_body, response_code
    except Exception as e:
        print(f"Error! Exception: {e}")
        return f"Unsuccessful", 500

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

from flask import Flask
import requests

app = Flask(__name__)

ADVERSARY_HOST="raspberrypi3"
ADVERSARY_PORT="5000"

@app.route("/")
def hello_world():
    return("Connection Successful!")

@app.route("/request")
def request():
    r = requests.get(f'http://{ADVERSARY_HOST}:{ADVERSARY_PORT}/')
    print("Status code:",r.status_code)
    print("Body:",r.content)
    return("Request Successful!")
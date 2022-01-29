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
    r = requests.get(f'https://{ADVERSARY_HOST}:{ADVERSARY_PORT}/')
    print("Status code:",r.status_code)
    print("Body:",r.content)
    return("Request Successful!")

if __name__ == "__main__":
    app.run(host='0.0.0.0',ssl_context=('cert.pem','key.pem'),debug=True)
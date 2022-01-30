from flask import Flask
import requests
import os

app = Flask(__name__)

server_directory = os.path.dirname(os.path.realpath(__file__))

@app.route("/home")
def hello_world():
    with open(f"{server_directory}/static/home.html","r") as html_file:
        html = html_file.read()
    return(html)

if __name__ == "__main__":
    app.run(host='0.0.0.0',ssl_context=('cert.pem','key.pem'),debug=True)
from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello_world():
    return("Hi ESP8266! I'm up.")

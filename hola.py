from flask import Flask

app = Flask(__name__)

@app.route("/hello")
def hola():
    return "<h1>Hola mundo</h1>"
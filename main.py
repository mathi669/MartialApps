from flask import Flask
from app import routes

app = Flask(__name__)


app.register_blueprint(routes.routes, url_prefix='/')

if __name__ == "__main__":
    app.run() 
    


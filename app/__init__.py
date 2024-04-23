from flask import Flask
from .routes import routes

app = Flask(__name__)

def init_app(config):
    app.config.from_object(config)

    app.register_blueprint(routes.main, url_prefix='/')

    return app


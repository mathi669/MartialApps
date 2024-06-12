from flask import Flask
from config import config
from app.routes.routes import routes
from flask_cors import CORS
from decouple import config as env_config
from flask_mail import Mail

def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "*"}})

    # Configuración de Flask-Mail
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USERNAME'] = env_config("MAIL_USERNAME")
    app.config['MAIL_PASSWORD'] = env_config("MAIL_PASSWORD")
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True

    mail = Mail(app)
    app.config.from_object(config['development'])
    app.register_blueprint(routes, url_prefix='/')
    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=env_config('PORT'), threaded=True)
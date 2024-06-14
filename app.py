from flask import Flask
from config import config
from app.routes import routes
from app.routes.routes import routes  # Importa el blueprint routes correctamente
from flask_cors import CORS
from decouple import config as env_config
from flask_mail import Mail
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Configuración de Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = env_config("MAIL_USERNAME")  # Add your email here
app.config['MAIL_PASSWORD'] = env_config("MAIL_PASSWORD")  # Add your app password here
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)

if __name__ == "__main__":
    app.config.from_object(config['development'])
    app.register_blueprint(routes, url_prefix='/')
    port = int(os.getenv('PORT', 8080))  # Use PORT provided by Cloud Run, default to 8080
    app.run(debug=True, host='0.0.0.0', port=port, threaded=True)

from flask import Flask
from config import config
from app.routes import routes
from app.routes.routes import routes  # Importa el blueprint routes correctamente
from flask_cors import CORS
from decouple import config as env_config


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}) 
if __name__ == "__main__":
    
    app.config.from_object(config['development'])
    app.register_blueprint(routes, url_prefix='/')
    app.run(debug=True, host='0.0.0.0', port=env_config('PORT'), threaded=True)

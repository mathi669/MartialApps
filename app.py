from flask import Flask
from config import config
from app.routes import routes
from app.routes.routes import routes  # Importa el blueprint routes correctamente
from flask_cors import CORS


app = Flask(__name__)
if __name__ == "__main__":
    
    CORS(app, resources={r"/*": {"origins": "*"}}) 
    app.config.from_object(config['development'])
    app.register_blueprint(routes, url_prefix='/')
    app.run(debug=True, host='0.0.0.0', port=8000, threaded=True)

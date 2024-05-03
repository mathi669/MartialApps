from flask import Flask
from config import config
from app.routes import routes



# app = Flask(__name__, static_url_path='/app/static', static_folder='/app/static', template_folder='templates')
app = Flask(__name__, static_url_path='/app/static')

def page_not_found(error):
    return "<h1>Not found page</h1>", 404

if __name__ == "__main__":
    
    app.config.from_object(config['development'])
    
    app.register_blueprint(routes.routes, url_prefix='/')
    app.register_error_handler(404, page_not_found)
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True) 
    


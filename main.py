from flask import Flask
from decouple import config
from app import routes
from app.database.mysql_conection import get_conection



app = Flask(__name__)
get_conection().__init__(app)

app.register_blueprint(routes.routes, url_prefix='/')

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True) 
    


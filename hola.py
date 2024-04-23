from flask import Flask, jsonify
app = Flask(__name__)

@app.route("/hello")
def hola():
    return "<h1>Hola mundo</h1>"

user = {
    "id": 1,
    "name": "John Doe",
    "email": "john.doe@example.com"
}

@app.route('/user', methods=['GET'])
def get_user():
    return jsonify(user)

if __name__ == 'main':
    app.run(debug=True)
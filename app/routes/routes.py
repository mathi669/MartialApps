from flask import Blueprint, render_template, abort, request, redirect, url_for, flash, jsonify
from jinja2 import TemplateNotFound
from ..models.user import ModelUser
from ..models.entities.Usersmodel import User
from ..database.mysql_conection import get_conection

routes = Blueprint("routes", __name__, template_folder='../views')

@routes.route('/')
@routes.route('/home')
def hola():
    try:
        return render_template('home.html')
    except TemplateNotFound:
        abort(404)

@routes.route('/adios')
def adios():
    try:
        return render_template('adios.html')
    except TemplateNotFound:
        abort(404)
        
@routes.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'POST':
            # print(request.form['username'])
            # print(request.form['password'])
            user = User(0,request.form['username'],request.form['password'])
            logged_user=ModelUser.login(get_conection(),user)
            if logged_user != None:
                if logged_user.password:
                    return redirect(url_for('home'))
                else:
                    flash("Invalid pass")
                    return render_template('login.html')
            else:
                flash("user not found")
                return render_template('login.html')
        else:
            return render_template('login.html')
    except TemplateNotFound:
        abort(404)
        

@routes.route('/test_db_connection', methods=['GET'])
def test_db_conection():
    try:
        get_conection().engine.execute('SELECT 1')
        return jsonify({'message': 'Database connection successful'}), 200
    except Exception as e:
        return jsonify({'message': f'Database connection failed: {str(e)}'}), 500
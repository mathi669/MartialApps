from flask import Blueprint, render_template, abort, request, redirect, url_for, flash, jsonify
from jinja2 import TemplateNotFound
from ..models.user import ModelUser
from ..models.entities.Usersmodel import User
from ..database.mysql_conection import get_conection

routes = Blueprint("routes", __name__, template_folder='../templates')



@routes.route('/')
@routes.route('/home')
def hola():
    try:
        return render_template('home.html')
    except TemplateNotFound:
        abort(404)

@routes.route('/registro')
def registro():
    try:
        return render_template('newaccount.html')
    except TemplateNotFound:
        abort(404)
        
@routes.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'POST':
            # conn = get_conection()
            # print(conn)
            user = User(0,request.form['dc_nombre'],request.form['dc_contrasena'])
            logged_user=ModelUser.login(user)
            if logged_user != None:
                if logged_user.password:
                    return redirect(url_for('home.html'))
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
    except Exception as ex:
        #### mostrar mensaje de error en sitio web ##
        print(ex)
        
@routes.route('/get_users', methods=['GET'])
def get_users():
    try:
        users=ModelUser.get_users()
        print(f"users: {users}")
        return jsonify(users)
    except Exception as ex:
        return jsonify({'message': str(ex)}), 500

        
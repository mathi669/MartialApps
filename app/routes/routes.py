from flask import Blueprint, render_template, abort, request, redirect, url_for, flash, jsonify
import uuid
from datetime import datetime, date
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

@routes.route('/registro', methods=['POST'])
def registro():
    try:
        username = request.json['dc_nombre']
        password = request.json['dc_contrasena']
        email = request.json['dc_correo_electronico']
        phone = request.json['dc_telefono']
        id = request.json['id']
        nivel_artes_marciales = int(request.json['tb_nivel_artes_marciales_id'])
        date = datetime.strptime(request.json['df_fecha_solicitud'], '%d/%m/%Y').strftime('%Y-%m-%d')
        user_id = int(request.json['tb_tipo_usuario_id'])
        status_id = int(request.json['tb_usuario_estado_id'])
        level_id = int(request.json['tb_nivel_id'])
        emergency_contact = int(request.json['tb_contacto_emergencia_id'])
        user=User(id, username, password, email, phone, nivel_artes_marciales, date, user_id, status_id, level_id, emergency_contact)
        
        affected_rows = ModelUser.signup(user)
        
        if affected_rows == 1:
            return jsonify({})
        else:
            return jsonify({'message': "Error al registrar"}), 500
        # return render_template('newaccount.html')
    except TemplateNotFound:
        abort(404)
    except Exception as ex:
        return jsonify({'message': str(ex)}), 500
        
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

        
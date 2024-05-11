from flask import Blueprint, request, flash, jsonify
from ..models.user import ModelUser
from ..models.entities.Usersmodel import User
from datetime import datetime
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from decouple import config
from app.services.AuthService import AuthService
from app.utils.Security import Security
from ..models.schedule import ScheduleModel




routes = Blueprint("routes", __name__)

jwtoken=config('JWT_SECRET_KEY') 
jwt = JWTManager()

@routes.route('/registro', methods=['GET', 'POST'])
def registro():
    try:
        if request.method == 'POST':
            username = request.json['dc_nombre']
            password = request.json['dc_contrasena']
            email = request.json['dc_correo_electronico']
            phone = request.json['dc_telefono']
            nivel_artes_marciales = int(request.json['tb_nivel_artes_marciales_id'])
            date = datetime.strptime(request.json['df_fecha_solicitud'], '%d/%m/%Y').strftime('%Y-%m-%d')
            user_id = int(request.json['tb_tipo_usuario_id'])
            status_id = int(request.json['tb_usuario_estado_id'])
            level_id = int(request.json['tb_nivel_id'])
            emergency_contact = int(request.json['tb_contacto_emergencia_id'])
            user = User(username, password, email, phone, nivel_artes_marciales, date, user_id, status_id, level_id, emergency_contact)
            affected_rows = ModelUser.signup(user)
            if affected_rows == 1:
                return jsonify({'message':'Usuario registrado con exito'}), 200
            else:
                return jsonify({'error':'Error en el registro de usuario'}) , 400
        else:
            return jsonify({'error':'Método no permitido'}), 405
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    

@routes.route('/login', methods=['POST'])
def login():
    try:
        if request.method == 'POST':
            email = request.json.get('dc_correo_electronico')
            password = request.json.get('dc_contrasena')
            user = User(email, password)
            authenticated_user = AuthService.login_user(user)
            
            if(authenticated_user != None):
                encoded_token = Security.generate_token(authenticated_user)
                return jsonify({'success':True, 'token': encoded_token})
            else:
                return jsonify({'success': False})
            
            # logged_user = ModelUser.login(user)
            
            # if logged_user is not None:
            #     return jsonify({'message': 'acceso correcto'}), 200
            # else:
            #     return jsonify({'error':'Usuario o contraseña incorrectos'}), 401
        else:
            return jsonify({'error':'Método no permitido'}), 405
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@routes.route('/get_users', methods=['GET'])
@jwt_required()
def get_users():
    try:
        if request.method == 'GET':
            users = ModelUser.get_users()
            return jsonify(users), 200
        else:
            return jsonify({'error':'Método no permitido'}), 405
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@routes.route('/get_user/<int:user_id>', methods=['GET'])
def get_user_by_id(user_id):
    try:
        if request.method == 'GET':
            user = ModelUser.get_user_by_id(user_id)
            if user:
                return jsonify(user), 200
            else:
                return jsonify({'error': 'Usuario no encontrado'}), 404
        else:
            return jsonify({'error': 'Método no permitido'}), 405
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@routes.route('/delete_user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        if request.method == 'DELETE':
            # Eliminar usuario por ID
            affected_rows = ModelUser.delete_user(user_id)
            if affected_rows == 1:
                return jsonify({'message': 'Usuario eliminado exitosamente'}), 200
            else:
                return jsonify({'error': 'Usuario no encontrado'}), 404
        else:
            return jsonify({'error': 'Método no permitido'}), 405
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@routes.route('/update_user/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    try:
        if request.method == 'PUT':
            # Obtener datos del cuerpo de la solicitud
            new_user_data = request.json
            
            # Actualizar usuario por ID
            affected_rows = ModelUser.update_user(user_id, new_user_data)
            if affected_rows == 1:
                return jsonify({'message': 'Usuario actualizado exitosamente'}), 200
            else:
                return jsonify({'error': 'Usuario no encontrado'}), 404
        else:
            return jsonify({'error': 'Método no permitido'}), 405
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

### schedule router
@routes.route('/get_schedule', methods=['GET'])
def get_schedule():
    try:
        if request.method == 'GET':
            schedule = ScheduleModel.get_schedule()
            return jsonify(schedule), 200
        else:
            return jsonify({'error':'Método no permitido'}), 405
    except Exception as e:
        return jsonify({'error': str(e)}), 500
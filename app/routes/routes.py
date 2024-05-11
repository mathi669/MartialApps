from app.database.mysql_conection import get_conection
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


@routes.route('/register', methods=['POST'])
def register_user():
    try:
        # Obtener datos del cuerpo de la solicitud
        data = request.get_json()
        
        # Extraer datos del cuerpo de la solicitud
        correo = data.get('dc_correo_electronico')
        contrasena = data.get('contrasena')
        nombre = data.get('nombre')
        apellido = data.get('apellido')
        telefono = data.get('telefono')
        nivel_artes_marciales_id = data.get('nivel_artes_marciales_id')
        tipo_usuario_id = data.get('tipo_usuario_id')
        usuario_estado_id = data.get('usuario_estado_id')
        nivel_id = data.get('nivel_id')
        contacto_emergencia_id = data.get('contacto_emergencia_id')
        es_gimnasio = data.get('es_gimnasio')

        # Verificar si todos los campos requeridos están presentes y no son nulos
        required_fields = {'dc_correo_electronico', 'contrasena', 'nombre', 'apellido'}
        missing_fields = required_fields - set(data.keys())
        if missing_fields:
            return jsonify({'error': f'Faltan los siguientes campos: {", ".join(missing_fields)}'}), 400

        # Llamar al stored procedure para registrar el usuario
        conn = get_conection()
        with conn.cursor() as cursor:
            cursor.callproc('sp_InsertarUsuario', (nombre + apellido, correo, contrasena, telefono, nivel_artes_marciales_id, tipo_usuario_id, usuario_estado_id, nivel_id, contacto_emergencia_id, es_gimnasio))
            conn.commit()
        conn.close()

        # Devolver respuesta exitosa
        return jsonify({'mensaje': 'Usuario registrado correctamente'}), 200

    except Exception as e:
        # Devolver error en caso de excepción
        return jsonify({'error': str(e)}), 500


@routes.route('/login', methods=['POST'])
def login():
    try:
        if request.method == 'POST':
            email = request.json.get('dc_correo_electronico')
            print("aqui esta el mail: ", email)
            password = request.json.get('dc_contrasena')
            user = User(email, password)
            authenticated_user = AuthService.login_user(user)
            
            if authenticated_user:
                encoded_token = Security.generate_token(authenticated_user)
                return jsonify({'success': True, 'token': encoded_token})
            else:
                print("Error de autenticación: Usuario o contraseña incorrectos.")
                return jsonify({'success': False, 'error': 'Usuario o contraseña incorrectos'})
        else:
            return jsonify({'error':'Método no permitido'}), 405
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@routes.route('/get_users', methods=['GET'])
# @jwt_required()
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
    

    # seccion de endpoints de gimnasio 
@routes.route('/gimnasios', methods=['GET'])
def get_all_gimnasios():
    try:
        conn = get_conection()  # Obtener conexión a la base de datos
        with conn.cursor() as cursor:
            cursor.callproc('sp_GetAllGimnasios')
            result = cursor.fetchall()  # Obtener todos los registros devueltos por el procedimiento almacenado
        conn.close()  # Cerrar la conexión

        # Formatear los resultados como una lista de diccionarios
        gimnasios = []
        for row in result:
            gimnasio = {
                'id': row[0],
                'nombre': row[1],
                'correo_electronico': row[2],
                'telefono': row[3],
                'ubicacion': row[4],
                'horario': row[5],
                'fecha_ingreso': row[6].strftime('%Y-%m-%d'),  # Convertir fecha a formato ISO
                'descripcion': row[7],
                'imagen_url': row[8],
                'estado_id': row[9]
            }
            gimnasios.append(gimnasio)

        return jsonify({'gimnasios': gimnasios}), 200  # Devolver la lista de gimnasios como JSON
    except Exception as e:
        return jsonify({'error': str(e)}), 500  # Devolver un error 500 en caso de excepción
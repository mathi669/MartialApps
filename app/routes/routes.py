import requests
from threading import Thread
from app.database.mysql_conection import get_conection
from flask import Blueprint, request, jsonify, session, current_app
from app.models.user import ModelUser
from datetime import datetime, timedelta, date, time
from decouple import config
from app.services.AuthService import AuthService
from app.utils.Security import Security
from app.models.schedule import ScheduleModel
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity,
)
from flask_mail import Mail, Message
import mysql.connector
from functools import wraps
from apscheduler.schedulers.background import BackgroundScheduler


routes = Blueprint("routes", __name__)
mail = Mail()

jwtoken = config("JWT_SECRET_KEY")

jwt = JWTManager()

# Configuración de la API de ImgBB
IMG_API_KEY = config("IMG_BB_KEY")

scheduler = BackgroundScheduler()


# Función para subir imagen a ImgBB
def upload_image_to_imgbb(base64_image):
    url = "https://api.imgbb.com/1/upload"
    payload = {"key": IMG_API_KEY, "image": base64_image}
    response = requests.post(url, data=payload)
    print(response.text)
    return response

def convert_timedelta_to_string(data):
    converted_data = []
    for item in data:
        converted_item = []
        for value in item:
            if isinstance(value, timedelta):
                converted_item.append(str(value))
            elif isinstance(value, datetime):
                converted_item.append(value.strftime("%Y-%m-%d %H:%M:%S"))
            elif isinstance(value, date):
                converted_item.append(value.strftime("%Y-%m-%d"))
            elif isinstance(value, time):
                converted_item.append(value.strftime("%H:%M:%S"))
            else:
                converted_item.append(value)
        converted_data.append(converted_item)
    return converted_data


"""access and register routes"""

import requests

def upload_image_to_imgbb(base64_image):
    url = "https://api.imgbb.com/1/upload"
    payload = {"key": IMG_API_KEY, "image": base64_image}
    response = requests.post(url, data=payload)
    return response

@routes.route("/registerGym", methods=["POST"])
def register_gym():
    try:
        # Obtener datos del cuerpo de la solicitud
        data = request.get_json()

        # Verificar si todos los campos requeridos están presentes y no son nulos
        required_fields = {
            "nombreGimnasio",
            "correo",
            "contrasena",
            "telefonoGimnasio",
            "ubicacionGimnasio",
            "descripcion",
            "imagen_base64",
            "horario",
            "redSocial",
        }
        missing_fields = required_fields - set(data.keys())
        if missing_fields:
            return (
                jsonify(
                    {
                        "error": f'Faltan los siguientes campos: {", ".join(missing_fields)}'
                    }
                ),
                400,
            )

        # Extraer datos del cuerpo de la solicitud
        nombre_gimnasio = data.get("nombreGimnasio")
        correo = data.get("correo")
        contrasena = data.get("contrasena")
        telefono = data.get("telefonoGimnasio")
        ubicacion_gimnasio = data.get("ubicacionGimnasio")
        descripcion = data.get("descripcion")
        imagen_base64 = data.get("imagen_base64")
        horario = data.get("horario") 
        red_social = data.get("redSocial")

        # Llamar al método para subir la imagen a ImgBB
        response = upload_image_to_imgbb(imagen_base64)
        if response.status_code != 200:
            return jsonify({"error": "Error al cargar la imagen"}), 500
        
        image_url = response.json()["data"]["url"]

        # Llamar al stored procedure para registrar el gimnasio
        conn = get_conection()
        with conn.cursor() as cursor:
            # Obtener el último ID de la tabla tb_gimnasio
            cursor.execute("SELECT MAX(id) FROM tb_gimnasio")
            last_id_row = cursor.fetchone()
            last_id = last_id_row[0] if last_id_row and last_id_row[0] is not None else 0
            
            # Calcular el nuevo ID sumando 1 al último ID obtenido
            new_id = last_id + 1
            
            # Insertar el nuevo registro en la tabla tb_gimnasio con el nuevo ID
            cursor.execute(
                "INSERT INTO tb_gimnasio (id, dc_nombre, dc_correo_electronico, dc_contrasena, dc_telefono, dc_ubicacion, dc_horario, df_fecha_ingreso, dc_descripcion, dc_imagen_url, dc_red_social) VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), %s, %s, %s)",
                (new_id, nombre_gimnasio, correo, contrasena, telefono, ubicacion_gimnasio, horario, descripcion, image_url, red_social),
            )
            conn.commit()

            # Llamar al stored procedure para registrar la solicitud de registro
            cursor.callproc(
                "sp_InsertarSolicitudRegistro",
                (new_id, datetime.now()),
            )
            conn.commit()

        # Devolver respuesta exitosa
        return jsonify({"mensaje": "Solicitud de registro de gimnasio enviada correctamente"}), 200

    except Exception as e:
        # Registrar el error para la depuración
        print(f"Error en register_gym: {e}")
        # Devolver error en caso de excepción
        return jsonify({"error": str(e)}), 500
    
@routes.route("/register", methods=["POST"])
def register_user():
    try:
        # Obtener datos del cuerpo de la solicitud
        data = request.get_json()

        # Extraer datos del cuerpo de la solicitud
        correo = data.get("dc_correo_electronico")
        contrasena = data.get("dc_contrasena")
        
        nombre = data.get("dc_nombre")
        apellido = data.get("dc_apellido")
        telefono = data.get("dc_telefono")
        nivel_artes_marciales_id = data.get("tb_nivel_artes_marciales_id")
        tipo_usuario_id = data.get("tb_tipo_usuario_id")
        usuario_estado_id = data.get("tb_usuario_estado_id")
        nivel_id = data.get("tb_nivel_id")
        contacto_emergencia_id = data.get("tb_contacto_emergencia_id")
        es_gimnasio = data.get("es_gimnasio")

        # Verificar si todos los campos requeridos están presentes y no son nulos
        required_fields = {
            "dc_correo_electronico",
            "dc_contrasena",
            "dc_nombre",
            "dc_apellido",
        }
        missing_fields = required_fields - set(data.keys())
        if missing_fields:
            return (
                jsonify(
                    {
                        "error": f'Faltan los siguientes campos: {", ".join(missing_fields)}'
                    }
                ),
                400,
            )

        # Llamar al stored procedure para registrar el usuario
        conn = get_conection()
        with conn.cursor() as cursor:
            cursor.callproc(
                "sp_InsertarUsuario",
                (
                    nombre + " " + apellido,
                    correo,
                    contrasena,
                    telefono,
                    nivel_artes_marciales_id,
                    tipo_usuario_id,
                    usuario_estado_id,
                    nivel_id,
                    contacto_emergencia_id,
                    es_gimnasio,
                ),
            )
            conn.commit()
        conn.close()

        # Devolver respuesta exitosa
        return jsonify({"mensaje": "Usuario registrado correctamente"}), 200

    except Exception as e:
        # Devolver error en caso de excepción
        return jsonify({"error": str(e)}), 500


@routes.route("/login", methods=["POST"])
def login():
    try:
        if request.method == "POST":
            user_type = request.json.get("user_type")
            email = request.json.get("dc_correo_electronico")
            print("Aquí está el correo: ", email)
            password = request.json.get("dc_contrasena")
            user_data = {"dc_correo_electronico": email, "dc_contrasena": password}
            print(f"Autenticando tipo de usuario: {user_type}")

            auth_response = AuthService.login_user(user_type, user_data)
            print("Respuesta de autenticación:", auth_response)

            if auth_response["success"]:
                print("Autenticación exitosa.")
                encoded_token = Security.generate_token(auth_response["user"])
                response = {
                    "success": True,
                    "token": encoded_token,
                    "user": auth_response["user"],
                    "message": auth_response["message"],
                }
                return jsonify(response)
            else:
                print("Error de autenticación: Usuario o contraseña incorrectos.")
                return jsonify(
                    {
                        "success": False,
                        "message": "Usuario o contraseña incorrectos",
                    }
                )
        else:
            return jsonify({"message": "Método no permitido"}), 405
    except Exception as e:
        print("Error en el endpoint /login:", e)
        return jsonify({"error": str(e)}), 500

@routes.route("/logout", methods=["POST"])
def logout():
    try:
        # Elimina la información de la sesión
        session.clear()
        return jsonify({"success": True, "message": "Sesión cerrada exitosamente"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


"""Gym routes"""


@routes.route("/createGym", methods=["POST"])
def create_gym():
    try:
        data = request.get_json()

        if not all(
            [
                data.get("dc_nombre"),
                data.get("dc_correo_electronico"),
                data.get("dc_telefono"),
                data.get("dc_ubicacion"),
                data.get("dc_horario"),
                data.get("tb_gimnasio_estado_id"),
                data.get("image"),
            ]
        ):
            return (
                jsonify({"error": "All fields except dc_descripcion are required"}),
                400,
            )

        # Subir la imagen a ImgBB
        response = upload_image_to_imgbb(data["image"])
        if not response.ok:
            return jsonify({"error": "Failed to upload image"}), 500
        image_url = response.json()["data"]["url"]

        # Conectar a la base de datos y llamar al procedimiento almacenado
        conn = get_conection()
        with conn.cursor() as cursor:
            cursor.callproc(
                "sp_InsertarGimnasio",
                (
                    data.get("dc_nombre"),
                    data.get("dc_correo_electronico"),
                    data.get("dc_telefono"),
                    data.get("dc_ubicacion"),
                    data.get("dc_horario"),
                    datetime.now(),  # df_fecha_ingreso
                    data.get("dc_descripcion"),
                    image_url,
                    int(data.get("tb_gimnasio_estado_id")),
                ),
            )
            conn.commit()
        conn.close()

        return jsonify({"mensaje": "Gimnasio creado correctamente"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@routes.route("/updateGym/<int:gym_id>", methods=["PUT"])
def update_gym(gym_id):
    try:
        data = request.json
        image = request.files.get("image")
        image_url = data.get("dc_imagen_url")
        
        conn = get_conection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT dc_nombre, dc_correo_electronico, dc_contrasena, dc_telefono, dc_ubicacion, dc_horario, dc_descripcion, dc_imagen_url, tb_gimnasio_estado_id, dc_red_social FROM tb_gimnasio WHERE id = %s", (gym_id,))
            current_data = cursor.fetchone()

        nombre = data.get("dc_nombre", current_data[0])
        correo = data.get("dc_correo_electronico", current_data[1])
        contrasena = data.get("dc_contrasena", current_data[2])
        telefono = data.get("dc_telefono", current_data[3])
        ubicacion = data.get("dc_ubicacion", current_data[4])
        horario = data.get("dc_horario", current_data[5])
        descripcion = data.get("dc_descripcion", current_data[6])
        image_url = image_url if image_url else current_data[7]
        estado_id = int(data.get("tb_gimnasio_estado_id", current_data[8]))
        redSocial = data.get("dc_red_social", current_data[9])

        if not image and not image_url:
            conn = get_conection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT dc_imagen_url FROM tb_gimnasio WHERE id = %s", (gym_id,))
                existing_image_url = cursor.fetchone()
                if existing_image_url:
                    image_url = existing_image_url[0]
            conn.close()

        if image:
            response = upload_image_to_imgbb(image)
            if not response.ok:
                return jsonify({"error": "Failed to upload image"}), 500
            image_url = response.json()["data"]["url"]

        conn = get_conection()
        with conn.cursor() as cursor:
            cursor.callproc(
                "sp_ActualizarGimnasio",
                (
                    gym_id,
                    nombre,
                    correo,
                    contrasena,
                    telefono,
                    ubicacion,
                    horario,
                    datetime.now(),
                    descripcion,
                    image_url,
                    estado_id,
                    redSocial
                ),
            )
            conn.commit()

            # Obtener los correos de los usuarios inscritos
            cursor.execute("""
                SELECT u.dc_correo_electronico, u.dc_telefono
                FROM tb_solicitud_reserva r
                JOIN tb_usuario u ON r.tb_usuario_id = u.id
                WHERE r.tb_gimnasio_id = %s
            """, (gym_id,))
            usuarios = cursor.fetchall()

        conn.close()

        for usuario in usuarios:
            enviar_correo(usuario[0], "Actualización del Gimnasio", "Los detalles del gimnasio han sido actualizados.")

        return jsonify({"mensaje": "Gimnasio actualizado correctamente y notificaciones enviadas"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@routes.route("/deleteGym/<int:gym_id>", methods=["DELETE"])
def delete_gym(gym_id):
    try:
        # Conectar a la base de datos y llamar al procedimiento almacenado
        conn = get_conection()
        with conn.cursor() as cursor:
            cursor.callproc("sp_EliminarGimnasio", (gym_id,))
            conn.commit()
        conn.close()

        return jsonify({"mensaje": "Gimnasio eliminado correctamente"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@routes.route("/gym/<int:gym_id>", methods=["GET"])
def get_gym(gym_id):
    try:
        # Conectar a la base de datos y llamar al procedimiento almacenado
        conn = get_conection()
        print("Conectado?, ", conn)
        with conn.cursor() as cursor:
            cursor.callproc("sp_ObtenerGimnasio", (gym_id,))
            result = cursor.fetchone()
        conn.close()

        if result:
            return jsonify(result), 200
        else:
            return jsonify({"error": "Gimnasio no encontrado"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@routes.route("/gyms", methods=["GET"])
def get_all_gyms():
    query = request.args.get("query", '')
    try:
        conn = get_conection()  # Obtener conexión a la base de datos
        with conn.cursor() as cursor:
            cursor.callproc("sp_GetAllGimnasios", (query,))
            result = cursor.fetchall()  # Obtener todos los registros devueltos por el procedimiento almacenado
        conn.close()  # Cerrar la conexión
        
        # Formatear los resultados como una lista de diccionarios
        gimnasios = []
        for row in result:
            gimnasio = {
                "id": row[0],
                "nombre": row[1],
                "correo_electronico": row[2],
                "telefono": row[3],
                "ubicacion": row[4],
                "horario": row[5],
                "fecha_ingreso": row[6].strftime(
                    "%Y-%m-%d"
                ),  # Convertir fecha a formato ISO
                "descripcion": row[7],
                "imagen_url": row[8],
                "estado_id": row[9],
            }
            gimnasios.append(gimnasio)

        return (
            jsonify({"gimnasios": gimnasios}),
            200,
        )  # Devolver la lista de gimnasios como JSON
    except Exception as e:
        return (
            jsonify({"error": str(e)}),
            500,
        )  # Devolver un error 500 en caso de excepción

def format_result(cursor, result):
    columns = [col[0] for col in cursor.description]
    formatted_result = []
    for row in result:
        row_dict = dict(zip(columns, row))
        for key, value in row_dict.items():
            if isinstance(value, datetime):
                row_dict[key] = value.strftime('%Y-%m-%d')
            elif isinstance(value, timedelta):
                total_seconds = int(value.total_seconds())
                hours, remainder = divmod(total_seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                row_dict[key] = f'{hours:02}:{minutes:02}:{seconds:02}'
        formatted_result.append(row_dict)
    return formatted_result

        
@routes.route("/filterGyms", methods=["GET"])
def get_filtered_gyms():
    
    tipo_artes_marciales = request.args.get("tipo_artes_marciales", None)
    ubicacion = request.args.get("ubicacion", None)
    horario = request.args.get("horario", None)
    
    try:
        conn = get_conection()
        with conn.cursor() as cursor:
            print(f"Llamando a sp_GetFilteredGimnasios con: {tipo_artes_marciales}, {ubicacion}, {horario}")
            cursor.callproc("sp_GetFilteredGimnasios", (tipo_artes_marciales, ubicacion, horario))
            result = cursor.fetchall()
            print(f"Resultados obtenidos: {result}")
            formatted_result = format_result(cursor, result)
        conn.close()
        
        return jsonify({"gimnasios": formatted_result}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@routes.route("/gym/<int:gym_id>/status", methods=["GET"])
def get_gym_status(gym_id):
    conn = None
    try:
        # Conectar a la base de datos y obtener el horario del gimnasio
        conn = get_conection()
        if conn is None:
            return jsonify({"error": "No se pudo conectar a la base de datos"}), 500
        with conn.cursor() as cursor:
            cursor.execute("SELECT dc_horario FROM tb_gimnasio WHERE id = %s", (gym_id,))
            result = cursor.fetchone()

        if result:
            horario = result[0]
            print("result: " + horario)
            status = check_gym_status(horario)
            return jsonify({"status": status}), 200
        else:
            return jsonify({"error": "Gimnasio no encontrado"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

def check_gym_status(horario):
    try:
        # Eliminar espacios innecesarios
        horario = horario.replace(" ", "")
        
        # Suponiendo que el formato del horario es "HH:MM-HH:MM"
        open_time_str, close_time_str = horario.split('-')
        open_time = datetime.strptime(open_time_str, '%H:%M').time()
        close_time = datetime.strptime(close_time_str, '%H:%M').time()

        # Obtener la hora actual
        now = datetime.now().time()

        # Comparar la hora actual con el horario del gimnasio
        if open_time <= now <= close_time:
            return "abierto"
        else:
            return "cerrado"
    except Exception as e:
        return str(e)  # Para facilitar la depuración, devolver el mensaje de error
    


"""User routes"""


@routes.route("/get_users", methods=["GET"])
#@jwt_required()
def get_users():
    try:
        if request.method == "GET":
            users = ModelUser.get_users()
            return jsonify(users), 200
        else:
            return jsonify({"error": "Método no permitido"}), 405
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
def gym_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_role = request.headers.get('X-User-Role')  # Asumiendo que el rol del usuario viene en los headers
        if user_role != 'gym':
            return jsonify({"error": "Acceso no autorizado"}), 403
        return f(*args, **kwargs)
    return decorated_function


@routes.route("/get_user/<int:user_id>", methods=["GET"])
#@gym_required
def get_user_by_id(user_id):
    try:
        conn = get_conection()
        with conn.cursor() as cursor:
            cursor.callproc("sp_ObtenerPerfilUsuario", (user_id,))
            result = cursor.fetchone()
        conn.close()

        if result:
            user_info = {
                "id": result[0],
                "nombre": result[1],
                "correo_electronico": result[2],
                "telefono": result[3],
                "fecha_solicitud": result[4],
                "genero": result[5],
                "contacto_emergencia": {
                    "nombre": result[6],
                    "apellido": result[7],
                    "email": result[8],
                    "telefono": result[9],
                    "relacion": result[10]
                }
            }
            return jsonify(user_info), 200
        else:
            return jsonify({"error": "Usuario no encontrado"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@routes.route("/search_users", methods=["GET"])
def search_users():
    query = request.args.get('query')
    if not query:
        return jsonify({"error": "No query provided"}), 400
    
    try:
        conn = get_conection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM tb_usuario WHERE dc_nombre LIKE %s", (f"%{query}%",))
            results = cursor.fetchall()
        conn.close()

        if results:
            return jsonify(results), 200
        else:
            return jsonify({"error": "No se encontraron usuarios"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@routes.route("/delete_user/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    try:
        if request.method == "DELETE":
            # Eliminar usuario por ID
            affected_rows = ModelUser.delete_user(user_id)
            if affected_rows == 1:
                return jsonify({"message": "Usuario eliminado exitosamente"}), 200
            else:
                return jsonify({"error": "Usuario no encontrado"}), 404
        else:
            return jsonify({"error": "Método no permitido"}), 405
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@routes.route("/update_user/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    try:
        if request.method == "PUT":
            # Obtener datos del cuerpo de la solicitud
            new_user_data = request.json

            # Actualizar usuario por ID
            affected_rows = ModelUser.update_user(user_id, new_user_data)
            if affected_rows == 1:
                return jsonify({"message": "Usuario actualizado exitosamente"}), 200
            else:
                return jsonify({"error": "Usuario no encontrado"}), 404
        else:
            return jsonify({"error": "Método no permitido"}), 405
    except Exception as e:
        return jsonify({"error": str(e)}), 500


"""schedule routes"""


@routes.route("/get_schedule", methods=["GET"])
def get_schedule():
    try:
        if request.method == "GET":
            schedule = ScheduleModel.get_schedule()
            return jsonify(schedule), 200
        else:
            return jsonify({"error": "Método no permitido"}), 405
    except Exception as e:
        return jsonify({"error": str(e)}), 500


"""levels routes"""


# Endpoint para obtener todos los niveles
@routes.route("/niveles", methods=["GET"])
def get_all_niveles():
    try:
        conn = get_conection()  # Obtener conexión a la base de datos
        with conn.cursor() as cursor:
            cursor.callproc("sp_ObtenerNiveles")
            result = (
                cursor.fetchall()
            )  # Obtener todos los registros devueltos por el procedimiento almacenado

        # Formatear los resultados como una lista de diccionarios
        niveles = []
        for row in result:
            nivel = {"id": row[0], "dc_nivel": row[1]}
            niveles.append(nivel)

        conn.close()  # Cerrar la conexión

        return (
            jsonify({"niveles": niveles}),
            200,
        )  # Devolver la lista de niveles como JSON

    except Exception as e:
        return (
            jsonify({"error": str(e)}),
            500,
        )  # Devolver un error 500 en caso de excepción


"""lessons routes"""


from datetime import datetime, date, time, timedelta

def convert_timedelta_to_string(data):
    converted_data = []
    for item in data:
        converted_item = []
        for value in item:
            if isinstance(value, timedelta):
                converted_item.append(str(value))
            elif isinstance(value, datetime):
                converted_item.append(value.strftime("%Y-%m-%d %H:%M:%S"))
            elif isinstance(value, date):
                converted_item.append(value.strftime("%Y-%m-%d"))
            elif isinstance(value, time):
                converted_item.append(value.strftime("%H:%M:%S"))
            else:
                converted_item.append(value)
        converted_data.append(converted_item)
    return converted_data

@routes.route("/classes/<int:gym_id>", methods=["GET"])
def get_classes_by_gym(gym_id):
    try:
        conn = get_conection()  # Obtener conexión a la base de datos
        with conn.cursor() as cursor:
            cursor.callproc("sp_obtenerClase", (gym_id,))
            result = cursor.fetchall()  # Obtener todos los registros devueltos por el procedimiento almacenado
        conn.close()  # Cerrar la conexión

        # Convertir timedelta a string si es necesario
        result = convert_timedelta_to_string(result)

        # Ajusta esta lista según las columnas que realmente devuelva tu procedimiento almacenado
        columns = [
            "id",
            "dc_nombre_clase",
            "dc_horario",
            "nb_cupos_disponibles",
            "df_fecha",
            "df_hora",
            "tb_clase_estado_id",
            "tb_gimnasio_id",
            "tb_arte_marcial_id",
            "tb_profesor_id",
            "dc_imagen_url",
            "dc_descripcion"
        ]
        json_result = [dict(zip(columns, row)) for row in result]

        return jsonify(json_result), 200  # Devolver la lista de clases como JSON
    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Devolver un error 500 en caso de excepción

"""Configurations routes"""


@routes.route("/change_username", methods=["PUT"])
def change_username():
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        nombre = data.get("nombre")

        if not user_id or not nombre:
            return jsonify({"error": "Missing user_id or nombre"}), 400

        conn = get_conection()
        with conn.cursor() as cursor:
            cursor.callproc("sp_CambiarNombreUsuario", (user_id, nombre))
            conn.commit()
        conn.close()

        return jsonify({"message": "Nombre de usuario cambiado correctamente"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@routes.route("/change_email", methods=["PUT"])
def change_email():
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        correo = data.get("correo")

        if not user_id or not correo:
            return jsonify({"error": "Missing user_id or correo"}), 400

        conn = get_conection()
        with conn.cursor() as cursor:
            cursor.callproc("sp_CambiarCorreo", (user_id, correo))
            conn.commit()
        conn.close()

        return jsonify({"message": "Correo electrónico cambiado correctamente"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@routes.route("/change_phone", methods=["PUT"])
def change_phone():
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        telefono = data.get("telefono")

        if not user_id or not telefono:
            return jsonify({"error": "Missing user_id or telefono"}), 400

        conn = get_conection()
        with conn.cursor() as cursor:
            cursor.callproc("sp_CambiarTelefono", (user_id, telefono))
            conn.commit()
        conn.close()

        return jsonify({"message": "Teléfono cambiado correctamente"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@routes.route("/change_password", methods=["PUT"])
def change_password():
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        contrasena = data.get("contrasena")

        if not user_id or not contrasena:
            return jsonify({"error": "Missing user_id or contrasena"}), 400

        conn = get_conection()
        with conn.cursor() as cursor:
            cursor.callproc("sp_CambiarContrasena", (user_id, contrasena))
            conn.commit()
        conn.close()

        return jsonify({"message": "Contraseña cambiada correctamente"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500



from flask import request, jsonify
from datetime import timedelta

@routes.route("/create_class", methods=["POST"])
def create_class():
    conn = None
    cursor = None
    try:
        data = request.get_json()

        # Log para imprimir los datos recibidos
        # print("Datos recibidos:")
        # print(data)

        # Validar datos requeridos
        required_fields = {
            "nombre_clase",
            "horario",
            "cupos_disponibles",
            "fecha",
            "hora",
            "imagen",  # Asegúrate de incluir 'imagen' aquí
        }
        missing_fields = required_fields - set(data.keys())
        if missing_fields:
            return (
                jsonify(
                    {
                        "error": f"Faltan los siguientes campos: {', '.join(missing_fields)}"
                    }
                ),
                400,
            )

        # Subir la imagen a ImgBB
        response = upload_image_to_imgbb(data["imagen"])
        if not response.ok:
            return jsonify({"error": "Failed to upload image"}), 500
        image_url = response.json()["data"]["url"]

        conn = get_conection()
        cursor = conn.cursor()
        cursor.callproc(
            "sp_InsertarClase",
            (
                data["nombre_clase"],
                data["horario"],
                data["cupos_disponibles"],
                data["categoria_id"],
                data["fecha"],
                data["hora"],
                data["clase_estado_id"],
                data["gimnasio_id"],
                data["arte_marcial_id"],
                data["profesor_id"],
                image_url,
                data["descripcion"],
            ),
        )
        conn.commit()
        result = cursor.fetchall()

        # Log para imprimir el resultado de la consulta
        print("Resultado de la consulta:")
        print(result)

        def convert_timedelta_to_string(data):
            converted_data = []
            for item in data:
                converted_item = {}
                for i, value in enumerate(item):
                    if isinstance(value, timedelta):
                        converted_item[cursor.description[i][0]] = str(value)
                    else:
                        converted_item[cursor.description[i][0]] = value
                converted_data.append(converted_item)
            return converted_data

        converted_result = convert_timedelta_to_string(result)

        if converted_result and converted_result[0]['tb_clase_estado_id']:
            return (
                jsonify({"message": "Clase creada exitosamente!", "class": converted_result[0]}),
                200,
            )
        else:
            return jsonify({"error": "No se pudo crear la clase o la información retornada no es válida."}), 400

    except mysql.connector.Error as err:
        return jsonify({"error": f"Error de MySQL: {str(err)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Ocurrió un error inesperado: {str(e)}"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            
@routes.route("/getAdditionalInfo", methods=["GET"])
def get_additional_info():
    conn = get_conection()

    if not session.get("logged_in"):
        return jsonify(error="User not authenticated"), 401

    user_id = session.get("user_id")

    try:
        with conn.cursor() as cursor:

            cursor.execute("SELECT id FROM tb_clase_estado LIMIT 1")
            clase_estado = cursor.fetchone()

            cursor.execute(
                "SELECT id FROM tb_gimnasio WHERE id = %s LIMIT 1", (user_id,)
            )
            gimnasio = cursor.fetchone()

            cursor.execute("SELECT id FROM tb_arte_marcial LIMIT 1")
            arte_marcial = cursor.fetchone()

            cursor.execute(
                "SELECT id FROM tb_profesor WHERE id = %s LIMIT 1", (user_id,)
            )
            profesor = cursor.fetchone()

            if not (clase_estado and gimnasio and arte_marcial and profesor):
                return jsonify(error="Required information not found"), 404

            additional_info = {
                "clase_estado_id": clase_estado["id"],
                "gimnasio_id": gimnasio["id"],
                "arte_marcial_id": arte_marcial["id"],
                "profesor_id": profesor["id"],
            }

            return jsonify(additional_info=additional_info)
    except Exception as e:
        return jsonify(error=str(e)), 500


@routes.route("/get_classes", methods=["GET"])
def get_classes():
    try:
        conn = get_conection()
        with conn.cursor() as cursor:
            cursor.callproc("sp_GetAllClases")
            result = cursor.fetchall()
        conn.close()

        result = convert_timedelta_to_string(result)

        columns = [
            "id",
            "dc_nombre_clase",
            "dc_horario",
            "nb_cupos_disponibles",
            "df_fecha",
            "df_hora",
            "tb_clase_estado_id",
            "tb_gimnasio_id",
            "tb_arte_marcial_id",
            "tb_profesor_id",
            "dc_imagen_url",
        ]
        json_result = [dict(zip(columns, row)) for row in result]

        return jsonify(json_result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@routes.route("/update_class/<int:class_id>", methods=["POST"])
def update_class(class_id):
    try:
        data = request.get_json()

        conn = get_conection()
        with conn.cursor() as cursor:
            cursor.callproc(
                "sp_ActualizarClase",
                (
                    class_id,
                    data["dc_nombre_clase"],
                    data["dc_horario"],
                    data["nb_cupos_disponibles"],
                    data["df_fecha"],
                    data["df_hora"],
                    data["tb_clase_estado_id"],
                    data["tb_gimnasio_id"],
                    data["tb_arte_marcial_id"],
                    data["tb_profesor_id"],
                    data["dc_imagen_url"],
                ),
            )
            conn.commit()
        conn.close()

        return jsonify({"mensaje": "Clase actualizada correctamente"}), 200

    except Exception as e:
        
        return jsonify({"error": str(e)}), 500


@routes.route("/delete_class/<int:class_id>", methods=["DELETE"])
def delete_class(class_id):
    try:
        conn = get_conection()
        with conn.cursor() as cursor:
            cursor.callproc("sp_EliminarClase", (class_id,))
            conn.commit()
        conn.close()

        return jsonify({"mensaje": "Clase eliminada correctamente"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@routes.route("/solicitudes_registro", methods=["GET"])
def get_solicitudes_registro():
    try:
        conn = get_conection()
        with conn.cursor() as cursor:
            cursor.execute("CALL sp_ObtenerSolicitudesRegistro")
            raw_solicitudes = cursor.fetchall()
        conn.close()

        solicitudes = []
        for solicitud in raw_solicitudes:
            solicitudes.append({
                "id_solicitud_registro": solicitud[0],
                "id_estado_solRegistro": solicitud[1],
                "id_gimnasio": solicitud[2],
                "df_fecha_solicitud": solicitud[3],
                "df_fecha_aprobacion": solicitud[4],
                "nombre_gimnasio": solicitud[5],
                "telefono_gimnasio": solicitud[6],
                "correo_gimnasio": solicitud[7],
                "direccion_gimnasio": solicitud[8],
                "foto_gimnasio": solicitud[9]
            })

        return jsonify({"solicitudes_registro": solicitudes}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@routes.route("/reservarClase", methods=["POST"])
def reservar_clase():
    try:
        data = request.get_json()
        clase_id = data.get("clase_id")
        gimnasio_id = data.get("gimnasio_id")
        usuario_id = data.get("usuario_id")
        fecha = data.get("fecha")
        hora = data.get("hora").split(' - ')[0]  # Tomar solo la hora de inicio

        required_fields = {"clase_id", "gimnasio_id", "usuario_id", "fecha", "hora"}
        missing_fields = required_fields - set(data.keys())
        if missing_fields:
            return jsonify({"ok": False, "mensaje": f'Faltan los siguientes campos: {", ".join(missing_fields)}', "solicitud": None}), 400

        conn = get_conection()
        with conn.cursor() as cursor:
            cursor.callproc("sp_InsertarSolicitudReserva", (clase_id, gimnasio_id, fecha, hora, usuario_id))
            solicitud_id = cursor.fetchone()[0]
            conn.commit()

            cursor.execute("SELECT dc_correo_electronico, dc_nombre FROM tb_usuario WHERE id = %s", [usuario_id])
            user_email, user_name = cursor.fetchone()

        conn.close()

        cuerpo_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; margin: 0; padding: 0;">
            <div style="background-color: #f4f4f4; padding: 20px;">
                <div style="max-width: 600px; background-color: #ffffff; margin: auto; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1);">
                    <h2 style="color: #333;">Hola {user_name},</h2>
                    <p>Tu reserva para la clase ha sido creada correctamente.</p>
                    <p><strong>Fecha:</strong> {fecha}</p>
                    <p><strong>Hora:</strong> {hora}</p>
                    <p>Gracias por usar Martial Apps. Esperamos que disfrutes de tu clase.</p>
                    <p>Saludos,<br>El equipo de Martial Apps</p>
                    <div style="text-align: center; margin-top: 20px;">
                        <a href="http://127.0.0.1:5173/" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Ir a Martial Apps</a>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """

        enviar_correo(user_email, "Reserva de Clase - Martial Apps", cuerpo_html)

        return jsonify({"ok": True, "mensaje": "Solicitud de reserva creada correctamente y correo enviado", "solicitud": {"id": solicitud_id, "clase_id": clase_id, "gimnasio_id": gimnasio_id, "fecha": fecha, "hora": hora, "usuario_id": usuario_id}}), 200

    except Exception as e:
        return jsonify({"ok": False, "mensaje": str(e), "solicitud": None}), 500


@routes.route("/reservasUsuario/<int:usuario_id>", methods=["GET"])
def get_reservation(usuario_id):
    try:
        conn = get_conection()
        with conn.cursor() as cursor:
            cursor.callproc("sp_ObtenerReservasUsuario", [usuario_id])
            reservas = cursor.fetchall()
        conn.close()
        
        results = []
        for reserva in reservas:
            time_value = reserva[3]
            if isinstance(time_value, timedelta):
                hours, remainder = divmod(time_value.seconds, 3600)
                minutes, _ = divmod(remainder, 60)
                time_str = f"{hours:02}:{minutes:02}:00"
            else:
                time_str = time_value.strftime("%H:%M:%S")
                
            results.append({
                "id": reserva[0],
                "class": reserva[1],
                "date": reserva[2].strftime("%Y-%m-%d"),
                "time": time_str,
                "description": reserva[4],
                "gymImage": reserva[5]
            })
        
        return jsonify({"ok": True, "reservas": results}), 200


    except Exception as e:
        return jsonify({"ok": False, "mensaje": str(e)}), 500


@routes.route("/cancelarReserva/<int:reserva_id>", methods=["DELETE"])
def cancelar_reserva(reserva_id):
    try:
        conn = get_conection()
        with conn.cursor() as cursor:
            cursor.callproc("sp_CancelarSolicitudReserva", [reserva_id])
            conn.commit()
        conn.close()

        return jsonify({"ok": True, "mensaje": "Reserva cancelada exitosamente"}), 200

    except Exception as e:
        return jsonify({"ok": False, "mensaje": str(e)}), 500
    
    

from datetime import timedelta

@routes.route("/user/reservation-requests", methods=["GET"])
def get_reservation_requests():
    try:
        # Obtener el ID del usuario desde la solicitud
        tb_usuario_id = request.args.get("tb_usuario_id")

        # Llamar al stored procedure para obtener las solicitudes de reserva del usuario
        conn = get_conection()
        with conn.cursor() as cursor:
            cursor.callproc("sp_ObtenerSolicitudesReservaUsuario", (tb_usuario_id,))
            result = cursor.fetchall()
        conn.close()

        # Convertir el resultado en un formato JSON
        columns = [
            "solicitud_id",
            "nb_clase_id",
            "dc_horario",
            "nb_cupos_disponibles",
            "df_fecha",
            "df_hora",
            "tb_gimnasio_id",
            "dc_nombre_clase",
            "dc_imagen_url"
        ]
        
        json_result = []
        for row in result:
            row_dict = dict(zip(columns, row))
            if isinstance(row_dict["df_hora"], timedelta):
                # Convertir timedelta a string en formato HH:MM:SS
                row_dict["df_hora"] = str(row_dict["df_hora"])
            json_result.append(row_dict)

        return jsonify(json_result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Configuracion de correos

def enviar_correo_async(app, destinatario, asunto, cuerpo_html):
    print("Enviando correo...")
    with app.app_context():
        try:
            msg = Message(asunto, sender=current_app.config['MAIL_USERNAME'], recipients=[destinatario])
            msg.html = cuerpo_html
            mail.send(msg)
            print("Correo enviado exitosamente!")
        except Exception as e:
            print("Error al enviar el correo:", str(e))

def enviar_correo(destinatario, asunto, cuerpo_html):
    thr = Thread(target=enviar_correo_async, args=[current_app._get_current_object(), destinatario, asunto, cuerpo_html])
    thr.start()

@routes.route('/aceptar_solicitud/<int:id_solicitud>', methods=['POST'])
def aceptar_solicitud(id_solicitud):
    try:
        conn = get_conection()
        cursor = conn.cursor()
        cursor.callproc('sp_AceptarSolicitudRegistro', [id_solicitud])
        conn.commit()

        cursor.execute("SELECT id_gimnasio FROM tb_solicitud_registro WHERE id_solicitud_registro = %s", [id_solicitud])
        id_gimnasio = cursor.fetchone()[0]

        cursor.execute("SELECT dc_correo_electronico, dc_nombre FROM tb_gimnasio WHERE id = %s", [id_gimnasio])
        gym_email, gym_name = cursor.fetchone()

        cuerpo_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; margin: 0; padding: 0;">
            <div style="background-color: #f4f4f4; padding: 20px;">
                <div style="max-width: 600px; background-color: #ffffff; margin: auto; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1);">
                    <h2 style="color: #333;">Hola {gym_name},</h2>
                    <p>Tu solicitud de registro ha sido <strong>aceptada</strong>.</p>
                    <p>¡Bienvenido a Martial Apps!</p>
                    <p>Gracias por unirte a nuestra comunidad. Ahora puedes acceder a todas las funciones de nuestra plataforma.</p>
                    <p>Saludos,<br>El equipo de Martial Apps</p>
                    <div style="text-align: center; margin-top: 20px;">
                        <a href="http://127.0.0.1:5173/" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Ir a Martial Apps</a>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """

        enviar_correo(gym_email, "Solicitud Aceptada - Martial Apps", cuerpo_html)

        return jsonify({"mensaje": "Solicitud aceptada y correo enviado correctamente"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@routes.route('/rechazar_solicitud/<int:id_solicitud>', methods=['POST'])
def rechazar_solicitud(id_solicitud):
    try:
        conn = get_conection()
        cursor = conn.cursor()
        cursor.callproc('sp_RechazarSolicitudRegistro', [id_solicitud])
        conn.commit()

        cursor.execute("SELECT id_gimnasio FROM tb_solicitud_registro WHERE id_solicitud_registro = %s", [id_solicitud])
        id_gimnasio = cursor.fetchone()[0]

        cursor.execute("SELECT dc_correo_electronico, dc_nombre FROM tb_gimnasio WHERE id = %s", [id_gimnasio])
        gym_email, gym_name = cursor.fetchone()

        cuerpo_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; margin: 0; padding: 0;">
            <div style="background-color: #f4f4f4; padding: 20px;">
                <div style="max-width: 600px; background-color: #ffffff; margin: auto; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1);">
                    <h2 style="color: #333;">Hola {gym_name},</h2>
                    <p>Lamentamos informarte que tu solicitud de registro ha sido <strong>rechazada</strong>.</p>
                    <p>Te agradecemos por tu interés en unirte a Martial Apps.</p>
                    <p>Si tienes alguna duda o necesitas más información, no dudes en contactarnos.</p>
                    <p>Saludos,<br>El equipo de Martial Apps</p>
                </div>
            </div>
        </body>
        </html>
        """

        enviar_correo(gym_email, "Solicitud Rechazada - Martial Apps", cuerpo_html)

        return jsonify({"mensaje": "Solicitud rechazada y correo enviado correctamente"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

"""comentarios y calificaciones"""

@routes.route("/comments/gym/<int:gym_id>", methods=["GET", "POST"])
def handle_gym_comments(gym_id):
    if request.method == "POST":
        data = request.json
        user_id = data.get('user_id')
        comment = data.get('comment')
        rating = data.get('rating')

        if not user_id or not comment or not rating:
            return jsonify({"error": "Missing fields"}), 400

        try:
            conn = get_conection()
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO tb_comentarios_gimnasio (tb_gimnasio_id, tb_usuario_id, dc_comentario, nb_puntaje) VALUES (%s, %s, %s, %s)",
                    (gym_id, user_id, comment, rating)
                )
            conn.commit()
            conn.close()
            return jsonify({"message": "Comment added", "comment": comment, "rating": rating, "status": 201}), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    else:
        try:
            conn = get_conection()
            with conn.cursor() as cursor:
                cursor.execute(
                    """SELECT c.dc_comentario, c.nb_puntaje, c.df_fecha, u.dc_nombre
                       FROM tb_comentarios_gimnasio c
                       JOIN tb_usuario u ON c.tb_usuario_id = u.id
                       WHERE c.tb_gimnasio_id = %s""", (gym_id,)
                )
                result = cursor.fetchall()
            conn.close()
            comments = [{"comment": row[0], "rating": row[1], "date": row[2], "user": row[3]} for row in result]
            return jsonify({"comments": comments}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

@routes.route("/comments/class/<int:class_id>", methods=["GET", "POST"])
def handle_class_comments(class_id):
    if request.method == "POST":
        data = request.json
        user_id = data.get('user_id')
        comment = data.get('comment')
        rating = data.get('rating')

        if not user_id or not comment or not rating:
            return jsonify({"error": "Missing fields"}), 400

        try:
            conn = get_conection()
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO tb_comentarios_clase (tb_clase_id, tb_usuario_id, dc_comentario, nb_puntaje) VALUES (%s, %s, %s, %s)",
                    (class_id, user_id, comment, rating)
                )
            conn.commit()
            conn.close()
            return jsonify({"message": "Comment added", "comment": comment, "rating": rating , "status": 201}), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    else:
        try:
            conn = get_conection()
            with conn.cursor() as cursor:
                cursor.execute(
                    """SELECT c.dc_comentario, c.nb_puntaje, c.df_fecha, u.dc_nombre
                       FROM tb_comentarios_clase c
                       JOIN tb_usuario u ON c.tb_usuario_id = u.id
                       WHERE c.tb_clase_id = %s""", (class_id,)
                )
                result = cursor.fetchall()
            conn.close()
            comments = [{"comment": row[0], "rating": row[1], "date": row[2], "user": row[3]} for row in result]
            return jsonify({"comments": comments}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        
# Recomend gym
@routes.route("/recommendations", methods=["POST"])
def recommend_gym():
    try:
        data = request.get_json()
        gym_id = data.get("gymId")
        user_id = data.get("userId")
        fecha_recomendacion = datetime.now()

        if not gym_id or not user_id:
            return jsonify({"error": "Missing gymId or userId"}), 400

        conn = get_conection()
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO tb_recommendations (usuario_id, gimnasio_id, fecha_recomendacion) VALUES (%s, %s, %s)",
                (user_id, gym_id, fecha_recomendacion)
            )
            conn.commit()
        
        # Obtener el correo electrónico del gimnasio
        with conn.cursor() as cursor:
            cursor.execute("SELECT dc_correo_electronico FROM tb_gimnasio WHERE id = %s", (gym_id,))
            gym_email = cursor.fetchone()[0]
        
        conn.close()

        # Enviar notificación de recomendación por correo
        send_recommendation_email(gym_email)

        return jsonify({"message": "Gimnasio recomendado exitosamente"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@routes.route("/recommendations/count/<int:gym_id>", methods=["GET"])
def get_recommendation_count(gym_id):
    try:
        conn = get_conection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM tb_recommendations WHERE gimnasio_id = %s", (gym_id,))
            count = cursor.fetchone()[0]
        conn.close()
        return jsonify({"recommendation_count": count}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Función para enviar un correo de notificación
def send_recommendation_email(gym_email):
    try:
        msg = Message("Nueva Recomendación de Gimnasio",
                      sender=current_app.config['MAIL_USERNAME'],
                      recipients=[gym_email])
        msg.body = "¡Felicidades! Tu gimnasio ha sido recomendado por un usuario."
        thr = Thread(target=send_async_email, args=[current_app._get_current_object(), msg])
        thr.start()
    except Exception as e:
        print(f"Error al enviar el correo: {e}")

def send_async_email(app, msg):
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            print(f"Error al enviar el correo: {e}")


@routes.route("/reportUser", methods=["POST"])
def report_user():
    try:
        data = request.get_json()

        reportado_id = data.get("user_id")
        reporter_id = data.get("reporter_id")
        reporter_type = data.get("reporter_type")
        report_reason = data.get("reason")
        report_details = data.get("details")

        conn = get_conection() 
        with conn.cursor() as cursor:
            cursor.callproc(
                "sp_ReporteUsuario",
                (
                    reportado_id,
                    reporter_id,
                    reporter_type,
                    report_reason,
                    report_details,
                ),
            )
            conn.commit()

        conn.close()

        return jsonify({"mensaje": "Reporte enviado correctamente"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Aceptar reporte de usuario
@routes.route('/acceptReport/<int:report_id>', methods=['POST'])
def accept_report(report_id):
    if request.method == 'POST':
        data = request.get_json()
        reporter_id = data.get("reporter_id")
        try:
            # Actualizar estado del usuario reportado a inactivo y marcar como reportado
            update_query = """
                UPDATE tb_usuario
                SET tb_usuario_estado_id = 2, usuario_reportado = 1
                WHERE id = %s
            """
            # Establecer conexión y ejecutar la consulta de actualización
            conn = get_conection()
            cursor = conn.cursor()
            cursor.execute(update_query, (reporter_id,))
            conn.commit()

            # Verificar si se actualizó algún registro
            if cursor.rowcount == 0:
                return jsonify({"error": f"No se encontró ningún usuario con id {reporter_id}"}), 404

            # Consulta para obtener correo electrónico y nombre del reportador
            reportador_info_query = """
                SELECT dc_correo_electronico, dc_nombre FROM tb_usuario WHERE id = %s
            """
            cursor.execute(reportador_info_query, (reporter_id,))
            result = cursor.fetchone()

            # Verificar si se encontraron resultados
            if not result:
                return jsonify({"error": f"No se encontró ningún usuario con id {reporter_id}"}), 404

            reportador_email, reportador_name = result

            # Construir y enviar correo con plantilla HTML
            asunto = "Suspensión de Usuario Reportado"
            cuerpo_html = f"""
                <html>
                    <body style="font-family: Arial, sans-serif; margin: 0; padding: 0;">
                        <div style="background-color: #f4f4f4; padding: 20px;">
                            <div style="max-width: 600px; background-color: #ffffff; margin: auto; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1);">
                                <h2 style="color: #333;">Suspensión de Usuario Reportado</h2>
                                <p>Estimado {reportador_name},</p>
                                <p>Le informamos que su cuenta ha sido suspendida debido a reportes.</p>
                                <p>Atentamente,<br>Equipo de Administración</p>
                            </div>
                        </div>
                    </body>
                </html>
            """

            # Enviar correo de manera asíncrona
            enviar_correo(reportador_email, asunto, cuerpo_html)

            # Cerrar conexión
            cursor.close()
            conn.close()

            return jsonify({"message": "Report accepted and email sent"}), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return jsonify({"error": "Method not allowed"}), 405

# Rechazar reporte de usuario
@routes.route('/rejectReport/<int:report_id>', methods=['POST'])
def reject_report(report_id):
    if request.method == 'POST':
        data = request.get_json()
        reporter_id = data.get('reporter_id')
        reject_reason = data.get('reject_reason')

        if not reporter_id or not reject_reason:
            return jsonify({"error": "Missing reporter_id or reject_reason"}), 400

        try:
            # Consulta para obtener correo electrónico y nombre del reportador
            reportador_info_query = """
                SELECT dc_correo_electronico, dc_nombre FROM tb_gimnasio WHERE id = %s
            """
            # Establecer conexión y ejecutar la consulta
            conn = get_conection()
            cursor = conn.cursor()
            cursor.execute(reportador_info_query, (reporter_id,))
            result = cursor.fetchone()

            # Verificar si se encontraron resultados
            if not result:
                return jsonify({"error": f"No se encontró ningún usuario con id {reporter_id}"}), 404

            reportador_email, reportador_name = result

            # Construir y enviar correo con plantilla HTML
            asunto = "Desistimiento de Suspensión de Usuario Reportado"
            cuerpo_html = f"""
                <html>
                    <body style="font-family: Arial, sans-serif; margin: 0; padding: 0;">
                        <div style="background-color: #f4f4f4; padding: 20px;">
                            <div style="max-width: 600px; background-color: #ffffff; margin: auto; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1);">
                                <h2 style="color: #333;">Desistimiento de Suspensión de Usuario Reportado</h2>
                                <p>Estimado {reportador_name},</p>
                                <p>Le informamos que se ha desistido de la suspensión del usuario reportado.</p>
                                <p>Motivo del desistimiento: {reject_reason}</p>
                                <p>Atentamente,<br>Equipo de Administración</p>
                            </div>
                        </div>
                    </body>
                </html>
            """

            # Enviar correo de manera asíncrona
            enviar_correo(reportador_email, asunto, cuerpo_html)

            # Cerrar conexión
            cursor.close()
            conn.close()

            return jsonify({"message": "Report rejected and email sent"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return jsonify({"error": "Method not allowed"}), 405

    # Endpoint para obtener todos los reportes de usuarios
@routes.route('/pendingReports', methods=['GET'])
def get_reports():
    try:
        # Establecer conexión y obtener cursor
        conn = get_conection()
        cursor = conn.cursor()

        # Consulta SQL para obtener todos los reportes
        query = """
            SELECT
                ru.id AS report_id,
                ru.user_id,
                u.dc_nombre AS user_name,
                ru.reporter_id,
                ru.reporter_type,
                ru.reason AS report_reason,
                ru.details AS report_details,
                ru.created_at AS report_created_at
            FROM reportes_usuario ru
            JOIN tb_usuario u ON ru.user_id = u.id
            ORDER BY ru.created_at DESC
        """

        # Ejecutar la consulta
        cursor.execute(query)

        # Obtener todos los reportes
        reports = []
        for row in cursor.fetchall():
            report = {
                "report_id": row[0],
                "user_id": row[1],
                "user_name": row[2],
                "reporter_id": row[3],
                "reporter_type": row[4],
                "report_reason": row[5],
                "report_details": row[6],
                "report_created_at": row[7].isoformat()  # Convertir a formato ISO para ser JSON serializable
            }
            reports.append(report)

        # Cerrar cursor y conexión
        cursor.close()
        conn.close()

        # Devolver los reportes como JSON
        return jsonify({"reports": reports}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@routes.route("/favorites", methods=["POST"])
def add_favorite():
    try:
        data = request.get_json()
        user_id = data.get("userId")
        gym_id = data.get("gymId")

        if not user_id or not gym_id:
            return jsonify({"error": "Missing userId or gymId"}), 400

        conn = get_conection()
        with conn.cursor() as cursor:
            # Verificar si la relación usuario-gimnasio ya existe
            cursor.execute(
                "SELECT * FROM tb_favoritos WHERE usuario_id = %s AND gimnasio_id = %s",
                (user_id, gym_id)
            )
            existing_favorite = cursor.fetchone()

            if existing_favorite:
                return jsonify({"message": "Gimnasio ya está en favoritos", "color": "error"}), 200

            # Si no existe, insertar la nueva relación
            cursor.execute(
                "INSERT INTO tb_favoritos (usuario_id, gimnasio_id) VALUES (%s, %s)",
                (user_id, gym_id)
            )
            conn.commit()
        conn.close()

        return jsonify({"message": "Gimnasio agregado a favoritos", "color": "success"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@routes.route("/favorites", methods=["DELETE"])
def remove_favorite():
    try:
        data = request.get_json()
        user_id = data.get("userId")
        gym_id = data.get("gymId")

        if not user_id or not gym_id:
            return jsonify({"error": "Missing userId or gymId"}), 400

        conn = get_conection()
        with conn.cursor() as cursor:
            cursor.execute(
                "DELETE FROM tb_favoritos WHERE usuario_id = %s AND gimnasio_id = %s",
                (user_id, gym_id)
            )
            conn.commit()
        conn.close()

        return jsonify({"message": "Gimnasio eliminado de favoritos"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@routes.route("/favorites/<int:user_id>", methods=["GET"])
def get_favorites(user_id):
    try:
        conn = get_conection()
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT g.id, g.dc_nombre, g.dc_ubicacion, g.dc_imagen_url FROM tb_favoritos f JOIN tb_gimnasio g ON f.gimnasio_id = g.id WHERE f.usuario_id = %s",
                (user_id,)
            )
            result = cursor.fetchall()
        conn.close()

        favorites = [{"id": row[0], "nombre": row[1], "ubicacion": row[2], "imagen_url": row[3]} for row in result]
        return jsonify({"favorites": favorites}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

        """Programacion de recordatorios y demas"""

def send_reminder():
    conn = mysql.connector.connect(user='tu_usuario', password='tu_contraseña', host='localhost', database='tu_base_de_datos')
    cursor = conn.cursor()

    # Selecciona las reservas para mañana y obtén el correo del usuario
    query = """
        SELECT u.dc_correo_electronico
        FROM tb_solicitud_reserva r
        JOIN tb_usuario u ON r.tb_usuario_id = u.id
        WHERE r.df_fecha = %s
    """
    cursor.execute(query, (datetime.now().date() + timedelta(days=1),))

    for (dc_correo_electronico,) in cursor:
        enviar_correo(dc_correo_electronico, "Recordatorio de Reserva", "Tienes una reserva para mañana.")

    cursor.close()
    conn.close()

# Programa la tarea de recordatorio para que se ejecute diariamente
scheduler.add_job(send_reminder, 'interval', days=1)
scheduler.start()



def send_scheduled_reminder(app, data):
    with app.app_context():
        conn = get_conection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT dc_correo_electronico, dc_telefono FROM tb_usuario WHERE id = %s", (data['id_usuario'],))
            usuario = cursor.fetchone()
        conn.close()
        
        email_body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6;">
                <div style="max-width: 600px; margin: auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1);">
                    <h2 style="text-align: center; color: #007BFF;">Recordatorio de Entrenamiento</h2>
                    <p>Hola,</p>
                    <p>Este es un recordatorio para tu próxima sesión de entrenamiento.</p>
                    <p><strong>Fecha:</strong> {data['fecha']}</p>
                    <p><strong>Hora:</strong> {data['hora']}</p>
                    <p><strong>Mensaje:</strong> {data['mensaje']}</p>
                    <p>Esperamos que disfrutes de tu entrenamiento y logres todos tus objetivos.</p>
                    <p>Gracias por confiar en nosotros.</p>
                    <div style="text-align: center; margin-top: 20px;">
                        <img src="https://i.ibb.co/Wfv1md5/martiallogo.jpg" alt="MartialApps" style="width: 150px;">
                    </div>
                    <p style="text-align: center; margin-top: 20px; font-size: 0.9em; color: #555;">
                        &copy; {datetime.now().year} MartialApps. Todos los derechos reservados.
                    </p>
                </div>
            </body>
        </html>
        """
        
        enviar_correo(usuario[0], "Recordatorio de Entrenamiento", email_body)
        # enviar_whatsapp(usuario[1], data['mensaje'])

@routes.route('/schedule_reminder', methods=['POST'])
def schedule_reminder():
    data = request.json
    conn = get_conection()
    with conn.cursor() as cursor:
        cursor.callproc("sp_ProgramarRecordatorio", (
            data['id_usuario'], 
            data['fecha'], 
            data['hora'], 
            data['mensaje']
        ))
        conn.commit()

    conn.close()

    # Obtener la instancia de la aplicación actual
    app = current_app._get_current_object()

    reminder_time = datetime.strptime(data['fecha'] + ' ' + data['hora'], '%Y-%m-%d %H:%M:%S')
    scheduler.add_job(send_scheduled_reminder, 'date', run_date=reminder_time, args=[app, data])

    return "Recordatorio programado", 200
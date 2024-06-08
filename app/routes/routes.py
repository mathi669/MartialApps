import requests
from app.database.mysql_conection import get_conection
from flask import Blueprint, request, jsonify, session, current_app
from ..models.user import ModelUser
from ..models.entities.Usersmodel import User
from datetime import datetime, timedelta, date, time
from decouple import config
from app.services.AuthService import AuthService
from app.utils.Security import Security
from ..models.schedule import ScheduleModel
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity,
)
from flask_mail import Message
import mysql.connector

routes = Blueprint("routes", __name__)

jwtoken = config("JWT_SECRET_KEY")

jwt = JWTManager()

# Configuración de la API de ImgBB
IMG_API_KEY = config("IMG_BB_KEY")


# Función para subir imagen a ImgBB
def upload_image_to_imgbb(base64_image):
    url = "https://api.imgbb.com/1/upload"
    payload = {"key": IMG_API_KEY, "image": base64_image}
    response = requests.post(url, data=payload)
    print(response.text)
    return response


"""access and register routes"""

@routes.route("/registerGym", methods=["POST"])
def register_gym():
    try:
        # Obtener datos del cuerpo de la solicitud
        data = request.get_json()

        # Extraer datos del cuerpo de la solicitud
        nombre_gimnasio = data.get("nombreGimnasio")
        correo = data.get("correo")
        contrasena = data.get("contrasena")
        telefono = data.get("telefonoGimnasio")
        ubicacion_gimnasio = data.get("ubicacionGimnasio")

        # Verificar si todos los campos requeridos están presentes y no son nulos
        required_fields = {
            "nombreGimnasio",
            "correo",
            "contrasena",
            "telefonoGimnasio",
            "ubicacionGimnasio",
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

        # Llamar al stored procedure para registrar el gimnasio
        conn = get_conection()
        with conn.cursor() as cursor:
            # Obtener el último ID de la tabla tb_gimnasio
            cursor.execute("SELECT MAX(id) FROM tb_gimnasio")
            last_id = cursor.fetchone()[0]
            
            # Calcular el nuevo ID sumando 1 al último ID obtenido
            new_id = last_id + 1
            
            # Definir el horario y la descripción predeterminados
            horario_predeterminado = "9:00 - 16:00"
            descripcion_predeterminada = "Aquí debe ir la descripción del gimnasio"
            img = "Aquí debe ir la descripción del gimnasio"
            
            # Insertar el nuevo registro en la tabla tb_gimnasio con el nuevo ID
            cursor.execute(
                "INSERT INTO tb_gimnasio (id, dc_nombre, dc_correo_electronico, dc_contrasena, dc_telefono, dc_ubicacion, dc_horario, df_fecha_ingreso, dc_descripcion, dc_imagen_url) VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), %s, %s)",
                (new_id, nombre_gimnasio, correo, contrasena, telefono, ubicacion_gimnasio, horario_predeterminado, descripcion_predeterminada, img),
            )
            conn.commit()

            # Llamar al stored procedure para registrar la solicitud de registro
            cursor.callproc(
                "sp_InsertarSolicitudRegistro",
                (new_id, datetime.datetime.now()),
            )
            conn.commit()

        conn.close()

        # Devolver respuesta exitosa
        return jsonify({"mensaje": "Solicitud de registro de gimnasio enviada correctamente"}), 200

    except Exception as e:
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
        nivel_id = data.get("tb_nivel_artes_marciales_id")
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
        # Obtener datos del formulario
        data = request.form
        image = request.files.get("image")
        image_url = data.get("dc_imagen_url")

        # Si se proporciona una nueva imagen, subirla a ImgBB
        if image:
            response = upload_image_to_imgbb(image)
            if not response.ok:
                return jsonify({"error": "Failed to upload image"}), 500
            image_url = response.json()["data"]["url"]

        # Conectar a la base de datos y llamar al procedimiento almacenado
        conn = get_conection()
        with conn.cursor() as cursor:
            cursor.callproc(
                "sp_ActualizarGimnasio",
                (
                    gym_id,
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

        return jsonify({"mensaje": "Gimnasio actualizado correctamente"}), 200

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
    try:
        conn = get_conection()  # Obtener conexión a la base de datos
        with conn.cursor() as cursor:
            cursor.callproc("sp_GetAllGimnasios")
            result = (
                cursor.fetchall()
            )  # Obtener todos los registros devueltos por el procedimiento almacenado
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


"""User routes"""


@routes.route("/get_users", methods=["GET"])
# @jwt_required()
def get_users():
    try:
        if request.method == "GET":
            users = ModelUser.get_users()
            return jsonify(users), 200
        else:
            return jsonify({"error": "Método no permitido"}), 405
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@routes.route("/get_user/<int:user_id>", methods=["GET"])
def get_user_by_id(user_id):
    try:
        if request.method == "GET":
            user = ModelUser.get_user_by_id(user_id)
            if user:
                return jsonify(user), 200
            else:
                return jsonify({"error": "Usuario no encontrado"}), 404
        else:
            return jsonify({"error": "Método no permitido"}), 405
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


@routes.route("/create_class", methods=["POST"])
def create_class():
    conn = None
    cursor = None
    try:
        data = request.get_json()

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
            ),
        )
        conn.commit()
        result = cursor.fetchall()

        if result and result[0]["success"]:
            return (
                jsonify({"message": "Clase creada exitosamente!", "class": result[0]}),
                200,
            )
        else:
            return jsonify({"error": "No se pudo crear la clase."}), 400

    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 400
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


@routes.route("/update_class/<int:class_id>", methods=["PUT"])
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
                    data["id_categoria"],
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
            solicitudes = cursor.fetchall()
        conn.close()

        # Convertir las solicitudes obtenidas a un formato JSON y devolverlas
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
        hora = data.get("hora")

        required_fields = {"clase_id", "gimnasio_id", "usuario_id", "fecha", "hora"}
        missing_fields = required_fields - set(data.keys())
        if missing_fields:
            return jsonify({"ok": False, "mensaje": f'Faltan los siguientes campos: {", ".join(missing_fields)}', "solicitud": None}), 400

        conn = get_conection()
        with conn.cursor() as cursor:
            cursor.callproc("sp_InsertarSolicitudReserva", (clase_id, gimnasio_id, fecha, hora, usuario_id))
            solicitud_id = cursor.fetchone()[0]
            conn.commit()

            # Obtener correo del usuario
            cursor.execute("SELECT dc_correo_electronico FROM tb_usuario WHERE id = %s", [usuario_id])
            user_email = cursor.fetchone()[0]

        conn.close()

        # Enviar correo de confirmación de reserva
        cuerpo_html = f"<p>Hola,</p><p>Tu reserva para la clase ha sido creada correctamente.</p><p>Fecha: {fecha}</p><p>Hora: {hora}</p>"
        enviar_correo(user_email, "Reserva de Clase", cuerpo_html)

        return jsonify({"ok": True, "mensaje": "Solicitud de reserva creada correctamente y correo enviado", "solicitud": {"id": solicitud_id, "clase_id": clase_id, "gimnasio_id": gimnasio_id, "fecha": fecha, "hora": hora, "usuario_id": usuario_id}}), 200

    except Exception as e:
        return jsonify({"ok": False, "mensaje": str(e), "solicitud": None}), 500



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

def enviar_correo(destinatario, asunto, cuerpo_html):
    msg = Message(asunto, sender=current_app.config['MAIL_USERNAME'], recipients=[destinatario])
    msg.html = cuerpo_html
    mail = current_app.extensions.get('mail')
    mail.send(msg)

@routes.route('/aceptar_solicitud/<int:id_solicitud>', methods=['POST'])
def aceptar_solicitud(id_solicitud):
    try:
        conn = get_conection()
        cursor = conn.cursor()
        cursor.callproc('sp_AceptarSolicitudRegistro', [id_solicitud])
        conn.commit()

        # Obtener detalles de la solicitud y el gimnasio
        cursor.execute("SELECT id_gimnasio FROM tb_solicitud_registro WHERE id_solicitud_registro = %s", [id_solicitud])
        id_gimnasio = cursor.fetchone()[0]

        cursor.execute("SELECT dc_correo_electronico FROM tb_gimnasio WHERE id = %s", [id_gimnasio])
        gym_email = cursor.fetchone()[0]

        # Enviar correo de confirmación
        cuerpo_html = f"<p>Hola,</p><p>Tu solicitud de registro ha sido aceptada.</p>"
        enviar_correo(gym_email, "Solicitud Aceptada", cuerpo_html)

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

        # Obtener detalles de la solicitud y el gimnasio
        cursor.execute("SELECT id_gimnasio FROM tb_solicitud_registro WHERE id_solicitud_registro = %s", [id_solicitud])
        id_gimnasio = cursor.fetchone()[0]

        cursor.execute("SELECT dc_correo_electronico FROM tb_gimnasio WHERE id = %s", [id_gimnasio])
        gym_email = cursor.fetchone()[0]

        # Enviar correo de rechazo
        cuerpo_html = f"<p>Hola,</p><p>Tu solicitud de registro ha sido rechazada.</p>"
        enviar_correo(gym_email, "Solicitud Rechazada", cuerpo_html)

        return jsonify({"mensaje": "Solicitud rechazada y correo enviado correctamente"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
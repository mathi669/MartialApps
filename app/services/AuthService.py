from app.database.mysql_conection import get_conection


class AuthService:

    @classmethod
    def login_user(cls, user_type, user_data):
        try:
            conn = get_conection()
            print(user_data["dc_correo_electronico"])
            with conn.cursor() as cursor:
                if user_type == "usuario":
                    cursor.callproc(
                        "sp_AuthUser",
                        (
                            user_data["dc_correo_electronico"],
                            user_data["dc_contrasena"],
                        ),
                    )
                elif user_type == "gimnasio":
                    cursor.callproc(
                        "sp_AuthGym",
                        (
                            user_data["dc_correo_electronico"],
                            user_data["dc_contrasena"],
                        ),
                    )
                result = cursor.fetchone()
                print(result)

                if (
                    result and result[0]
                ):  # Verificar si el primer elemento indica si el usuario existe
                    if user_type == "gimnasio":
                        gimnasio_data = {
                            "success": result[0],
                            "id": result[1],
                            "dc_nombre": result[2],
                            "dc_correo_electronico": user_data["dc_correo_electronico"],
                            "dc_telefono": result[3],
                            "dc_ubicacion": result[4],
                            "dc_horario": result[5],
                            "df_fecha_ingreso": result[6],
                            "dc_descripcion": result[7],
                            "dc_imagen_url": result[8],
                            "tb_gimnasio_estado_id": result[9],
                            "message": "Gimnasio autenticado exitosamente.",
                        }
                        return {
                            "success": True,
                            "user": gimnasio_data,
                            "message": "Autenticación exitosa",
                        }
                    else:
                        user_data = {
                            "id": result[1],
                            "dc_nombre": result[2],
                            "dc_correo_electronico": user_data["dc_correo_electronico"],
                            "dc_telefono": result[4],
                            "tb_nivel_artes_marciales_id": result[5],
                            "df_fecha_solicitud": result[6],
                            "tb_tipo_usuario_id": result[7],
                            "tb_usuario_estado_id": result[8],
                            "tb_nivel_id": result[9],
                            "tb_contacto_emergencia_id": result[10],
                            "es_gimnasio": result[11],
                            "message": "Usuario autenticado exitosamente.",
                        }
                        return {
                            "success": True,
                            "user": user_data,
                            "message": "Autenticación exitosa",
                        }
                else:
                    return {
                        "success": False,
                        "message": "Usuario o contraseña incorrectos",
                    }
        except Exception as e:
            print("Error en el método login_user:", e)
            raise  # Vuelve a lanzar la excepción original
        finally:
            conn.close()

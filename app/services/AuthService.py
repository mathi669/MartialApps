from app.database.mysql_conection import get_conection
from app.models.user import User


class AuthService:

    @classmethod
    def login_user(cls, user_type, user):
        try:
            conn = get_conection() 
            print(user.dc_correo_electronico)
            with conn.cursor() as cursor:
                if user_type == 'usuario':
                    cursor.callproc('sp_AuthUser', (user.dc_correo_electronico, user.dc_contrasena))
                elif user_type == 'gimnasio':
                    cursor.callproc('sp_AuthGym', (user.dc_correo_electronico, user.dc_contrasena))
                result = cursor.fetchone()
                print(result)
                
                if result and result[0]:  # Verificar si el primer elemento indica si el usuario existe
                    if user_type == 'gimnasio':
                        gimnasio_data = {
                            "success": result[0],
                            "id": result[1],
                            "dc_nombre": result[2],
                            "dc_correo_electronico": user.dc_correo_electronico,
                            "dc_telefono": result[3],
                            "dc_ubicacion": result[4],
                            "dc_horario": result[5],
                            "df_fecha_ingreso": result[6],
                            "dc_descripcion": result[7],
                            "dc_imagen_url": result[8],
                            "tb_gimnasio_estado_id": result[9]
                        }
                        return gimnasio_data
                    else:
                        return {
                            "id_usuario": result[1],
                            "dc_correo_electronico": user.dc_correo_electronico
                        }
                else:
                    return None
        except Exception as e:
            print("Error en el método login_user:", e)
            raise  # Vuelve a lanzar la excepción original
        finally:
            conn.close()

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
                if (
                    result and result[0]
                ):  # Verificar si el primer elemento indica si el usuario existe
                    user.id_usuario = result[
                        1
                    ]  # Asignar el ID del usuario (segundo elemento)
                    return user
                else:
                    return None
        except Exception as e:
            print("Error en el método login_user:", e)
            raise  # Vuelve a lanzar la excepción original
        finally:
            conn.close() 

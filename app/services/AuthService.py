from app.database.mysql_conection import get_conection
from app.models.user import User

class AuthService():
    
    @classmethod
    def login_user(cls, user):
        try:
            authenticated_user = False
            conn = get_conection()  # Obtener conexión a la base de datos
            print(user.dc_correo_electronico)
            with conn.cursor() as cursor:
                cursor.callproc('sp_AuthUser', (user.dc_correo_electronico, user.dc_contrasena))
                result = cursor.fetchone()
                print(result)
                if result[0] == 1:
                    authenticated_user = user
        except Exception as e:
            print("Error en el método login_user:", e)
            raise  # Vuelve a lanzar la excepción original
        finally:
            conn.close()  # Asegúrate de cerrar la conexión
        return authenticated_user
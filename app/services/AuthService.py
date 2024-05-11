from app.database.mysql_conection import get_conection
from app.models.user import User

class AuthService():
    
    @classmethod
    def login_user(cls, user):
        try:
            conn = get_conection()
            authenticated_user = None
            with conn.cursor() as cursor:
                cursor.execute('call sp_AuthUser(%s, %s)', (user.dc_correo_electronico, user.dc_contrasena))
                row = cursor.fetchone()
                if row != None:
                    authenticated_user = User(int(row[0]), row[1], None, row[2])
            conn.close()
            return authenticated_user
        except Exception as e:
            raise Exception(e)
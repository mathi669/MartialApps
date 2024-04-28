from .entities.Usersmodel import User
from ..database.mysql_conection import get_conection

class ModelUser():
    
    @classmethod
    def get_users(self):
        try:
            conection = get_conection()
            users = []
            with conection.cursor() as cursor:
                cursor.execute("SELECT id, dc_nombre, dc_contrasena, dc_correo_electronico, dc_telefono FROM tb_usuario")
                resultset=cursor.fetchall()
                
                for row in resultset:
                    user = User(row[0],row[1],row[2],row[3],row[4])
                    users.append(user.to_JSON())
                    
            conection.close()
            return users
        except Exception as ex:
            raise Exception(ex)
    
    @classmethod
    def login(self, user):
        try:
            cursor = get_conection()
            sql="""SELECT id, dc_correo_electronico, dc_contrasena, dc_nombre FROM tb_usuario
                        WHERE dc_correo_electronico = '{}'""".format(user.dc_correo_electronico)
            cursor.execute(sql)
            row=cursor.fetchone()
            if row != None:
                user=User(row[0],row[1],User.check_password(row[2], user.password), row[3])
                return user
            else:
                return None
        except Exception as ex:
            raise Exception(ex)
from .entities.Usersmodel import User
from ..database.mysql_conection import get_conection

class ModelUser():
    
    @classmethod
    def login(self, user):
        try:
            cursor = get_conection.connection.cursor()
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
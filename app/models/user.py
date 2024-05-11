from .entities.Usersmodel import User
from ..database.mysql_conection import get_conection

class ModelUser():
    
    @classmethod
    def get_users(self):
        try:
            conection = get_conection()
            users = []
            with conection.cursor() as cursor:
                cursor.execute("SELECT id, dc_nombre, dc_contrasena, dc_correo_electronico, dc_telefono, df_fecha_solicitud FROM tb_usuario")
                resultset=cursor.fetchall()
                
                for row in resultset:
                    user = {
                        'id': row[0],
                        'dc_contrasena': row[1],
                        'dc_correo_electronico': row[2],
                        'dc_nombre': row[3],
                        'dc_telefono': row[4],
                        'df_fecha_solicitud': row[5]
                    }
                    users.append(user)
                    
            conection.close()
            return users
        except Exception as ex:
            raise Exception(ex)
    
    @classmethod
    def get_user_by_id(cls, user_id):
        try:
            connection = get_conection()
            with connection.cursor() as cursor:
                cursor.execute("SELECT dc_contrasena, dc_correo_electronico, dc_nombre, dc_telefono, df_fecha_solicitud FROM tb_usuario WHERE id = %s", (user_id,))
                result = cursor.fetchone()
                if result:
                    user = {
                        'dc_contrasena': result[0],
                        'dc_correo_electronico': result[1],
                        'dc_nombre': result[2],
                        'dc_telefono': result[3],
                        'df_fecha_solicitud': result[4]
                    }
                else:
                    user = None
            connection.close()
            return user
        except Exception as ex:
            raise Exception(ex)
        
    @classmethod
    def login(self, user):
        try:
            conn = get_conection()
            
            with conn.cursor() as cursor:
                sql = """SELECT id, dc_correo_electronico, dc_contrasena, dc_nombre FROM tb_usuario 
                WHERE dc_contrasena = %s AND dc_correo_electronico = %s"""
                cursor.execute(sql, (user.dc_contrasena, user.dc_correo_electronico))
                row=cursor.fetchone()
                if row != None:
                    user=User(row[0],row[1],User.check_password(row[2], user.password), row[3])
                    return user
                else:
                    return None
        except Exception as ex:
            print(f'que wea pasó {ex}')
            raise Exception(ex)
        
    @classmethod
    def signup(self, user):
        try:
            conn = get_conection()
            
            with conn.cursor() as cursor:
                sql="""INSERT INTO tb_usuario (dc_nombre, dc_contrasena, dc_correo_electronico, dc_telefono, tb_nivel_artes_marciales_id, df_fecha_solicitud, tb_tipo_usuario_id, tb_usuario_estado_id, tb_nivel_id, tb_contacto_emergencia_id)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                values = (user.dc_nombre, user.dc_contrasena, user.dc_correo_electronico, user.dc_telefono, user.tb_nivel_artes_marciales_id, user.df_fecha_solicitud, user.tb_tipo_usuario_id, user.tb_usuario_estado_id, user.tb_nivel_id, user.tb_contacto_emergencia_id)
                cursor.execute(sql, values)
                affected_rows = cursor.rowcount
                conn.commit()
            conn.close()
            print(affected_rows)
            return affected_rows
        except Exception as ex:
            print(f'que wea pasó {ex}')
            raise Exception(ex)
    
    @classmethod
    def delete_user(cls, user_id):
        try:
            conn = get_conection()
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM tb_usuario WHERE id = %s", (user_id,))
                affected_rows = cursor.rowcount
                conn.commit()
            return affected_rows
        except Exception as ex:
            print(f'Error: {ex}')
            raise Exception(ex)
        finally:
            conn.close()

    @classmethod
    def update_user(cls, user_id, new_user_data):
        try:
            conn = get_conection()
            with conn.cursor() as cursor:
                sql = """UPDATE tb_usuario SET dc_nombre = %s, dc_contrasena = %s, dc_correo_electronico = %s, dc_telefono = %s, df_fecha_solicitud = %s WHERE id = %s"""
                values = (new_user_data['dc_nombre'], new_user_data['dc_contrasena'], new_user_data['dc_correo_electronico'], new_user_data['dc_telefono'], new_user_data['df_fecha_solicitud'], user_id)
                cursor.execute(sql, values)
                affected_rows = cursor.rowcount
                conn.commit()
            return affected_rows
        except Exception as ex:
            print(f'Error: {ex}')
            raise Exception(ex)
        finally:
            conn.close()
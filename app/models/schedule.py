from .entities.Usersmodel import User
from ..database.mysql_conection import get_conection
import timedelta

class ScheduleModel():
    
    @classmethod
    def get_schedule(self):
        try:
            conection = get_conection()
            schedule = []
            with conection.cursor() as cursor:
                cursor.execute("SELECT id, nb_clase_id, tb_gimnasio_id, df_fecha, df_hora, tb_calificacion_id FROM tb_solicitud_reserva")
                resultset=cursor.fetchall()
                
                for row in resultset:
                    user = {
                        'id': row[0],
                        'nb_clase_id': row[1],
                        'tb_gimnasio_id': row[2],
                        'df_fecha': row[3],
                        'df_hora': row[4].strftime('%H:%M:%S'),
                        'tb_calificacion_id': row[5]
                    }
                    schedule.append(user)
                    
            conection.close()
            return schedule
        except Exception as ex:
            raise Exception(ex)
        
    @classmethod
    def get_schedule_by_id(cls, schedule_id):
        try:
            connection = get_conection()
            with connection.cursor() as cursor:
                cursor.execute("SELECT id, nb_clase_id, tb_gimnasio_id, df_fecha, df_hora, tb_calificacion_id FROM tb_solicitud_reserva WHERE id = %s", (schedule_id,))
                result = cursor.fetchone()
                if result:
                    user = {
                        'id': result[0],
                        'nb_clase_id': result[1],
                        'tb_gimnasio_id': result[2],
                        'df_fecha': result[3],
                        'df_hora': result[4].strftime('%H:%M:%S'),
                        'tb_calificacion_id': result[5]
                    }
                else:
                    user = None
            connection.close()
            return user
        except Exception as ex:
            raise Exception(ex)
        
    @classmethod
    def add_schedule(self, schedule):
        try:
            conn = get_conection()
            
            with conn.cursor() as cursor:
                sql="""INSERT INTO tb_solicitud_reserva (id, nb_clase_id, tb_gimnasio_id, df_fecha, df_hora, tb_calificacion_id)
                        VALUES (%s, %s, %s, %s, %s, %s)"""
                values = (schedule.id, schedule.nb_clase_id, schedule.tb_gimnasio_id, schedule.df_fecha, schedule.df_hora, schedule.tb_calificacion_id)
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
    def delete_schedule(cls, schedule_id):
        try:
            conn = get_conection()
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM tb_solicitud_reserva WHERE id = %s", (schedule_id,))
                affected_rows = cursor.rowcount
                conn.commit()
            return affected_rows
        except Exception as ex:
            print(f'Error: {ex}')
            raise Exception(ex)
        finally:
            conn.close()

    @classmethod
    def update_schedule(cls, schedule_id, new_schedule_data):
        try:
            conn = get_conection()
            with conn.cursor() as cursor:
                sql = """UPDATE tb_solicitud_reserva SET df_fecha = %s, df_hora = %s WHERE id = %s"""
                values = (new_schedule_data['dc_nombre'], new_schedule_data['dc_contrasena'], schedule_id)
                cursor.execute(sql, values)
                affected_rows = cursor.rowcount
                conn.commit()
            return affected_rows
        except Exception as ex:
            print(f'Error: {ex}')
            raise Exception(ex)
        finally:
            conn.close()
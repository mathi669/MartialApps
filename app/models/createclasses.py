from ..database.mysql_conection import get_conection
from .entities.CreateClass import CreateNewClass

class CreateMartialClass():
    
    @classmethod
    def get_classes():
        try:
            conection = get_conection()
            createclas = []
            with conection.cursor() as cursor:
                cursor.execute("SELECT * FROM tb_clase")
                resultset = cursor.fetchall()
                
                for row in resultset:
                    classes = {
                        'dc_horario': row[0],
                        'nb_cupos_disponibles': row[1],
                        'id_categoria': row[2],
                        'df_fecha': row[3],
                        'df_hora': row[4],
                        'tb_clase_estado_id': row[5],
                        'tb_gimnasio_id': row[6],
                        'tb_profesor_id': row[7],
                        'dc_nombre_clase': row[8],
                        'dc_imagen_url': row[9]
                    }
                    createclas.append(classes)
            conection.close()
            return classes
        except Exception as ex:
            raise Exception(ex)

    @classmethod
    def get_class(id, clas_id):
        try:
            connection = get_conection()
            with connection.cursor() as cursor:
                cursor.execute("""SELECT 
                               id, 
                               dc_horario, 
                               nb_cupos_disponibles, 
                               id_categoria, 
                               df_fecha, 
                               df_hora, 
                               tb_clase_estado_id, 
                               tb_gimnasio_id, 
                               tb_arte_marcial_id, 
                               tb_profesor_id, 
                               dc_nombre_clase, 
                               dc_imagen_url 
                            FROM tb_clase WHERE id = %s""", (clas_id))
                result = cursor.fetchone()

                if result:
                    clases = {
                        'id': result[0],
                        'dc_horario':result[1],
                        'nb_cupos_disponibles':result[2],
                        'id_categoria':result[3],
                        'df_fecha':result[4],
                        'df_hora':result[5],
                        'tb_clase_estado_id':result[6],
                        'tb_gimnasio_id':result[7],
                        'tb_arte_marcial_id':result[8],
                        'tb_profesor_id':result[9],
                        'dc_nombre_clase':result[10],
                        'dc_imagen_url':result[11]
                    }
                else:
                    clases = None
            connection.close()
            return clases
        except Exception as ex:
            raise Exception(ex)

    @classmethod
    def add_class(self, clases):
        try:
            connection = get_conection()
            with connection.cursor() as cursor:
                sql="""
                    INSERT INTO tb_clase (dc_horario, nb_cupos_disponibles, id_categoria, df_fecha, df_hora, tb_clase_estado_id, tb_gimnasio_id, tb_arte_marcial_id, tb_profesor_id, dc_nombre_clase, dc_imagen_url)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                values = ()
                cursor.execute(sql)
                mysql.connection.commit()
                cursor.close()
                return jsonify({'message': 'Class added successfully'}), 201
        except Exception as e:
            return jsonify({'message': str(e)}), 500

    @classmethod
    def update_class(id):
        try:
            data = request.json
            cursor = mysql.connection.cursor()
            cursor.execute("""
                UPDATE tb_clase
                SET dc_horario = %s, nb_cupos_disponibles = %s, id_categoria = %s, df_fecha = %s, df_hora = %s, tb_clase_estado_id = %s, tb_gimnasio_id = %s, tb_arte_marcial_id = %s, tb_profesor_id = %s, dc_nombre_clase = %s, dc_imagen_url = %s
                WHERE id = %s
            """, (
                data['dc_horario'],
                data['nb_cupos_disponibles'],
                data['id_categoria'],
                data['df_fecha'],
                data['df_hora'],
                data['tb_clase_estado_id'],
                data['tb_gimnasio_id'],
                data['tb_arte_marcial_id'],
                data['tb_profesor_id'],
                data['dc_nombre_clase'],
                data['dc_imagen_url'],
                id
            ))
            mysql.connection.commit()
            cursor.close()
            return jsonify({'message': 'Class updated successfully'}), 200
        except Exception as e:
            return jsonify({'message': str(e)}), 500

    @classmethod
    def delete_class(id):
        try:
            cursor = mysql.connection.cursor()
            cursor.execute("DELETE FROM tb_clase WHERE id = %s", (id,))
            mysql.connection.commit()
            cursor.close()
            return jsonify({'message': 'Class deleted successfully'}), 200
        except Exception as e:
            return jsonify({'message': str(e)}), 500
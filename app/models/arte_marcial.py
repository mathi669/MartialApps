from src.database.mysql_conection import get_connect # type: ignore

class model_martial_art:

    @classmethod
    def get_martial_art(cls):
        connection=get_connect()
        with connection.cursor() as cursor:
            SQL='SELECT id, dc_arte_marcial from tb_arte_marcial'
            cursor.excecute(SQL)
            martial_list=cursor.fetchall()
        connection.close()
        return martial_list
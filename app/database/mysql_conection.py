from decouple import config
import pymysql


def get_conection():
    try:
        conn = pymysql.connect(
            host=config('MYSQL_HOST'),
            user=config('MYSQL_USER'),
            password=config('MYSQL_PASSWORD'),
            port=config('PORT_DB', cast=int, default=3306),
            db=config('MYSQL_DB')
        )
        return conn
    except Exception as ex:
        print(f"Error al conectar a la base de datos: {ex}")
        return None
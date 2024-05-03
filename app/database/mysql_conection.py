from decouple import config
import pymysql


def get_conection():
    try:
        return pymysql.connect(
            host=config('MYSQL_HOST'),
            user=config('MYSQL_USER'),
            password=config('MYSQL_PASSWORD'),
            port=config('PORT', cast=int, default=3306),
            db=config('MYSQL_DB')
        )
    except Exception as ex:
        print(ex)
from decouple import config
import pymysql

print(config('MYSQL_HOST'))

def get_connect():
    try:
        return pymysql.connect(
            host=config('MYSQL_HOST'),
            user=config('MYSQL_USER'),
            password=config('MYSQL_PASSWORD'),
            db=config('MYSQL_DB')
        )
    except Exception as ex:
        print(ex)
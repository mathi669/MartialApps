from decouple import config as env_config

class Config:
    SECRET_KEY = env_config('SECRET_KEY')
    MYSQL_HOST = env_config('MYSQL_HOST')
    MYSQL_USER = env_config('MYSQL_USER')
    MYSQL_PASSWORD = env_config('MYSQL_PASSWORD')
    MYSQL_DB = env_config('MYSQL_DB')
    PORT_DB = env_config('PORT_DB')
    JWT_SECRET_KEY = env_config('JWT_SECRET_KEY')
    JWT_KEY = env_config('JWT_KEY')
    IMG_BB_KEY = env_config('IMG_BB_KEY')
    MAIL_USERNAME = env_config('MAIL_USERNAME')
    MAIL_PASSWORD = env_config('MAIL_PASSWORD')
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

class DevelopmentConfig(Config):
    DEBUG = True

config = {
    'development': DevelopmentConfig,
    'default': DevelopmentConfig
}

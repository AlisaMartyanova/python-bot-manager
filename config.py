from os import environ


class Config:

    # configure database postgres
    USER = environ.get('USER')
    PASSWORD = environ.get('PASSWORD')
    HOST = environ.get('HOST')
    DB_PORT = environ.get('DB_PORT')
    DB_NAME = environ.get('DB_NAME')
    SQLALCHEMY_DATABASE_URI = 'postgresql://{}:{}@{}:{}/{}'.format(
        USER, PASSWORD, HOST, DB_PORT, DB_NAME)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # secrets
    SECRET_KEY = environ.get('SECRET')

    # jwt
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']

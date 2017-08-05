import os

class BaseConfig(object):
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = '\xc5\xf5\xaf\x11U9\x01\xdd\xcc\xee\xe6\xba1\x0c)\x9b\xfe^\xbc\x9f\x87\xd1\x99B'


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class ProductionConfig(BaseConfig):
    DEBUG = False
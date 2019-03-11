#coding=utf-8
import os

basedir = os.path.abspath(os.path.dirname(__file__))
nginx_path = '/etc/nginx'

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or '1'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root@127.0.0.1/easy_nginx?charset=utf8'

    #SQLALCHEMY_TRACK_MODIFICATIONS = True
    @staticmethod
    def init_app(app):
        pass

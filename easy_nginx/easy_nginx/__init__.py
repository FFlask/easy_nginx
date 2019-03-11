from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from flask_login import LoginManager

db = SQLAlchemy()

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'

from models import *

def create_app():
    app = Flask(__name__,static_url_path='',root_path='/app/easy_nginx/easy_nginx')
    app.config.from_object(Config)
    Config.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    from auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)
    from main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    from secure import secure as secure_blueprint
    app.register_blueprint(secure_blueprint)
    return app
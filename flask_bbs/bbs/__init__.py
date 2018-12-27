from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from flask_login import LoginManager

db = SQLAlchemy()

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'bbs1.login'

from models import *

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    Config.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    from bbs1 import bbs1 as bb1_blueprint
    app.register_blueprint(bb1_blueprint)
    from bbs_admin import bbs_admin as bbs_admin_blueprint
    app.register_blueprint(bbs_admin_blueprint)
    return app
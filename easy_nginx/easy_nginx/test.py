from . import db,create_app
from models import *
from functools import wraps
app = create_app()

with app.app_context():
    pass


from flask import Blueprint

bbs_admin = Blueprint('bbs_admin',__name__)
from . import views
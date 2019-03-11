from flask import Blueprint

secure = Blueprint('secure',__name__)
from . import views
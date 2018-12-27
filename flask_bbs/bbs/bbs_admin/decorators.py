#coding=utf-8
from ..models import Permissions,User
from functools import wraps
from flask import abort
from flask_login import current_user

def permission_required(permission):
    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return func(*args, **kwargs)
        return decorated_function
    return decorator

def is_manager(func):
    return permission_required(Permissions.Manager)(func)

def is_admin(func):
    return permission_required(Permissions.Admin)(func)

